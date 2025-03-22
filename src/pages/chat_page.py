import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from src.constants import COLORS
from src.ui.modern_ui import ModernUI
from datetime import datetime

class ChatPage:
    def __init__(self, parent, get_contacts_callback, get_messages_callback, send_message_callback, show_frame_callback):
        self.parent = parent
        self.get_contacts = get_contacts_callback
        self.get_messages = get_messages_callback
        self.send_message = send_message_callback
        self.show_frame = show_frame_callback
        
        self.current_user = None
        self.frame = None
        self.contacts_tree = None
        self.chat_area = None
        self.message_entry = None
        self.selected_contact = None
        self.messages = {}  # {contact_id: [(timestamp, sender_name, message)]}
        
        # Create the frame
        self.create_frame()
        
        # Optional: set up chat client callbacks if needed
        # self.chat_client.set_message_callback(self.on_message_received)
        # self.chat_client.set_error_callback(self.on_chat_error)
        
    def create_frame(self):
        """Create the chat page frame"""
        self.frame = ModernUI.create_card(self.parent)
        
        # Create main container with padding
        main_frame = ttk.Frame(self.frame, style='Card.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="💬 Messages",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # Create split view for contacts and chat
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill='both', expand=True)
        
        # Left side - Contacts list
        contacts_frame = ttk.Frame(paned_window, style='Card.TFrame')
        paned_window.add(contacts_frame, weight=1)
        
        # Contacts title
        ttk.Label(
            contacts_frame,
            text="Contacts",
            style='Subtitle.TLabel'
        ).pack(pady=(0, 10))
        
        # Create Treeview for contacts
        self.contacts_tree = ttk.Treeview(
            contacts_frame,
            columns=('name',),
            show='headings',
            style='Treeview',
            height=20
        )
        self.contacts_tree.heading('name', text='Name')
        self.contacts_tree.column('name', width=200)
        
        # Add scrollbar to contacts
        contacts_scroll = ttk.Scrollbar(contacts_frame, orient='vertical', command=self.contacts_tree.yview)
        self.contacts_tree.configure(yscrollcommand=contacts_scroll.set)
        
        # Pack contacts list and scrollbar
        self.contacts_tree.pack(side='left', fill='both', expand=True)
        contacts_scroll.pack(side='right', fill='y')
        
        # Bind contact selection
        self.contacts_tree.bind('<<TreeviewSelect>>', self.on_contact_select)
        
        # Right side - Chat area
        chat_frame = ttk.Frame(paned_window, style='Card.TFrame')
        paned_window.add(chat_frame, weight=2)
        
        # Chat header
        self.chat_header = ttk.Label(
            chat_frame,
            text="Select a contact to start chatting",
            style='Subtitle.TLabel'
        )
        self.chat_header.pack(fill='x', pady=(0, 10))
        
        # Chat messages area
        self.chat_area = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            height=20,
            font=('Segoe UI', 10),
            bg='white',
            fg=COLORS['text']
        )
        self.chat_area.pack(fill='both', expand=True, pady=(0, 10))
        self.chat_area.configure(state='disabled')
        
        # Message input area
        input_frame = ttk.Frame(chat_frame, style='Card.TFrame')
        input_frame.pack(fill='x')
        
        self.message_entry = ModernUI.create_entry(
            input_frame,
            placeholder="Type your message..."
        )
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        
        ModernUI.create_button(
            input_frame,
            "Send",
            lambda: self.send_message(None)
        ).pack(side='right')
        
        # Load contacts
        self.refresh_contacts()
        
    def refresh_contacts(self):
        """Refresh the contacts list"""
        # Clear existing contacts
        for item in self.contacts_tree.get_children():
            self.contacts_tree.delete(item)
            
        # Add contacts
        contacts = self.get_contacts()
        for contact in contacts:
            self.contacts_tree.insert(
                '',
                'end',
                values=(contact['full_name'],),
                tags=(str(contact['unique_id']),)
            )
            
    def on_contact_select(self, event):
        """Handle contact selection"""
        selection = self.contacts_tree.selection()
        if not selection:
            return
            
        contact_id = self.contacts_tree.item(selection[0])['tags'][0]
        contact_name = self.contacts_tree.item(selection[0])['values'][0]
        
        self.selected_contact = {
            'id': contact_id,
            'name': contact_name
        }
        
        # Update chat header
        self.chat_header.configure(text=f"Chat with {contact_name}")
        
        # Clear and load messages
        self.chat_area.configure(state='normal')
        self.chat_area.delete('1.0', tk.END)
        
        if contact_id in self.messages:
            for timestamp, sender_name, message in self.messages[contact_id]:
                self.add_message_to_chat(timestamp, sender_name, message)
                
        self.chat_area.configure(state='disabled')
        self.chat_area.see(tk.END)
        
    def send_message(self, event):
        """Send a message to the selected contact"""
        if not self.selected_contact:
            messagebox.showwarning("No Contact", "Please select a contact to send a message to")
            return
            
        message = self.message_entry.get().strip()
        if not message:
            return
            
        success = self.send_message(self.selected_contact['id'], message)
        
        if success:
            # Add message to local chat
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.add_message(
                self.selected_contact['id'],
                timestamp,
                self.current_user['full_name'],
                message
            )
            
            # Clear message input
            self.message_entry.delete(0, tk.END)
        
    def on_message_received(self, message):
        """Handle received chat message"""
        sender_id = message['sender_id']
        sender_name = message['sender_name']
        content = message['content']
        timestamp = message['timestamp']
        
        self.add_message(sender_id, timestamp, sender_name, content)
        
    def add_message(self, contact_id, timestamp, sender_name, content):
        """Add a message to the chat history"""
        # Initialize messages list for contact if needed
        if contact_id not in self.messages:
            self.messages[contact_id] = []
            
        # Add message to history
        self.messages[contact_id].append((timestamp, sender_name, content))
        
        # If this contact is currently selected, show the message
        if self.selected_contact and self.selected_contact['id'] == contact_id:
            self.chat_area.configure(state='normal')
            self.add_message_to_chat(timestamp, sender_name, content)
            self.chat_area.configure(state='disabled')
            self.chat_area.see(tk.END)
            
    def add_message_to_chat(self, timestamp, sender_name, content):
        """Add a message to the chat display"""
        self.chat_area.insert(tk.END, f"[{timestamp}] {sender_name}:\n")
        self.chat_area.insert(tk.END, f"{content}\n\n")
        
    def on_chat_error(self, error_message):
        """Handle chat client errors"""
        messagebox.showerror("Chat Error", error_message)