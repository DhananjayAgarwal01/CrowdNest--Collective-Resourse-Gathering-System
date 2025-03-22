import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.components import ModernUI
from src.constants import COLORS, CATEGORIES, CONDITIONS, LOCATIONS
import base64
from PIL import Image, ImageTk
import io
import scrolledtext

class DonationListPage:
    def __init__(self, parent, get_donations_callback, contact_donor_callback):
        self.parent = parent
        self.get_donations = get_donations_callback
        self.contact_donor_callback = contact_donor_callback
        self.frame = None
        self.search_entry = None
        self.category_filter = None
        self.condition_filter = None
        self.location_filter = None
        self.donations_tree = None
        self.create_frame()
        self.load_donations()  # Load all donations by default
        
    def create_frame(self):
        self.frame = ModernUI.create_card(self.parent)
        
        # Create a scrollable canvas for the content
        canvas = tk.Canvas(self.frame, bg=COLORS['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=800)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        
        # Header
        header_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        header_frame.pack(fill='x', pady=(20, 30))
        
        ttk.Label(header_frame, text="Available Donations", style='Title.TLabel').pack()
        ttk.Label(header_frame, text="Find items you need", style='Subtitle.TLabel').pack()
        
        # Search and filter section
        search_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        search_frame.pack(fill='x', padx=40, pady=20)
        
        # Search bar with icon
        search_box_frame = ttk.Frame(search_frame, style='Card.TFrame')
        search_box_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(search_box_frame, text="🔍", font=('Segoe UI', 12)).pack(side='left', padx=(0, 5))
        self.search_entry = ModernUI.create_entry(search_box_frame, "Search donations...", width=50)
        self.search_entry.pack(side='left', padx=5)
        ModernUI.create_button(search_box_frame, "Search", self.search_donations, style='Primary.TButton').pack(side='left', padx=5)
        
        # Filters
        filter_frame = ttk.Frame(search_frame, style='Card.TFrame')
        filter_frame.pack(fill='x')
        
        # Category filter
        self.category_filter = ModernUI.create_dropdown(filter_frame, ["All Categories"] + CATEGORIES, "Category", width=20)
        self.category_filter.pack(side='left', padx=5)
        
        # Condition filter
        self.condition_filter = ModernUI.create_dropdown(filter_frame, ["All Conditions"] + CONDITIONS, "Condition", width=20)
        self.condition_filter.pack(side='left', padx=5)
        
        # Location filter
        self.location_filter = ModernUI.create_dropdown(filter_frame, ["All Locations"] + LOCATIONS, "Location", width=20)
        self.location_filter.pack(side='left', padx=5)
        
        # Clear filters button
        ModernUI.create_button(filter_frame, "Clear Filters", self.clear_filters, style='Secondary.TButton').pack(side='right', padx=5)
        
        # Donations list
        list_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        list_frame.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Configure Treeview with more columns
        columns = ('Title', 'Category', 'Condition', 'Location', 'Donor', 'Date')
        self.donations_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure headings and columns
        column_widths = {
            'Title': 200,
            'Category': 150,
            'Condition': 100,
            'Location': 150,
            'Donor': 100,
            'Date': 100
        }
        
        for col, width in column_widths.items():
            self.donations_tree.heading(col, text=col)
            self.donations_tree.column(col, width=width)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.donations_tree.yview)
        x_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.donations_tree.xview)
        self.donations_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Pack the treeview and scrollbars
        self.donations_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.donations_tree.bind('<Double-1>', self.show_donation_preview)
        
        # Action buttons
        button_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        button_frame.pack(fill='x', padx=40, pady=20)
        
        ModernUI.create_button(button_frame, "Request Selected", self.request_donation, width=20).pack(side='left', padx=5)
        ModernUI.create_button(button_frame, "Contact Donor", self.contact_donor, width=20).pack(side='left', padx=5)
        ModernUI.create_button(button_frame, "Back to Dashboard", 
                             lambda: self.parent.show_frame('dashboard'), 
                             style='Secondary.TButton', width=20).pack(side='right', padx=5)
    
    def load_donations(self, search_query=None, category=None, condition=None, location=None):
        donations = self.get_donations(search_query, category, condition, location)
        self.update_donation_list(donations)
    
    def search_donations(self):
        search_term = self.search_entry.get()
        category = self.category_filter.get() if self.category_filter.get() != "Category" and self.category_filter.get() != "All Categories" else None
        condition = self.condition_filter.get() if self.condition_filter.get() != "Condition" and self.condition_filter.get() != "All Conditions" else None
        location = self.location_filter.get() if self.location_filter.get() != "Location" and self.location_filter.get() != "All Locations" else None
        
        self.load_donations(search_term, category, condition, location)
    
    def clear_filters(self):
        self.category_filter.set("Category")
        self.condition_filter.set("Condition")
        self.location_filter.set("Location")
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Search donations...")
        self.load_donations()
    
    def update_donation_list(self, donations):
        # Clear existing items
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
        
        # Add new items
        for donation in donations:
            self.donations_tree.insert('', 'end', values=(
                donation['title'],
                donation['category'],
                donation['condition'],
                donation['location'],
                donation['donor_name'],
                donation['created_at']
            ), tags=(donation['unique_id'],))
    
    def show_donation_preview(self, event):
        # Get selected item
        selection = self.donations_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        donation = self.donations_tree.item(item)
        
        # Create preview dialog
        preview = tk.Toplevel(self.parent)
        preview.title("Donation Preview")
        preview.geometry("800x600")
        
        # Configure the preview window
        preview.configure(bg=COLORS['background'])
        preview.transient(self.parent)
        preview.grab_set()
        
        # Create main container
        main_frame = ttk.Frame(preview, style='Card.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left side - Image
        image_frame = ttk.Frame(main_frame, style='Card.TFrame')
        image_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Image display with shadow effect
        image_label = ttk.Label(image_frame, style='Card.TLabel')
        image_label.pack(fill='both', expand=True, padx=10, pady=10)
        
        try:
            # Load and resize image
            image_data = base64.b64decode(donation['values'][0])
            img = Image.open(io.BytesIO(image_data))
            img.thumbnail((400, 400))  # Maintain aspect ratio
            photo = ImageTk.PhotoImage(img)
            image_label.configure(image=photo)
            image_label.image = photo
        except:
            # Show placeholder if image fails to load
            image_label.configure(text="Image not available")
        
        # Right side - Details
        details_frame = ttk.Frame(main_frame, style='Card.TFrame')
        details_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Title with custom font and color
        title_label = ttk.Label(
            details_frame,
            text=donation['values'][0],
            font=('Segoe UI', 24, 'bold'),
            foreground=COLORS['primary'],
            style='Card.TLabel',
            wraplength=350
        )
        title_label.pack(fill='x', pady=(0, 10))
        
        # Status badge
        status_frame = ttk.Frame(details_frame, style='Card.TFrame')
        status_frame.pack(fill='x', pady=(0, 15))
        status_label = ttk.Label(
            status_frame,
            text="Available",
            style='StatusBadge.TLabel'
        )
        status_label.pack(side='left')
        
        # Category and condition badges
        category_label = ttk.Label(
            status_frame,
            text=donation['values'][1],
            style='CategoryBadge.TLabel'
        )
        category_label.pack(side='left', padx=5)
        
        condition_label = ttk.Label(
            status_frame,
            text=donation['values'][2],
            style='ConditionBadge.TLabel'
        )
        condition_label.pack(side='left')
        
        # Description with scrolled text
        desc_label = ttk.Label(
            details_frame,
            text="Description",
            font=('Segoe UI', 12, 'bold'),
            style='Card.TLabel'
        )
        desc_label.pack(fill='x', pady=(0, 5))
        
        desc_text = scrolledtext.ScrolledText(
            details_frame,
            wrap=tk.WORD,
            height=6,
            font=('Segoe UI', 10),
            bg=COLORS['card'],
            fg=COLORS['text']
        )
        desc_text.insert('1.0', "No description available")
        desc_text.configure(state='disabled')
        desc_text.pack(fill='both', expand=True, pady=(0, 15))
        
        # Location and donor info
        info_frame = ttk.Frame(details_frame, style='Card.TFrame')
        info_frame.pack(fill='x', pady=(0, 15))
        
        # Location with icon
        location_frame = ttk.Frame(info_frame, style='Card.TFrame')
        location_frame.pack(fill='x', pady=2)
        ttk.Label(
            location_frame,
            text="📍",
            style='Card.TLabel'
        ).pack(side='left')
        ttk.Label(
            location_frame,
            text=donation['values'][3],
            style='Card.TLabel'
        ).pack(side='left', padx=5)
        
        # Donor info with icon
        donor_frame = ttk.Frame(info_frame, style='Card.TFrame')
        donor_frame.pack(fill='x', pady=2)
        ttk.Label(
            donor_frame,
            text="👤",
            style='Card.TLabel'
        ).pack(side='left')
        ttk.Label(
            donor_frame,
            text=f"Posted by {donation['values'][4]}",
            style='Card.TLabel'
        ).pack(side='left', padx=5)
        
        # Date info with icon
        date_frame = ttk.Frame(info_frame, style='Card.TFrame')
        date_frame.pack(fill='x', pady=2)
        ttk.Label(
            date_frame,
            text="🕒",
            style='Card.TLabel'
        ).pack(side='left')
        ttk.Label(
            date_frame,
            text=f"Posted on {donation['values'][5]}",
            style='Card.TLabel'
        ).pack(side='left', padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(details_frame, style='Card.TFrame')
        button_frame.pack(fill='x', pady=(15, 0))
        
        ModernUI.create_button(
            button_frame,
            "Contact Donor",
            lambda: [self.contact_donor(donation['tags'][0]), preview.destroy()],
            width=20
        ).pack(side='left', padx=5)
        
        ModernUI.create_button(
            button_frame,
            "Close",
            preview.destroy,
            style='Secondary.TButton',
            width=15
        ).pack(side='right', padx=5)
    
    def request_donation(self, item=None):
        if not item:
            selection = self.donations_tree.selection()
            if not selection:
                messagebox.showinfo("Info", "Please select a donation first")
                return
            item = selection[0]
        
        donation_id = self.donations_tree.item(item, 'tags')[0]
        
        # Create request dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Request Donation")
        dialog.geometry("500x300")
        dialog.configure(bg=COLORS['card'])
        
        # Center the dialog
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Content frame
        content = ttk.Frame(dialog, style='Card.TFrame')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(content, text="Request Donation", style='Title.TLabel').pack(pady=(0, 20))
        
        # Message field
        ttk.Label(content, text="Message to Donor", style='Subtitle.TLabel').pack(anchor='w')
        message_text = tk.Text(content, height=5, width=50, wrap='word')
        message_text.configure(font=('Segoe UI', 10), padx=10, pady=5)
        message_text.pack(pady=(5, 20))
        
        # Buttons
        button_frame = ttk.Frame(content, style='Card.TFrame')
        button_frame.pack(fill='x', pady=10)
        
        def submit_request():
            message = message_text.get("1.0", tk.END).strip()
            if not message:
                messagebox.showerror("Error", "Please enter a message to the donor")
                return
            
            # Call the request donation callback function provided by the main app
            if self.get_donations(message=message, donation_id=donation_id):
                messagebox.showinfo("Success", "Request sent successfully!")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to send request")
        
        ModernUI.create_button(button_frame, "Send Request", submit_request, width=15).pack(side='left', padx=5)
        ModernUI.create_button(button_frame, "Cancel", dialog.destroy, style='Secondary.TButton', width=15).pack(side='right', padx=5)
    
    def contact_donor(self, item=None):
        if not item:
            selection = self.donations_tree.selection()
            if not selection:
                messagebox.showinfo("Info", "Please select a donation first")
                return
            item = selection[0]
        
        donation_id = self.donations_tree.item(item, 'tags')[0]
        
        # Call the contact donor callback function provided by the main app
        self.contact_donor_callback(donation_id)

    def display_donation(self, donation, row, col):
        """Display a single donation item"""
        # Create a frame for this donation
        donation_frame = ttk.Frame(self.frame, style='Card.TFrame', padding=10)
        donation_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Image display
        img_frame = ttk.Frame(donation_frame, style='Card.TFrame')
        img_frame.pack(fill='x', pady=(0, 10))
        
        # Try to display the first image
        if donation.get('all_images') and donation['all_images'][0]:
            try:
                # Decode base64 image
                img_data = base64.b64decode(donation['all_images'][0])
                img = Image.open(io.BytesIO(img_data))
                
                # Create thumbnail
                img.thumbnail((200, 200))
                photo = ImageTk.PhotoImage(img)
                
                # Create and pack the image label
                img_label = ttk.Label(img_frame, image=photo)
                img_label.image = photo  # Keep a reference!
                img_label.pack(pady=5)
            except Exception as e:
                print(f"Error displaying image: {e}")
                # Fallback to placeholder
                ttk.Label(
                    img_frame,
                    text="📦",
                    font=('Segoe UI', 48),
                    foreground=COLORS['primary']
                ).pack(pady=5)
        else:
            # No image placeholder
            ttk.Label(
                img_frame,
                text="📦",
                font=('Segoe UI', 48),
                foreground=COLORS['primary']
            ).pack(pady=5)
        
        # Title
        title_label = ttk.Label(
            donation_frame, 
            text=donation['title'],
            style='Title.TLabel',
            wraplength=200
        )
        title_label.pack(fill='x')
        
        # Category and Condition
        details_frame = ttk.Frame(donation_frame, style='Card.TFrame')
        details_frame.pack(fill='x', pady=5)
        
        ttk.Label(
            details_frame,
            text=f"📦 {donation['category']}",
            style='Subtitle.TLabel'
        ).pack(side='left', padx=5)
        
        ttk.Label(
            details_frame,
            text=f"✨ {donation['condition']}",
            style='Subtitle.TLabel'
        ).pack(side='right', padx=5)
        
        # Location
        ttk.Label(
            donation_frame,
            text=f"📍 {donation['location']}",
            style='Subtitle.TLabel'
        ).pack(fill='x', pady=5)
        
        # Donor info and date
        donor_frame = ttk.Frame(donation_frame, style='Card.TFrame')
        donor_frame.pack(fill='x', pady=5)
        
        ttk.Label(
            donor_frame,
            text=f"👤 {donation['donor_name']}",
            style='Subtitle.TLabel'
        ).pack(side='left')
        
        date_str = donation['created_at'].strftime('%Y-%m-%d') if donation['created_at'] else 'N/A'
        ttk.Label(
            donor_frame,
            text=f"📅 {date_str}",
            style='Subtitle.TLabel'
        ).pack(side='right')
        
        # Action buttons
        button_frame = ttk.Frame(donation_frame, style='Card.TFrame')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Request button
        ModernUI.create_button(
            button_frame,
            "Request Item",
            lambda d=donation: self.request_donation(d['unique_id']),
            width=15
        ).pack(side='left', padx=2)
        
        # Contact button
        ModernUI.create_button(
            button_frame,
            "Contact Donor",
            lambda d=donation: self.contact_donor_callback(d['donor_name']),
            style='Secondary.TButton',
            width=15
        ).pack(side='right', padx=2)