import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.modern_ui import ModernUI
from src.utils.email_validator import EmailValidator
from src.constants import COLORS, CATEGORIES, LOCATIONS, STATES
from src.database.database_handler import DatabaseHandler

class RequestListPage:
    def __init__(self, parent, user_info, show_frame_callback):
        """Initialize the request list page"""
        self.parent = parent
        self.user_info = user_info
        self.show_frame = show_frame_callback
        self.db = DatabaseHandler()
        
        # Create frame
        self.frame = ModernUI.create_card(parent)
        self.frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(
            self.frame,
            text="Resource Requests",
            style='Title.TLabel'
        ).pack(pady=(0, 20))
        
        # Search frame
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        # Search entry
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', padx=5)
        
        # Category dropdown
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(search_frame, textvariable=self.category_var, values=list(CATEGORIES))
        category_combo.pack(side='left', padx=5)
        
        # Location dropdown
        self.location_var = tk.StringVar()
        location_combo = ttk.Combobox(search_frame, textvariable=self.location_var, values=list(LOCATIONS))
        location_combo.pack(side='left', padx=5)
        
        # Search button
        search_btn = ModernUI.create_button(
            search_frame,
            "Search",
            self.search_requests,
            style='Primary.TButton'
        )
        search_btn.pack(side='left', padx=5)
        
        # Create Treeview for requests
        columns = ('title', 'category', 'location', 'requester', 'status', 'email')
        self.requests_tree = ttk.Treeview(self.frame, columns=columns, show='headings', style='Treeview')
        
        # Define column headings
        self.requests_tree.heading('title', text='Title')
        self.requests_tree.heading('category', text='Category')
        self.requests_tree.heading('location', text='Location')
        self.requests_tree.heading('requester', text='Requester')
        self.requests_tree.heading('status', text='Status')
        self.requests_tree.heading('email', text='Contact Email')
        
        # Define column widths
        self.requests_tree.column('title', width=200)
        self.requests_tree.column('category', width=100)
        self.requests_tree.column('location', width=150)
        self.requests_tree.column('requester', width=150)
        self.requests_tree.column('status', width=100)
        self.requests_tree.column('email', width=150)
        
        # Add scrollbar to treeview
        tree_scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.requests_tree.yview)
        self.requests_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.requests_tree.pack(side='top', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        
        # Action frame
        action_frame = ttk.Frame(self.frame, style='Card.TFrame')
        action_frame.pack(fill='x', pady=10)
        
        # Back to dashboard button
        ModernUI.create_button(
            action_frame,
            "Back to Dashboard",
            lambda: self.show_frame('dashboard'),
            style='Secondary.TButton'
        ).pack(side='right', padx=5)
        
        # View details button
        ModernUI.create_button(
            action_frame,
            "View Details",
            self.view_request_details,
            style='Primary.TButton'
        ).pack(side='left', padx=5)
        
        # Send email button
        ModernUI.create_button(
            action_frame,
            "Contact Requester",
            self.send_email_dialog,
            style='Primary.TButton'
        ).pack(side='left', padx=5)
        
        # Delete button (only visible to request owner)
        self.delete_btn = ModernUI.create_button(
            action_frame,
            "Delete Request",
            self.delete_request,
            style='Danger.TButton'
        )
        self.delete_btn.pack(side='left', padx=5)
        self.delete_btn.pack_forget()  # Initially hidden
        
        # Load initial requests
        self.refresh_requests()
    
    def search_requests(self):
        """Search requests based on criteria"""
        search_query = self.search_var.get()
        category = self.category_var.get() or None
        location = self.location_var.get() or None
        
        requests = self.db.search_requests(search_query, category, location)
        self.refresh_requests(requests)
    
    def refresh_requests(self, requests=None):
        """Populate the treeview with requests"""
        # Clear existing items
        for item in self.requests_tree.get_children():
            self.requests_tree.delete(item)
        
        if requests is None:
            requests = self.db.search_requests()
        
        # Add requests to treeview
        for request in requests:
            item_id = self.requests_tree.insert('', 'end', values=(
                request['title'],
                request['category'],
                f"{request['city']}, {request['state']}",
                request['requester_name'],
                request['status'],
                request['requester_email']
            ))
            # Store request ID in the item
            self.requests_tree.set(item_id, 'unique_id', request['unique_id'])
            
            # Show delete button if user is the requester
            selected_items = self.requests_tree.selection()
            if selected_items:
                request_id = self.requests_tree.set(selected_items[0], 'unique_id')
                if request.get('requester_id') == self.user_info['unique_id']:
                    self.delete_btn.pack(side='left', padx=5)
                else:
                    self.delete_btn.pack_forget()
    
    def view_request_details(self):
        """Display detailed information about the selected request"""
        selected_items = self.requests_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a request to view")
            return
        
        request_id = self.requests_tree.set(selected_items[0], 'unique_id')
        request = self.db.get_request_details(request_id)
        
        if not request:
            messagebox.showerror("Error", "Could not fetch request details")
            return
        
        # Create details window
        details_window = tk.Toplevel(self.frame)
        details_window.title("Request Details")
        details_window.geometry("500x400")
        
        # Add details to window
        content_frame = ttk.Frame(details_window, padding=20)
        content_frame.pack(fill='both', expand=True)
        
        ttk.Label(content_frame, text=request['title'], style='Title.TLabel').pack(pady=(0, 10))
        ttk.Label(content_frame, text=f"Category: {request['category']}").pack(anchor='w')
        ttk.Label(content_frame, text=f"Location: {request['city']}, {request['state']}").pack(anchor='w')
        ttk.Label(content_frame, text=f"Requester: {request['requester_name']}").pack(anchor='w')
        ttk.Label(content_frame, text=f"Status: {request['status']}").pack(anchor='w')
        ttk.Label(content_frame, text=f"Contact: {request['requester_email']}").pack(anchor='w')
        
        description_frame = ttk.LabelFrame(content_frame, text="Description", padding=10)
        description_frame.pack(fill='both', expand=True, pady=10)
        
        description_text = tk.Text(description_frame, wrap='word', height=5, width=40)
        description_text.insert('1.0', request['description'])
        description_text.configure(state='disabled')
        description_text.pack(fill='both', expand=True)
    
    def delete_request(self):
        """Delete the selected request"""
        selected_items = self.requests_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a request to delete")
            return
        
        request_id = self.requests_tree.set(selected_items[0], 'unique_id')
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this request?"):
            return
        
        # Delete request
        if self.db.delete_request(request_id, self.user_info['unique_id']):
            messagebox.showinfo("Success", "Request deleted successfully")
            self.refresh_requests()
        else:
            messagebox.showerror("Error", "Failed to delete request")
    
    def send_email_dialog(self):
        """Open dialog to send email"""
        # Get selected item
        selected_item = self.requests_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a request to contact")
            return
        
        # Get email from selected row
        values = self.requests_tree.item(selected_item[0])['values']
        recipient_email = values[5]
        
        # Create email dialog
        email_window = tk.Toplevel(self.frame)
        email_window.title("Send Email")
        email_window.geometry("400x300")
        
        # Subject
        ttk.Label(email_window, text="Subject:").pack(pady=(10,0))
        subject_entry = ttk.Entry(email_window, width=50)
        subject_entry.pack(pady=(0,10))
        
        # Message body
        ttk.Label(email_window, text="Message:").pack(pady=(10,0))
        message_text = tk.Text(email_window, height=10, width=50)
        message_text.pack(pady=(0,10))
        
        # Send button
        def send_email():
            subject = subject_entry.get()
            message = message_text.get("1.0", tk.END).strip()
            
            if not subject or not message:
                messagebox.showerror("Error", "Subject and message cannot be empty")
                return
            
            try:
                # Send email using EmailValidator
                EmailValidator.send_email(
                    recipient_email, 
                    subject, 
                    message
                )
                messagebox.showinfo("Success", "Email sent successfully!")
                email_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send email: {str(e)}")
        
        send_button = ModernUI.create_button(
            email_window,
            "Send Email",
            send_email,
            style='Primary.TButton'
        )
        send_button.pack(pady=10)
        
        email_window.focus_force()
