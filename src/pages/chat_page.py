import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from src.ui.modern_ui import ModernUI

class ChatPage:
    def __init__(self, parent, get_contacts_callback, get_messages_callback, send_message_callback, show_frame_callback):
        self.parent = parent
        self.get_contacts = get_contacts_callback
        self.get_messages = get_messages_callback
        self.send_message = send_message_callback
        self.show_frame = show_frame_callback
        self.frame = None
        self.selected_chat_user = None
        self.create_frame()
        
    def create_frame(self):
        self.frame = ModernUI.create_card(self.parent)
        
        # Main container with two panes
        paned_window = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for contacts
        contacts_frame = ttk.Frame(paned_window, style='Card.TFrame')
        paned_window.add(contacts_frame, weight=1)
        
        # Contacts header
        ttk.Label(contacts_frame, text="Contacts", font=('Poppins', 16, 'bold')).pack(pady=10)
        
        # Contacts list
        self.contacts_list = ttk.Treeview(contacts_frame, selectmode='browse', show='tree')
        self.contacts_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.contacts_list.bind('<<TreeviewSelect>>', self.on_contact_select)
        
        # Right panel for chat
        chat_frame = ttk.Frame(paned_window, style='Card.TFrame')
        paned_window.add(chat_frame, weight=2)
        
        # Chat header
        self.chat_header = ttk.Label(chat_frame, text="Select a contact", font=('Poppins', 16, 'bold'))
        self.chat_header.pack(pady=10)
        
        # Chat messages area
        self.messages_area = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=('Poppins', 10),
            height=20,
            state='disabled'
        )
        self.messages_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Message input area
        input_frame = ttk.Frame(chat_frame, style='Card.TFrame')
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.message_input = ModernUI.create_entry(input_frame, placeholder="Type your message...")
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        send_button = ModernUI.create_button(input_frame, "Send", self.send_message_handler)
        send_button.pack(side=tk.RIGHT)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self.frame, style='Card.TFrame')
        nav_frame.pack(fill=tk.X, padx=10, pady=5)
        
        back_button = ModernUI.create_button(
            nav_frame,
            "Back to Dashboard",
            lambda: self.show_frame('dashboard'),
            style='Secondary.TButton'
        )
        back_button.pack(side=tk.LEFT)
        
        # Load contacts
        self.load_contacts()
    
    def load_contacts(self):
        # Clear existing contacts
        for item in self.contacts_list.get_children():
            self.contacts_list.delete(item)
        
        # Get contacts from database
        contacts = self.get_contacts()
        
        # Add contacts to listbox
        for contact in contacts:
            self.contacts_list.insert('', 'end', text=contact['username'], values=(contact['unique_id'],))
    
    def on_contact_select(self, event):
        # Get selected index
        selection = self.contacts_list.selection()
        if not selection:
            return
            
        # Get contact data
        contact_data = self.contacts_list.item(selection[0], 'values')
        
        # Set selected chat user
        self.selected_chat_user = {'unique_id': contact_data[0]}
        
        # Update chat header
        self.chat_header.config(text=f"Chat with {self.contacts_list.item(selection[0], 'text')}")
        
        # Load messages
        self.update_chat_messages()
    
    def update_chat_messages(self):
        if not self.selected_chat_user:
            return
            
        # Clear messages area
        self.messages_area.config(state='normal')
        self.messages_area.delete(1.0, tk.END)
        
        # Get messages
        messages = self.get_messages(self.selected_chat_user['unique_id'])
        
        # Display messages
        for message in messages:
            # Format timestamp
            timestamp = message['created_at']
            if isinstance(timestamp, str):
                # Parse string timestamp if needed
                try:
                    timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    formatted_time = timestamp.strftime('%I:%M %p')
                except ValueError:
                    formatted_time = timestamp  # Use as is if parsing fails
            else:
                # Format datetime object
                formatted_time = timestamp.strftime('%I:%M %p')
            
            # Format message
            sender_name = message['sender_name']
            content = message['content']
            
            # Add message to text area
            self.messages_area.insert(tk.END, f"{sender_name} ({formatted_time}):\n")
            self.messages_area.insert(tk.END, f"{content}\n\n")
        
        # Disable editing
        self.messages_area.config(state='disabled')
        
        # Scroll to bottom
        self.messages_area.see(tk.END)
    
    def send_message_handler(self):
        if not self.selected_chat_user:
            messagebox.showinfo("Info", "Please select a contact first")
            return
            
        # Get message content
        content = self.message_input.get().strip()
        if not content:
            return
            
        # Send message
        success, message = self.send_message(
            self.selected_chat_user['unique_id'],
            content
        )
        
        if success:
            # Clear message entry
            self.message_input.delete(0, tk.END)
            
            # Update chat messages
            self.update_chat_messages()
        else:
            messagebox.showerror("Error", message)