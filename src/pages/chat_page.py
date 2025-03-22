import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime

class ChatPage:
    def __init__(self, parent, get_contacts_callback, get_messages_callback, send_message_callback, show_frame_callback):
        self.frame = ttk.Frame(parent)
        self.get_contacts = get_contacts_callback
        self.get_messages = get_messages_callback
        self.send_message = send_message_callback
        self.show_frame = show_frame_callback
        
        # Initialize selected chat user
        self.selected_chat_user = None
        
        # Create chat interface
        self.create_widgets()
        
    def create_widgets(self):
        # Main container with two panes
        paned_window = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left pane - Contacts list
        contacts_frame = ttk.Frame(paned_window)
        paned_window.add(contacts_frame, weight=1)
        
        # Contacts header
        ttk.Label(contacts_frame, text="Contacts", font=('Segoe UI', 14, 'bold')).pack(fill='x', pady=(0, 10))
        
        # Contacts list
        self.contacts_listbox = tk.Listbox(contacts_frame, font=('Segoe UI', 11))
        self.contacts_listbox.pack(fill='both', expand=True)
        self.contacts_listbox.bind('<<ListboxSelect>>', self.on_contact_selected)
        
        # Right pane - Chat area
        chat_frame = ttk.Frame(paned_window)
        paned_window.add(chat_frame, weight=3)
        
        # Chat header
        self.chat_header = ttk.Label(chat_frame, text="Select a contact to start chatting", font=('Segoe UI', 14, 'bold'))
        self.chat_header.pack(fill='x', pady=(0, 10))
        
        # Messages area
        self.messages_area = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, font=('Segoe UI', 10), state='disabled')
        self.messages_area.pack(fill='both', expand=True, pady=(0, 10))
        
        # Message input area
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill='x')
        
        self.message_entry = ttk.Entry(input_frame, font=('Segoe UI', 11))
        self.message_entry.pack(side='left', fill='x', expand=True)
        self.message_entry.bind('<Return>', self.on_send_message)
        
        send_button = ttk.Button(input_frame, text="Send", command=self.on_send_message)
        send_button.pack(side='right', padx=(10, 0))
        
        # Load contacts
        self.load_contacts()
    
    def load_contacts(self):
        # Clear existing contacts
        self.contacts_listbox.delete(0, tk.END)
        
        # Get contacts from database
        contacts = self.get_contacts()
        
        # Add contacts to listbox
        for contact in contacts:
            self.contacts_listbox.insert(tk.END, contact['username'])
            # Store the contact data in the listbox
            self.contacts_listbox.itemconfig(tk.END, {'contact_data': contact})
    
    def on_contact_selected(self, event):
        # Get selected index
        selection = self.contacts_listbox.curselection()
        if not selection:
            return
            
        # Get contact data
        index = selection[0]
        contact_data = self.contacts_listbox.itemcget(index, 'contact_data')
        
        # Set selected chat user
        self.selected_chat_user = contact_data
        
        # Update chat header
        self.chat_header.config(text=f"Chat with {contact_data['username']}")
        
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
    
    def on_send_message(self, event=None):
        if not self.selected_chat_user:
            messagebox.showinfo("Info", "Please select a contact first")
            return
            
        # Get message content
        content = self.message_entry.get().strip()
        if not content:
            return
            
        # Send message
        success, message = self.send_message(
            self.selected_chat_user['unique_id'],
            content
        )
        
        if success:
            # Clear message entry
            self.message_entry.delete(0, tk.END)
            
            # Update chat messages
            self.update_chat_messages()
        else:
            messagebox.showerror("Error", message)