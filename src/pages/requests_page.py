import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.modern_ui import ModernUI
from src.utils.email_validator import EmailValidator

class RequestsPage(ttk.Frame):
    def __init__(self, parent, db_handler, user_info, show_frame_callback):
        super().__init__(parent)
        self.parent = parent
        self.db = db_handler
        self.user_info = user_info
        self.show_frame = show_frame_callback
        
        # Create the main frame
        self.create_frame()
        
    def create_frame(self):
        """Create the requests page frame"""
        # Main container with padding
        self.frame = ModernUI.create_card(self.parent)
        self.frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(
            self.frame,
            text="Donation Requests",
            style='Title.TLabel'
        ).pack(pady=(0, 20))
        
        # Create Treeview for requests
        columns = ('title', 'requester', 'status', 'date')
        self.requests_tree = ttk.Treeview(self.frame, columns=columns, show='headings', style='Treeview')
        
        # Define column headings
        self.requests_tree.heading('title', text='Donation Title')
        self.requests_tree.heading('requester', text='Requester')
        self.requests_tree.heading('status', text='Status')
        self.requests_tree.heading('date', text='Request Date')
        
        # Define column widths
        self.requests_tree.column('title', width=200)
        self.requests_tree.column('requester', width=150)
        self.requests_tree.column('status', width=100)
        self.requests_tree.column('date', width=150)
        
        # Add scrollbar
        tree_scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.requests_tree.yview)
        self.requests_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.requests_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        
        # Buttons frame
        button_frame = ttk.Frame(self.frame, style='Card.TFrame')
        button_frame.pack(fill='x', pady=10)
        
        # Accept button
        ModernUI.create_button(
            button_frame,
            "Accept Request",
            self.accept_request
        ).pack(side='left', padx=5)
        
        # Decline button
        ModernUI.create_button(
            button_frame,
            "Decline Request",
            self.decline_request,
            style='Secondary.TButton'
        ).pack(side='left', padx=5)
        
        # Back button
        ModernUI.create_button(
            button_frame,
            "Back",
            lambda: self.show_frame('dashboard'),
            style='Secondary.TButton'
        ).pack(side='right', padx=5)
        
        # Load initial requests
        self.refresh_requests()
    
    def refresh_requests(self):
        """Refresh the requests list"""
        # Clear existing items
        for item in self.requests_tree.get_children():
            self.requests_tree.delete(item)
        
        # Get requests from database
        requests = self.db.get_donation_requests(self.user_info['unique_id'])
        
        # Add requests to treeview
        for request in requests:
            self.requests_tree.insert('', 'end', values=(
                request['donation_title'],
                request['requester_name'],
                request['status'],
                request['created_at']
            ))
    
    def accept_request(self):
        """Accept the selected request"""
        selected_items = self.requests_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a request to accept")
            return
        
        request_id = self.requests_tree.set(selected_items[0], 'unique_id')
        success, message = self.db.update_request_status(request_id, 'accepted')
        
        if success:
            # Send email notification
            request = self.db.get_request_details(request_id)
            EmailValidator.send_communication_email(
                self.user_info['full_name'],
                self.user_info['email'],
                request['requester_email'],
                "Donation Request Accepted",
                f"Your request for {request['donation_title']} has been accepted."
            )
            messagebox.showinfo("Success", "Request accepted successfully")
            self.refresh_requests()
        else:
            messagebox.showerror("Error", message)
    
    def decline_request(self):
        """Decline the selected request"""
        selected_items = self.requests_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a request to decline")
            return
        
        request_id = self.requests_tree.set(selected_items[0], 'unique_id')
        success, message = self.db.update_request_status(request_id, 'declined')
        
        if success:
            # Send email notification
            request = self.db.get_request_details(request_id)
            EmailValidator.send_communication_email(
                self.user_info['full_name'],
                self.user_info['email'],
                request['requester_email'],
                "Donation Request Declined",
                f"Your request for {request['donation_title']} has been declined."
            )
            messagebox.showinfo("Success", "Request declined successfully")
            self.refresh_requests()
        else:
            messagebox.showerror("Error", message)