import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
import io
import base64
from src.constants import COLORS, CATEGORIES, CONDITIONS, LOCATIONS
from src.ui.modern_ui import ModernUI

class DonationListPage:
    def __init__(self, parent, get_donations_callback, contact_donor_callback, show_frame_callback, update_status_callback=None):
        self.parent = parent
        self.get_donations = get_donations_callback
        self.contact_donor_callback = contact_donor_callback
        self.show_frame = show_frame_callback
        self.update_status_callback = update_status_callback
        self.frame = None
        self.search_entry = None
        self.category_filter = None
        self.condition_filter = None
        self.location_filter = None
        self.status_filter = None
        self.donations_tree = None
        self.create_frame()
        
    def create_frame(self):
        self.frame = ModernUI.create_card(self.parent)
        
        # Create a canvas with scrollbar for scrolling
        canvas = tk.Canvas(self.frame, bg=COLORS['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')
        
        # Configure the canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=800)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create header
        header_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(20,10))
        
        ttk.Label(
            header_frame,
            text="🎁 Available Donations",
            style='Title.TLabel'
        ).pack(side='left')
        
        # Create search and filter section
        search_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        search_frame.pack(fill='x', padx=20, pady=10)
        
        # Search box
        search_box_frame = ttk.Frame(search_frame, style='Card.TFrame')
        search_box_frame.pack(side='left', fill='x', expand=True, padx=(0,10))
        
        self.search_entry = ModernUI.create_entry(
            search_box_frame,
            placeholder="Search donations..."
        )
        self.search_entry.pack(side='left', fill='x', expand=True)
        self.search_entry.bind('<Return>', lambda e: self.refresh_donations())
        
        # Filter dropdowns
        filters_frame = ttk.Frame(search_frame, style='Card.TFrame')
        filters_frame.pack(side='right', fill='x')
        
        # Status filter
        self.status_filter = ModernUI.create_dropdown(
            filters_frame,
            ["All Status", "Available", "Received", "Donated"],
            "All Status"
        )
        self.status_filter.pack(side='left', padx=5)
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_donations())
        
        # Category filter
        self.category_filter = ModernUI.create_dropdown(
            filters_frame,
            ["All Categories"] + CATEGORIES,
            "All Categories"
        )
        self.category_filter.pack(side='left', padx=5)
        self.category_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_donations())
        
        # Condition filter
        self.condition_filter = ModernUI.create_dropdown(
            filters_frame,
            ["All Conditions"] + CONDITIONS,
            "All Conditions"
        )
        self.condition_filter.pack(side='left', padx=5)
        self.condition_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_donations())
        
        # Location filter
        self.location_filter = ModernUI.create_dropdown(
            filters_frame,
            ["All Locations"] + LOCATIONS,
            "All Locations"
        )
        self.location_filter.pack(side='left', padx=5)
        self.location_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_donations())
        
        # Create donations list
        donations_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        donations_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create Treeview
        columns = ('title', 'category', 'condition', 'location', 'donor', 'status')
        self.donations_tree = ttk.Treeview(donations_frame, columns=columns, show='headings', style='Treeview')
        
        # Define column headings
        self.donations_tree.heading('title', text='Title')
        self.donations_tree.heading('category', text='Category')
        self.donations_tree.heading('condition', text='Condition')
        self.donations_tree.heading('location', text='Location')
        self.donations_tree.heading('donor', text='Donor')
        self.donations_tree.heading('status', text='Status')
        
        # Define column widths
        self.donations_tree.column('title', width=200)
        self.donations_tree.column('category', width=100)
        self.donations_tree.column('condition', width=100)
        self.donations_tree.column('location', width=150)
        self.donations_tree.column('donor', width=150)
        self.donations_tree.column('status', width=100)
        
        # Add scrollbar to treeview
        tree_scrollbar = ttk.Scrollbar(donations_frame, orient='vertical', command=self.donations_tree.yview)
        self.donations_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Pack the treeview and its scrollbar
        self.donations_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        
        # Bind double-click event
        self.donations_tree.bind('<Double-1>', self.on_donation_select)
        
        # Create button frame
        button_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        button_frame.pack(fill='x', padx=20, pady=10)
        
        # Add buttons
        ModernUI.create_button(
            button_frame,
            "View Selected",
            self.view_donation_details
        ).pack(side='left', padx=5)
        
        ModernUI.create_button(
            button_frame,
            "Contact Donor",
            self.contact_donor
        ).pack(side='left', padx=5)
        
        ModernUI.create_button(
            button_frame,
            "Back to Dashboard",
            lambda: self.show_frame('dashboard'),
            style='Secondary.TButton'
        ).pack(side='right', padx=5)
        
        # Load initial donations
        self.refresh_donations()
    
    def refresh_donations(self):
        search_term = self.search_entry.get()
        category = self.category_filter.get() if self.category_filter.get() != "All Categories" else None
        condition = self.condition_filter.get() if self.condition_filter.get() != "All Conditions" else None
        location = self.location_filter.get() if self.location_filter.get() != "All Locations" else None
        status = self.status_filter.get() if self.status_filter.get() != "All Status" else None
        
        donations = self.get_donations(search_term, category, condition, location, status)
        self.update_donation_list(donations)
    
    def update_donation_list(self, donations):
        """Update the donations list with new data"""
        # Clear existing items
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
            
        # Add new items
        for donation in donations:
            self.donations_tree.insert(
                '',
                'end',
                values=(
                    donation['title'],
                    donation['category'],
                    donation['condition'],
                    donation['location'],
                    donation['donor_name'],
                    donation['status']
                ),
                tags=(str(donation['unique_id']),)
            )
            
    def view_donation_details(self):
        """View details of selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a donation to view")
            return
            
        item = selected_items[0]
        donation = {
            'id': self.donations_tree.item(item)['tags'][0],
            'values': self.donations_tree.item(item)['values']
        }
        
        # Create popup window
        popup = tk.Toplevel()
        popup.title("Donation Details")
        popup.geometry("500x600")
        
        # Create main frame
        main_frame = ModernUI.create_card(popup)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(
            main_frame,
            text=donation['values'][0],
            style='Title.TLabel'
        ).pack(pady=(0, 10))
        
        # Category and condition badges
        badges_frame = ttk.Frame(main_frame, style='Card.TFrame')
        badges_frame.pack(fill='x', pady=5)
        
        ttk.Label(
            badges_frame,
            text=donation['values'][1],
            style='CategoryBadge.TLabel'
        ).pack(side='left', padx=5)
        
        ttk.Label(
            badges_frame,
            text=donation['values'][2],
            style='ConditionBadge.TLabel'
        ).pack(side='left', padx=5)
        
        # Location
        location_frame = ttk.Frame(main_frame, style='Card.TFrame')
        location_frame.pack(fill='x', pady=10)
        
        ttk.Label(
            location_frame,
            text="📍 " + donation['values'][3],
            style='Card.TLabel'
        ).pack(anchor='w')
        
        # Donor info
        donor_frame = ttk.Frame(main_frame, style='Card.TFrame')
        donor_frame.pack(fill='x', pady=10)
        
        ttk.Label(
            donor_frame,
            text="👤 Donated by: " + donation['values'][4],
            style='Card.TLabel'
        ).pack(anchor='w')
        
        # Status
        status_frame = ttk.Frame(main_frame, style='Card.TFrame')
        status_frame.pack(fill='x', pady=10)
        
        ttk.Label(
            status_frame,
            text="Status: " + donation['values'][5],
            style='Card.TLabel'
        ).pack(anchor='w')
        
        # Action buttons
        button_frame = ttk.Frame(main_frame, style='Card.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        ModernUI.create_button(
            button_frame,
            "Contact Donor",
            lambda: self.contact_donor(donation['id'])
        ).pack(side='left', padx=5)
        
        ModernUI.create_button(
            button_frame,
            "Close",
            popup.destroy,
            style='Secondary.TButton'
        ).pack(side='left', padx=5)
    
    def contact_donor(self, item=None):
        if not item:
            selection = self.donations_tree.selection()
            if not selection:
                messagebox.showinfo("Info", "Please select a donation first")
                return
            item = selection[0]
        
        try:
            # Try to get the donation ID from tags first
            tags = self.donations_tree.item(item, 'tags')
            if tags:
                donation_id = tags[0]
            else:
                # If no tags, get the ID from the values
                values = self.donations_tree.item(item, 'values')
                if values and len(values) > 0:
                    # Assuming the first value is the donation ID
                    donation_id = values[0]
                else:
                    messagebox.showerror("Error", "Unable to retrieve donation ID")
                    return
        except Exception as e:
            print(f"Error retrieving donation ID: {e}")
            messagebox.showerror("Error", "Error retrieving donation details")
            return
        
        # Call the contact donor callback function provided by the main app
        try:
            self.contact_donor_callback(donation_id)
        except Exception as e:
            print(f"Error in contact_donor_callback: {e}")
            messagebox.showerror("Error", "Unable to contact donor")
    
    def on_donation_select(self, event):
        self.view_donation_details()
    
    def update_donation_status(self, donation_id, new_status):
        """Update the status of a donation"""
        if self.update_status_callback:
            success, message = self.update_status_callback(donation_id, new_status)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_donations()
            else:
                messagebox.showerror("Error", message)