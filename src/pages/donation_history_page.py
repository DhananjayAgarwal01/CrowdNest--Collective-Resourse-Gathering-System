import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.modern_ui import ModernUI

class DonationHistoryPage:
    def __init__(self, parent, donations, show_frame_callback):
        """Initialize the donation history page"""
        # Create main frame
        self.frame = ModernUI.create_card(parent)
        self.frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Store parameters
        # Ensure donations is a list, default to empty list if not
        self.donations = donations if isinstance(donations, list) else []
        self.show_frame = show_frame_callback
        
        # Title
        ttk.Label(
            self.frame,
            text="My Donation History",
            style='Title.TLabel'
        ).pack(pady=(0, 20))
        
        # Create Treeview for donation history
        columns = ('title', 'category', 'condition', 'location', 'status', 'date')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings', style='Treeview')
        
        # Define column headings
        self.tree.heading('title', text='Title')
        self.tree.heading('category', text='Category')
        self.tree.heading('condition', text='Condition')
        self.tree.heading('location', text='Location')
        self.tree.heading('status', text='Status')
        self.tree.heading('date', text='Donated Date')
        
        # Define column widths
        self.tree.column('title', width=200)
        self.tree.column('category', width=100)
        self.tree.column('condition', width=100)
        self.tree.column('location', width=150)
        self.tree.column('status', width=100)
        self.tree.column('date', width=150)
        
        # Add scrollbar
        tree_scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        
        # Populate treeview with donation history
        self.populate_donations()
        
        # Back button
        ModernUI.create_button(
            self.frame,
            "Back to Dashboard",
            lambda: self.show_frame('dashboard'),
            style='Secondary.TButton'
        ).pack(side='bottom', pady=10)
    
    def populate_donations(self):
        """Populate the treeview with donations"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add donations to treeview
        if not self.donations:
            # Show a message if no donations
            self.tree.insert('', 'end', values=('No donations found', '', '', '', '', ''))
        else:
            for donation in self.donations:
                # Use .get() to safely retrieve values with defaults
                self.tree.insert('', 'end', values=(
                    donation.get('title', 'N/A'),
                    donation.get('category', 'N/A'),
                    donation.get('condition', 'N/A'),
                    donation.get('location', 'N/A'),
                    donation.get('status', 'N/A'),
                    donation.get('updated_at', 'N/A')
                ))
    
    def reset(self):
        """Reset the page (called during logout)"""
        # Clear donations
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.donations = []
