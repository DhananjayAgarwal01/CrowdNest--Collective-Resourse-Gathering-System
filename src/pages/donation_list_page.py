import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.modern_ui import ModernUI
from src.utils.email_validator import EmailValidator
from src.constants import COLORS, CATEGORIES, CONDITIONS, LOCATIONS, STATES
from src.database.database_handler import DatabaseHandler

class DonationListPage:
    def __init__(self, parent, user_info, show_frame_callback):
        """Initialize the donation list page"""
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
            text="Available Donations",
            style='Title.TLabel'
        ).pack(pady=(0, 20))
        
        # Search frame with modern styling
        search_frame = ttk.Frame(self.frame, style='Card.TFrame')
        search_frame.pack(fill='x', pady=(0, 20), padx=10)
        
        # Search title
        ttk.Label(
            search_frame,
            text="Filter Donations",
            style='Subtitle.TLabel'
        ).pack(pady=(10, 15), padx=10, anchor='w')
        
        # Create filter container
        filter_container = ttk.Frame(search_frame)
        filter_container.pack(fill='x', padx=10, pady=(0, 10))
        
        # Search entry with icon
        search_container = ttk.Frame(filter_container)
        search_container.pack(side='left', padx=(0, 10), fill='x', expand=True)
        ttk.Label(search_container, text='🔍', font=('Segoe UI', 10)).pack(side='left', padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_container, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', fill='x', expand=True)
        
        # Category dropdown with icon
        category_container = ttk.Frame(filter_container)
        category_container.pack(side='left', padx=10)
        ttk.Label(category_container, text='📦', font=('Segoe UI', 10)).pack(side='left', padx=(0, 5))
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(category_container, textvariable=self.category_var, values=list(CATEGORIES), width=20)
        category_combo.pack(side='left')
        
        # State dropdown with icon
        state_container = ttk.Frame(filter_container)
        state_container.pack(side='left', padx=10)
        ttk.Label(state_container, text='📍', font=('Segoe UI', 10)).pack(side='left', padx=(0, 5))
        self.state_var = tk.StringVar()
        states_list = ['All Locations'] + list(STATES.keys())
        self.state_combo = ttk.Combobox(state_container, textvariable=self.state_var, values=states_list, width=20)
        self.state_combo.set('All Locations')
        self.state_combo.pack(side='left')
        
        # City dropdown
        city_container = ttk.Frame(filter_container)
        city_container.pack(side='left', padx=10)
        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(city_container, textvariable=self.city_var, width=20)
        self.city_combo.pack(side='left')
        
        # Bind state selection to update cities
        self.state_combo.bind('<<ComboboxSelected>>', self.update_cities)
        
        def update_cities(self, event=None):
            selected_state = self.state_var.get()
            if selected_state == 'All Locations':
                self.city_combo['values'] = []
                self.city_var.set('')
                self.city_combo['state'] = 'disabled'
            else:
                self.city_combo['state'] = 'normal'
                self.city_combo['values'] = STATES.get(selected_state, [])
                self.city_var.set('')
        
        def clear_filters(self):
            self.search_var.set('')
            self.category_var.set('')
            self.state_var.set('All Locations')
            self.city_var.set('')
            self.city_combo['state'] = 'disabled'
            self.search_donations()
        
        def search_donations(self):
            search_query = self.search_var.get().strip()
            category = self.category_var.get()
            state = self.state_var.get()
            city = self.city_var.get()
            
            location = None
            if state != 'All Locations' and state:
                location = state if not city else city
            
            # Clear existing items
            for item in self.donations_tree.get_children():
                self.donations_tree.delete(item)
            
            # Search donations
            donations = self.db.search_donations(
                search_query=search_query if search_query else None,
                category=category if category else None,
                location=location
            )
        
        # Search button container
        button_container = ttk.Frame(search_frame)
        button_container.pack(fill='x', padx=10, pady=(0, 10))
        
        # Search button with modern styling
        search_btn = ModernUI.create_button(
            button_container,
            "🔍 Search Donations",
            self.search_donations,
            style='Primary.TButton'
        )
        search_btn.pack(side='left', padx=5)
        
        # Clear filters button
        clear_btn = ModernUI.create_button(
            button_container,
            "❌ Clear Filters",
            self.clear_filters,
            style='Secondary.TButton'
        )
        clear_btn.pack(side='left', padx=5)
        
        # Create Treeview for donations
        columns = ('unique_id', 'title', 'category', 'condition', 'location', 'donor', 'status', 'email')
        self.donations_tree = ttk.Treeview(self.frame, columns=columns, show='headings', style='Treeview')
        
        # Define column headings
        self.donations_tree.heading('unique_id', text='ID')
        self.donations_tree.heading('title', text='Title')
        self.donations_tree.heading('category', text='Category')
        self.donations_tree.heading('condition', text='Condition')
        self.donations_tree.heading('location', text='Location')
        self.donations_tree.heading('donor', text='Donor')
        self.donations_tree.heading('status', text='Status')
        self.donations_tree.heading('email', text='Contact Email')
        
        # Define column widths
        self.donations_tree.column('unique_id', width=50)
        self.donations_tree.column('title', width=200)
        self.donations_tree.column('category', width=100)
        self.donations_tree.column('condition', width=100)
        self.donations_tree.column('location', width=150)
        self.donations_tree.column('donor', width=150)
        self.donations_tree.column('status', width=100)
        self.donations_tree.column('email', width=150)
        
        # Add scrollbar to treeview
        tree_scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.donations_tree.yview)
        self.donations_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.donations_tree.pack(side='top', fill='both', expand=True)
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
            self.view_donation_details,
            style='Primary.TButton'
        ).pack(side='left', padx=5)
        
        # Send email button
        ModernUI.create_button(
            action_frame,
            "Send Email to Donor",
            self.send_email_dialog,
            style='Primary.TButton'
        ).pack(side='left', padx=5)
        
        # Delete button (only visible to donation owner)
        self.delete_btn = ModernUI.create_button(
            action_frame,
            "Delete Donation",
            self.delete_donation,
            style='Danger.TButton'
        )
        self.delete_btn.pack(side='left', padx=5)
        self.delete_btn.pack_forget()  # Initially hidden
        
        # Load initial donations
        self.refresh_donations()
    
    def update_cities(self, event=None):
        """Update cities dropdown based on selected state"""
        selected_state = self.state_var.get()
        if selected_state in STATES:
            self.city_combo['values'] = STATES[selected_state]
            self.city_var.set('')  # Clear city selection
    
    def clear_filters(self):
        """Clear all search filters"""
        self.search_var.set('')
        self.category_var.set('')
        self.state_var.set('')
        self.city_var.set('')
        self.search_donations()
    
    def search_donations(self):
        """Search donations based on criteria"""
        search_query = self.search_var.get()
        category = self.category_var.get() or None
        state = self.state_var.get() or None
        city = self.city_var.get() or None
        
        # Combine state and city for location search
        location = None
        if city:
            location = city
        elif state:
            location = state
        
        donations = self.db.search_donations(search_query, category, location)
        self.refresh_donations(donations)
    
    def refresh_donations(self, donations=None):
        """Populate the treeview with donations"""
        # Clear existing items
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
        
        if donations is None:
            donations = self.db.search_donations()
        
        # Add donations to treeview
        for donation in donations:
            item_id = self.donations_tree.insert('', 'end', values=(
                donation['unique_id'],
                donation['title'],
                donation['category'],
                donation['condition'],
                f"{donation['city']}, {donation['state']}",
                donation['donor_name'],
                donation['status'],
                donation['donor_email']
            ))
            # Store donation ID in the item
            self.donations_tree.set(item_id, 'unique_id', donation['unique_id'])
            
            # Show delete button if user is the donor
            selected_items = self.donations_tree.selection()
            if selected_items:
                donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
                if donation.get('donor_id') == self.user_info['unique_id']:
                    self.delete_btn.pack(side='left', padx=5)
                else:
                    self.delete_btn.pack_forget()
    
    def request_item(self, donation):
        """Send a request for the selected donation"""
        if not self.user_info:
            messagebox.showerror("Error", "Please log in to request items")
            return
            
        # Create request in database
        success, message = self.db.create_donation_request(
            donation_id=donation['unique_id'],
            requester_id=self.user_info['unique_id'],
            requester_name=self.user_info['full_name'],
            requester_email=self.user_info['email']
        )
        
        if success:
            # Send email notification to donor
            EmailValidator.send_communication_email(
                self.user_info['full_name'],
                self.user_info['email'],
                donation['donor_email'],
                "New Donation Request",
                f"A new request has been made for your donation: {donation['title']}"
            )
            messagebox.showinfo("Success", "Request sent successfully")
        else:
            messagebox.showerror("Error", message)
    
    def view_donation_details(self):
        """Display detailed information about the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to view")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        donation = self.db.get_donation_details(donation_id)
        
        if not donation:
            messagebox.showerror("Error", "Could not fetch donation details")
            return
        
        # Create details window with improved styling
        details_window = tk.Toplevel(self.frame)
        details_window.title("Donation Details")
        details_window.geometry("600x600")
        
        # Add details to window with enhanced layout
        content_frame = ttk.Frame(details_window, style='Card.TFrame', padding=25)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title with larger font and emphasis
        title_label = ttk.Label(content_frame, text=donation['title'], style='Title.TLabel', font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Information section with improved spacing and organization
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill='x', pady=(0, 20))
        
        # Left column
        left_frame = ttk.Frame(info_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(left_frame, text="Category", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['category']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Condition", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['condition']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Location", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=f"{donation['city']}, {donation['state']}").pack(anchor='w', pady=(0, 10))
        
        # Right column
        right_frame = ttk.Frame(info_frame)
        right_frame.pack(side='right', fill='x', expand=True)
        
        ttk.Label(right_frame, text="Donor", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_name']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Status", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['status']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Contact", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_email']).pack(anchor='w', pady=(0, 10))
        
        # Description section with improved visibility
        description_frame = ttk.LabelFrame(content_frame, text="Description", padding=15)
        description_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        description_text = tk.Text(description_frame, wrap='word', height=6, width=50, font=('Segoe UI', 10))
        description_text.insert('1.0', donation['description'])
        description_text.configure(state='disabled')
        description_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Request button (only visible if user is not the donor)
        if donation.get('donor_id') != self.user_info['unique_id'] and donation['status'] == 'available':
            ModernUI.create_button(
                button_frame,
                "Request Item",
                lambda: self.request_item(donation),
                style='Primary.TButton'
            ).pack(side='left', padx=5)
        
        # Close button
        ModernUI.create_button(
            button_frame,
            "Close",
            details_window.destroy,
            style='Secondary.TButton'
        ).pack(side='right', padx=5)
    
    def delete_donation(self):
        """Delete the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to delete")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this donation?"):
            return
        
        # Delete donation
        if self.db.delete_donation(donation_id, self.user_info['unique_id']):
            messagebox.showinfo("Success", "Donation deleted successfully")
            self.refresh_donations()
        else:
            messagebox.showerror("Error", "Failed to delete donation")
    
    def send_email_dialog(self):
        """Open dialog to send email"""
        # Get selected item
        selected_item = self.donations_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a donation to contact")
            return
        
        # Get email from selected row
        values = self.donations_tree.item(selected_item[0])['values']
        recipient_email = values[6]
        
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

    def refresh_donations(self, donations=None):
        """Populate the treeview with donations"""
        # Clear existing items
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
        
        if donations is None:
            donations = self.db.search_donations()
        
        # Add donations to treeview
        for donation in donations:
            item_id = self.donations_tree.insert('', 'end', values=(
                donation['unique_id'],
                donation['title'],
                donation['category'],
                donation['condition'],
                f"{donation['city']}, {donation['state']}",
                donation['donor_name'],
                donation['status'],
                donation['donor_email']
            ))
            # Store donation ID in the item
            self.donations_tree.set(item_id, 'unique_id', donation['unique_id'])
            
            # Show delete button if user is the donor
            selected_items = self.donations_tree.selection()
            if selected_items:
                donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
                if donation.get('donor_id') == self.user_info['unique_id']:
                    self.delete_btn.pack(side='left', padx=5)
                else:
                    self.delete_btn.pack_forget()
    
    def request_item(self, donation):
        """Send a request for the selected donation"""
        if not self.user_info:
            messagebox.showerror("Error", "Please log in to request items")
            return
            
        # Create request in database
        success, message = self.db.create_donation_request(
            donation_id=donation['unique_id'],
            requester_id=self.user_info['unique_id'],
            requester_name=self.user_info['full_name'],
            requester_email=self.user_info['email']
        )
        
        if success:
            # Send email notification to donor
            EmailValidator.send_communication_email(
                self.user_info['full_name'],
                self.user_info['email'],
                donation['donor_email'],
                "New Donation Request",
                f"A new request has been made for your donation: {donation['title']}"
            )
            messagebox.showinfo("Success", "Request sent successfully")
        else:
            messagebox.showerror("Error", message)
    
    def view_donation_details(self):
        """Display detailed information about the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to view")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        donation = self.db.get_donation_details(donation_id)
        
        if not donation:
            messagebox.showerror("Error", "Could not fetch donation details")
            return
        
        # Create details window with improved styling
        details_window = tk.Toplevel(self.frame)
        details_window.title("Donation Details")
        details_window.geometry("600x600")
        
        # Add details to window with enhanced layout
        content_frame = ttk.Frame(details_window, style='Card.TFrame', padding=25)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title with larger font and emphasis
        title_label = ttk.Label(content_frame, text=donation['title'], style='Title.TLabel', font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Information section with improved spacing and organization
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill='x', pady=(0, 20))
        
        # Left column
        left_frame = ttk.Frame(info_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(left_frame, text="Category", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['category']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Condition", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['condition']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Location", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=f"{donation['city']}, {donation['state']}").pack(anchor='w', pady=(0, 10))
        
        # Right column
        right_frame = ttk.Frame(info_frame)
        right_frame.pack(side='right', fill='x', expand=True)
        
        ttk.Label(right_frame, text="Donor", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_name']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Status", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['status']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Contact", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_email']).pack(anchor='w', pady=(0, 10))
        
        # Description section with improved visibility
        description_frame = ttk.LabelFrame(content_frame, text="Description", padding=15)
        description_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        description_text = tk.Text(description_frame, wrap='word', height=6, width=50, font=('Segoe UI', 10))
        description_text.insert('1.0', donation['description'])
        description_text.configure(state='disabled')
        description_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Request button (only visible if user is not the donor)
        if donation.get('donor_id') != self.user_info['unique_id'] and donation['status'] == 'available':
            ModernUI.create_button(
                button_frame,
                "Request Item",
                lambda: self.request_item(donation),
                style='Primary.TButton'
            ).pack(side='left', padx=5)
        
        # Close button
        ModernUI.create_button(
            button_frame,
            "Close",
            details_window.destroy,
            style='Secondary.TButton'
        ).pack(side='right', padx=5)
    
    def delete_donation(self):
        """Delete the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to delete")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this donation?"):
            return
        
        # Delete donation
        if self.db.delete_donation(donation_id, self.user_info['unique_id']):
            messagebox.showinfo("Success", "Donation deleted successfully")
            self.refresh_donations()
        else:
            messagebox.showerror("Error", "Failed to delete donation")
    
    def send_email_dialog(self):
        """Open dialog to send email"""
        # Get selected item
        selected_item = self.donations_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a donation to contact")
            return
        
        # Get email from selected row
        values = self.donations_tree.item(selected_item[0])['values']
        recipient_email = values[6]
        
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

    def refresh_donations(self, donations=None):
        """Populate the treeview with donations"""
        # Clear existing items
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
        
        if donations is None:
            donations = self.db.search_donations()
        
        # Add donations to treeview
        for donation in donations:
            item_id = self.donations_tree.insert('', 'end', values=(
                donation['unique_id'],
                donation['title'],
                donation['category'],
                donation['condition'],
                f"{donation['city']}, {donation['state']}",
                donation['donor_name'],
                donation['status'],
                donation['donor_email']
            ))
            # Store donation ID in the item
            self.donations_tree.set(item_id, 'unique_id', donation['unique_id'])
            
            # Show delete button if user is the donor
            selected_items = self.donations_tree.selection()
            if selected_items:
                donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
                if donation.get('donor_id') == self.user_info['unique_id']:
                    self.delete_btn.pack(side='left', padx=5)
                else:
                    self.delete_btn.pack_forget()
    
    def request_item(self, donation):
        """Send a request for the selected donation"""
        if not self.user_info:
            messagebox.showerror("Error", "Please log in to request items")
            return
            
        # Create request in database
        success, message = self.db.create_donation_request(
            donation_id=donation['unique_id'],
            requester_id=self.user_info['unique_id'],
            requester_name=self.user_info['full_name'],
            requester_email=self.user_info['email']
        )
        
        if success:
            # Send email notification to donor
            EmailValidator.send_communication_email(
                self.user_info['full_name'],
                self.user_info['email'],
                donation['donor_email'],
                "New Donation Request",
                f"A new request has been made for your donation: {donation['title']}"
            )
            messagebox.showinfo("Success", "Request sent successfully")
        else:
            messagebox.showerror("Error", message)
    
    def view_donation_details(self):
        """Display detailed information about the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to view")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        donation = self.db.get_donation_details(donation_id)
        
        if not donation:
            messagebox.showerror("Error", "Could not fetch donation details")
            return
        
        # Create details window with improved styling
        details_window = tk.Toplevel(self.frame)
        details_window.title("Donation Details")
        details_window.geometry("600x600")
        
        # Add details to window with enhanced layout
        content_frame = ttk.Frame(details_window, style='Card.TFrame', padding=25)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title with larger font and emphasis
        title_label = ttk.Label(content_frame, text=donation['title'], style='Title.TLabel', font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Information section with improved spacing and organization
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill='x', pady=(0, 20))
        
        # Left column
        left_frame = ttk.Frame(info_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(left_frame, text="Category", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['category']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Condition", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['condition']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Location", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=f"{donation['city']}, {donation['state']}").pack(anchor='w', pady=(0, 10))
        
        # Right column
        right_frame = ttk.Frame(info_frame)
        right_frame.pack(side='right', fill='x', expand=True)
        
        ttk.Label(right_frame, text="Donor", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_name']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Status", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['status']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Contact", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_email']).pack(anchor='w', pady=(0, 10))
        
        # Description section with improved visibility
        description_frame = ttk.LabelFrame(content_frame, text="Description", padding=15)
        description_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        description_text = tk.Text(description_frame, wrap='word', height=6, width=50, font=('Segoe UI', 10))
        description_text.insert('1.0', donation['description'])
        description_text.configure(state='disabled')
        description_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Request button (only visible if user is not the donor)
        if donation.get('donor_id') != self.user_info['unique_id'] and donation['status'] == 'available':
            ModernUI.create_button(
                button_frame,
                "Request Item",
                lambda: self.request_item(donation),
                style='Primary.TButton'
            ).pack(side='left', padx=5)
        
        # Close button
        ModernUI.create_button(
            button_frame,
            "Close",
            details_window.destroy,
            style='Secondary.TButton'
        ).pack(side='right', padx=5)
    
    def delete_donation(self):
        """Delete the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to delete")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this donation?"):
            return
        
        # Delete donation
        if self.db.delete_donation(donation_id, self.user_info['unique_id']):
            messagebox.showinfo("Success", "Donation deleted successfully")
            self.refresh_donations()
        else:
            messagebox.showerror("Error", "Failed to delete donation")
    
    def send_email_dialog(self):
        """Open dialog to send email"""
        # Get selected item
        selected_item = self.donations_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a donation to contact")
            return
        
        # Get email from selected row
        values = self.donations_tree.item(selected_item[0])['values']
        recipient_email = values[6]
        
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

    def refresh_donations(self, donations=None):
        """Populate the treeview with donations"""
        # Clear existing items
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
        
        if donations is None:
            donations = self.db.search_donations()
        
        # Add donations to treeview
        for donation in donations:
            item_id = self.donations_tree.insert('', 'end', values=(
                donation['unique_id'],
                donation['title'],
                donation['category'],
                donation['condition'],
                f"{donation['city']}, {donation['state']}",
                donation['donor_name'],
                donation['status'],
                donation['donor_email']
            ))
            # Store donation ID in the item
            self.donations_tree.set(item_id, 'unique_id', donation['unique_id'])
            
            # Show delete button if user is the donor
            selected_items = self.donations_tree.selection()
            if selected_items:
                donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
                if donation.get('donor_id') == self.user_info['unique_id']:
                    self.delete_btn.pack(side='left', padx=5)
                else:
                    self.delete_btn.pack_forget()
    
    def request_item(self, donation):
        """Send a request for the selected donation"""
        if not self.user_info:
            messagebox.showerror("Error", "Please log in to request items")
            return
            
        # Create request in database
        success, message = self.db.create_donation_request(
            donation_id=donation['unique_id'],
            requester_id=self.user_info['unique_id'],
            requester_name=self.user_info['full_name'],
            requester_email=self.user_info['email']
        )
        
        if success:
            # Send email notification to donor
            EmailValidator.send_communication_email(
                self.user_info['full_name'],
                self.user_info['email'],
                donation['donor_email'],
                "New Donation Request",
                f"A new request has been made for your donation: {donation['title']}"
            )
            messagebox.showinfo("Success", "Request sent successfully")
        else:
            messagebox.showerror("Error", message)
    
    def view_donation_details(self):
        """Display detailed information about the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to view")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        donation = self.db.get_donation_details(donation_id)
        
        if not donation:
            messagebox.showerror("Error", "Could not fetch donation details")
            return
        
        # Create details window with improved styling
        details_window = tk.Toplevel(self.frame)
        details_window.title("Donation Details")
        details_window.geometry("600x600")
        
        # Add details to window with enhanced layout
        content_frame = ttk.Frame(details_window, style='Card.TFrame', padding=25)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title with larger font and emphasis
        title_label = ttk.Label(content_frame, text=donation['title'], style='Title.TLabel', font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Information section with improved spacing and organization
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill='x', pady=(0, 20))
        
        # Left column
        left_frame = ttk.Frame(info_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(left_frame, text="Category", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['category']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Condition", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['condition']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Location", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=f"{donation['city']}, {donation['state']}").pack(anchor='w', pady=(0, 10))
        
        # Right column
        right_frame = ttk.Frame(info_frame)
        right_frame.pack(side='right', fill='x', expand=True)
        
        ttk.Label(right_frame, text="Donor", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_name']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Status", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['status']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Contact", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_email']).pack(anchor='w', pady=(0, 10))
        
        # Description section with improved visibility
        description_frame = ttk.LabelFrame(content_frame, text="Description", padding=15)
        description_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        description_text = tk.Text(description_frame, wrap='word', height=6, width=50, font=('Segoe UI', 10))
        description_text.insert('1.0', donation['description'])
        description_text.configure(state='disabled')
        description_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Request button (only visible if user is not the donor)
        if donation.get('donor_id') != self.user_info['unique_id'] and donation['status'] == 'available':
            ModernUI.create_button(
                button_frame,
                "Request Item",
                lambda: self.request_item(donation),
                style='Primary.TButton'
            ).pack(side='left', padx=5)
        
        # Close button
        ModernUI.create_button(
            button_frame,
            "Close",
            details_window.destroy,
            style='Secondary.TButton'
        ).pack(side='right', padx=5)
    
    def delete_donation(self):
        """Delete the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to delete")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this donation?"):
            return
        
        # Delete donation
        if self.db.delete_donation(donation_id, self.user_info['unique_id']):
            messagebox.showinfo("Success", "Donation deleted successfully")
            self.refresh_donations()
        else:
            messagebox.showerror("Error", "Failed to delete donation")
    
    def send_email_dialog(self):
        """Open dialog to send email"""
        # Get selected item
        selected_item = self.donations_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a donation to contact")
            return
        
        # Get email from selected row
        values = self.donations_tree.item(selected_item[0])['values']
        recipient_email = values[6]
        
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

    def refresh_donations(self, donations=None):
        """Populate the treeview with donations"""
        # Clear existing items
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
        
        if donations is None:
            donations = self.db.search_donations()
        
        # Add donations to treeview
        for donation in donations:
            item_id = self.donations_tree.insert('', 'end', values=(
                donation['unique_id'],
                donation['title'],
                donation['category'],
                donation['condition'],
                f"{donation['city']}, {donation['state']}",
                donation['donor_name'],
                donation['status'],
                donation['donor_email']
            ))
            # Store donation ID in the item
            self.donations_tree.set(item_id, 'unique_id', donation['unique_id'])
            
            # Show delete button if user is the donor
            selected_items = self.donations_tree.selection()
            if selected_items:
                donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
                if donation.get('donor_id') == self.user_info['unique_id']:
                    self.delete_btn.pack(side='left', padx=5)
                else:
                    self.delete_btn.pack_forget()
    
    def request_item(self, donation):
        """Send a request for the selected donation"""
        if not self.user_info:
            messagebox.showerror("Error", "Please log in to request items")
            return
            
        # Create request in database
        success, message = self.db.create_donation_request(
            donation_id=donation['unique_id'],
            requester_id=self.user_info['unique_id'],
            requester_name=self.user_info['full_name'],
            requester_email=self.user_info['email']
        )
        
        if success:
            # Send email notification to donor
            EmailValidator.send_communication_email(
                self.user_info['full_name'],
                self.user_info['email'],
                donation['donor_email'],
                "New Donation Request",
                f"A new request has been made for your donation: {donation['title']}"
            )
            messagebox.showinfo("Success", "Request sent successfully")
        else:
            messagebox.showerror("Error", message)
    
    def view_donation_details(self):
        """Display detailed information about the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to view")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        donation = self.db.get_donation_details(donation_id)
        
        if not donation:
            messagebox.showerror("Error", "Could not fetch donation details")
            return
        
        # Create details window with improved styling
        details_window = tk.Toplevel(self.frame)
        details_window.title("Donation Details")
        details_window.geometry("600x600")
        
        # Add details to window with enhanced layout
        content_frame = ttk.Frame(details_window, style='Card.TFrame', padding=25)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title with larger font and emphasis
        title_label = ttk.Label(content_frame, text=donation['title'], style='Title.TLabel', font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Information section with improved spacing and organization
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill='x', pady=(0, 20))
        
        # Left column
        left_frame = ttk.Frame(info_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(left_frame, text="Category", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['category']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Condition", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['condition']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Location", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=f"{donation['city']}, {donation['state']}").pack(anchor='w', pady=(0, 10))
        
        # Right column
        right_frame = ttk.Frame(info_frame)
        right_frame.pack(side='right', fill='x', expand=True)
        
        ttk.Label(right_frame, text="Donor", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_name']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Status", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['status']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Contact", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_email']).pack(anchor='w', pady=(0, 10))
        
        # Description section with improved visibility
        description_frame = ttk.LabelFrame(content_frame, text="Description", padding=15)
        description_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        description_text = tk.Text(description_frame, wrap='word', height=6, width=50, font=('Segoe UI', 10))
        description_text.insert('1.0', donation['description'])
        description_text.configure(state='disabled')
        description_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Request button (only visible if user is not the donor)
        if donation.get('donor_id') != self.user_info['unique_id'] and donation['status'] == 'available':
            ModernUI.create_button(
                button_frame,
                "Request Item",
                lambda: self.request_item(donation),
                style='Primary.TButton'
            ).pack(side='left', padx=5)
        
        # Close button
        ModernUI.create_button(
            button_frame,
            "Close",
            details_window.destroy,
            style='Secondary.TButton'
        ).pack(side='right', padx=5)
    
    def delete_donation(self):
        """Delete the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to delete")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this donation?"):
            return
        
        # Delete donation
        if self.db.delete_donation(donation_id, self.user_info['unique_id']):
            messagebox.showinfo("Success", "Donation deleted successfully")
            self.refresh_donations()
        else:
            messagebox.showerror("Error", "Failed to delete donation")
    
    def send_email_dialog(self):
        """Open dialog to send email"""
        # Get selected item
        selected_item = self.donations_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a donation to contact")
            return
        
        # Get email from selected row
        values = self.donations_tree.item(selected_item[0])['values']
        recipient_email = values[6]
        
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

    def refresh_donations(self, donations=None):
        """Populate the treeview with donations"""
        # Clear existing items
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
        
        if donations is None:
            donations = self.db.search_donations()
        
        # Add donations to treeview
        for donation in donations:
            item_id = self.donations_tree.insert('', 'end', values=(
                donation['unique_id'],
                donation['title'],
                donation['category'],
                donation['condition'],
                f"{donation['city']}, {donation['state']}",
                donation['donor_name'],
                donation['status'],
                donation['donor_email']
            ))
            # Store donation ID in the item
            self.donations_tree.set(item_id, 'unique_id', donation['unique_id'])
            
            # Show delete button if user is the donor
            selected_items = self.donations_tree.selection()
            if selected_items:
                donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
                if donation.get('donor_id') == self.user_info['unique_id']:
                    self.delete_btn.pack(side='left', padx=5)
                else:
                    self.delete_btn.pack_forget()
    
    def request_item(self, donation):
        """Send a request for the selected donation"""
        if not self.user_info:
            messagebox.showerror("Error", "Please log in to request items")
            return
            
        # Create request in database
        success, message = self.db.create_donation_request(
            donation_id=donation['unique_id'],
            requester_id=self.user_info['unique_id'],
            requester_name=self.user_info['full_name'],
            requester_email=self.user_info['email']
        )
        
        if success:
            # Send email notification to donor
            EmailValidator.send_communication_email(
                self.user_info['full_name'],
                self.user_info['email'],
                donation['donor_email'],
                "New Donation Request",
                f"A new request has been made for your donation: {donation['title']}"
            )
            messagebox.showinfo("Success", "Request sent successfully")
        else:
            messagebox.showerror("Error", message)
    
    def view_donation_details(self):
        """Display detailed information about the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to view")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        donation = self.db.get_donation_details(donation_id)
        
        if not donation:
            messagebox.showerror("Error", "Could not fetch donation details")
            return
        
        # Create details window with improved styling
        details_window = tk.Toplevel(self.frame)
        details_window.title("Donation Details")
        details_window.geometry("600x600")
        
        # Add details to window with enhanced layout
        content_frame = ttk.Frame(details_window, style='Card.TFrame', padding=25)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title with larger font and emphasis
        title_label = ttk.Label(content_frame, text=donation['title'], style='Title.TLabel', font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Information section with improved spacing and organization
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill='x', pady=(0, 20))
        
        # Left column
        left_frame = ttk.Frame(info_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(left_frame, text="Category", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['category']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Condition", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['condition']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Location", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=f"{donation['city']}, {donation['state']}").pack(anchor='w', pady=(0, 10))
        
        # Right column
        right_frame = ttk.Frame(info_frame)
        right_frame.pack(side='right', fill='x', expand=True)
        
        ttk.Label(right_frame, text="Donor", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_name']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Status", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['status']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Contact", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_email']).pack(anchor='w', pady=(0, 10))
        
        # Description section with improved visibility
        description_frame = ttk.LabelFrame(content_frame, text="Description", padding=15)
        description_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        description_text = tk.Text(description_frame, wrap='word', height=6, width=50, font=('Segoe UI', 10))
        description_text.insert('1.0', donation['description'])
        description_text.configure(state='disabled')
        description_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Request button (only visible if user is not the donor)
        if donation.get('donor_id') != self.user_info['unique_id'] and donation['status'] == 'available':
            ModernUI.create_button(
                button_frame,
                "Request Item",
                lambda: self.request_item(donation),
                style='Primary.TButton'
            ).pack(side='left', padx=5)
        
        # Close button
        ModernUI.create_button(
            button_frame,
            "Close",
            details_window.destroy,
            style='Secondary.TButton'
        ).pack(side='right', padx=5)
    
    def delete_donation(self):
        """Delete the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to delete")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this donation?"):
            return
        
        # Delete donation
        if self.db.delete_donation(donation_id, self.user_info['unique_id']):
            messagebox.showinfo("Success", "Donation deleted successfully")
            self.refresh_donations()
        else:
            messagebox.showerror("Error", "Failed to delete donation")
    
    def send_email_dialog(self):
        """Open dialog to send email"""
        # Get selected item
        selected_item = self.donations_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a donation to contact")
            return
        
        # Get email from selected row
        values = self.donations_tree.item(selected_item[0])['values']
        recipient_email = values[6]
        
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

    def refresh_donations(self, donations=None):
        """Populate the treeview with donations"""
        # Clear existing items
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
        
        if donations is None:
            donations = self.db.search_donations()
        
        # Add donations to treeview
        for donation in donations:
            item_id = self.donations_tree.insert('', 'end', values=(
                donation['unique_id'],
                donation['title'],
                donation['category'],
                donation['condition'],
                f"{donation['city']}, {donation['state']}",
                donation['donor_name'],
                donation['status'],
                donation['donor_email']
            ))
            # Store donation ID in the item
            self.donations_tree.set(item_id, 'unique_id', donation['unique_id'])
            
            # Show delete button if user is the donor
            selected_items = self.donations_tree.selection()
            if selected_items:
                donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
                if donation.get('donor_id') == self.user_info['unique_id']:
                    self.delete_btn.pack(side='left', padx=5)
                else:
                    self.delete_btn.pack_forget()
    
    def request_item(self, donation):
        """Send a request for the selected donation"""
        if not self.user_info:
            messagebox.showerror("Error", "Please log in to request items")
            return
            
        # Create request in database
        success, message = self.db.create_donation_request(
            donation_id=donation['unique_id'],
            requester_id=self.user_info['unique_id'],
            requester_name=self.user_info['full_name'],
            requester_email=self.user_info['email']
        )
        
        if success:
            # Send email notification to donor
            EmailValidator.send_communication_email(
                self.user_info['full_name'],
                self.user_info['email'],
                donation['donor_email'],
                "New Donation Request",
                f"A new request has been made for your donation: {donation['title']}"
            )
            messagebox.showinfo("Success", "Request sent successfully")
        else:
            messagebox.showerror("Error", message)
    
    def view_donation_details(self):
        """Display detailed information about the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to view")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        donation = self.db.get_donation_details(donation_id)
        
        if not donation:
            messagebox.showerror("Error", "Could not fetch donation details")
            return
        
        # Create details window with improved styling
        details_window = tk.Toplevel(self.frame)
        details_window.title("Donation Details")
        details_window.geometry("600x600")
        
        # Add details to window with enhanced layout
        content_frame = ttk.Frame(details_window, style='Card.TFrame', padding=25)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title with larger font and emphasis
        title_label = ttk.Label(content_frame, text=donation['title'], style='Title.TLabel', font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Information section with improved spacing and organization
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill='x', pady=(0, 20))
        
        # Left column
        left_frame = ttk.Frame(info_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(left_frame, text="Category", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['category']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Condition", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['condition']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Location", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=f"{donation['city']}, {donation['state']}").pack(anchor='w', pady=(0, 10))
        
        # Right column
        right_frame = ttk.Frame(info_frame)
        right_frame.pack(side='right', fill='x', expand=True)
        
        ttk.Label(right_frame, text="Donor", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_name']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Status", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['status']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Contact", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_email']).pack(anchor='w', pady=(0, 10))
        
        # Description section with improved visibility
        description_frame = ttk.LabelFrame(content_frame, text="Description", padding=15)
        description_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        description_text = tk.Text(description_frame, wrap='word', height=6, width=50, font=('Segoe UI', 10))
        description_text.insert('1.0', donation['description'])
        description_text.configure(state='disabled')
        description_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Request button (only visible if user is not the donor)
        if donation.get('donor_id') != self.user_info['unique_id'] and donation['status'] == 'available':
            ModernUI.create_button(
                button_frame,
                "Request Item",
                lambda: self.request_item(donation),
                style='Primary.TButton'
            ).pack(side='left', padx=5)
        
        # Close button
        ModernUI.create_button(
            button_frame,
            "Close",
            details_window.destroy,
            style='Secondary.TButton'
        ).pack(side='right', padx=5)
    
    def delete_donation(self):
        """Delete the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to delete")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this donation?"):
            return
        
        # Delete donation
        if self.db.delete_donation(donation_id, self.user_info['unique_id']):
            messagebox.showinfo("Success", "Donation deleted successfully")
            self.refresh_donations()
        else:
            messagebox.showerror("Error", "Failed to delete donation")
    
    def send_email_dialog(self):
        """Open dialog to send email"""
        # Get selected item
        selected_item = self.donations_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a donation to contact")
            return
        
        # Get email from selected row
        values = self.donations_tree.item(selected_item[0])['values']
        recipient_email = values[6]
        
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

    def refresh_donations(self, donations=None):
        """Populate the treeview with donations"""
        # Clear existing items
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
        
        if donations is None:
            donations = self.db.search_donations()
        
        # Add donations to treeview
        for donation in donations:
            item_id = self.donations_tree.insert('', 'end', values=(
                donation['unique_id'],
                donation['title'],
                donation['category'],
                donation['condition'],
                f"{donation['city']}, {donation['state']}",
                donation['donor_name'],
                donation['status'],
                donation['donor_email']
            ))
            # Store donation ID in the item
            self.donations_tree.set(item_id, 'unique_id', donation['unique_id'])
            
            # Show delete button if user is the donor
            selected_items = self.donations_tree.selection()
            if selected_items:
                donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
                if donation.get('donor_id') == self.user_info['unique_id']:
                    self.delete_btn.pack(side='left', padx=5)
                else:
                    self.delete_btn.pack_forget()
    
    def request_item(self, donation):
        """Send a request for the selected donation"""
        if not self.user_info:
            messagebox.showerror("Error", "Please log in to request items")
            return
            
        # Create request in database
        success, message = self.db.create_donation_request(
            donation_id=donation['unique_id'],
            requester_id=self.user_info['unique_id'],
            requester_name=self.user_info['full_name'],
            requester_email=self.user_info['email']
        )
        
        if success:
            # Send email notification to donor
            EmailValidator.send_communication_email(
                self.user_info['full_name'],
                self.user_info['email'],
                donation['donor_email'],
                "New Donation Request",
                f"A new request has been made for your donation: {donation['title']}"
            )
            messagebox.showinfo("Success", "Request sent successfully")
        else:
            messagebox.showerror("Error", message)
    
    def view_donation_details(self):
        """Display detailed information about the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to view")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        donation = self.db.get_donation_details(donation_id)
        
        if not donation:
            messagebox.showerror("Error", "Could not fetch donation details")
            return
        
        # Create details window with improved styling
        details_window = tk.Toplevel(self.frame)
        details_window.title("Donation Details")
        details_window.geometry("600x600")
        
        # Add details to window with enhanced layout
        content_frame = ttk.Frame(details_window, style='Card.TFrame', padding=25)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title with larger font and emphasis
        title_label = ttk.Label(content_frame, text=donation['title'], style='Title.TLabel', font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Information section with improved spacing and organization
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill='x', pady=(0, 20))
        
        # Left column
        left_frame = ttk.Frame(info_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(left_frame, text="Category", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['category']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Condition", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['condition']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Location", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=f"{donation['city']}, {donation['state']}").pack(anchor='w', pady=(0, 10))
        
        # Right column
        right_frame = ttk.Frame(info_frame)
        right_frame.pack(side='right', fill='x', expand=True)
        
        ttk.Label(right_frame, text="Donor", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_name']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Status", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['status']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Contact", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_email']).pack(anchor='w', pady=(0, 10))
        
        # Description section with improved visibility
        description_frame = ttk.LabelFrame(content_frame, text="Description", padding=15)
        description_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        description_text = tk.Text(description_frame, wrap='word', height=6, width=50, font=('Segoe UI', 10))
        description_text.insert('1.0', donation['description'])
        description_text.configure(state='disabled')
        description_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Request button (only visible if user is not the donor)
        if donation.get('donor_id') != self.user_info['unique_id'] and donation['status'] == 'available':
            ModernUI.create_button(
                button_frame,
                "Request Item",
                lambda: self.request_item(donation),
                style='Primary.TButton'
            ).pack(side='left', padx=5)
        
        # Close button
        ModernUI.create_button(
            button_frame,
            "Close",
            details_window.destroy,
            style='Secondary.TButton'
        ).pack(side='right', padx=5)
    
    def delete_donation(self):
        """Delete the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to delete")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this donation?"):
            return
        
        # Delete donation
        if self.db.delete_donation(donation_id, self.user_info['unique_id']):
            messagebox.showinfo("Success", "Donation deleted successfully")
            self.refresh_donations()
        else:
            messagebox.showerror("Error", "Failed to delete donation")
    
    def send_email_dialog(self):
        """Open dialog to send email"""
        # Get selected item
        selected_item = self.donations_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a donation to contact")
            return
        
        # Get email from selected row
        values = self.donations_tree.item(selected_item[0])['values']
        recipient_email = values[6]
        
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

    def refresh_donations(self, donations=None):
        """Populate the treeview with donations"""
        # Clear existing items
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
        
        if donations is None:
            donations = self.db.search_donations()
        
        # Add donations to treeview
        for donation in donations:
            item_id = self.donations_tree.insert('', 'end', values=(
                donation['unique_id'],
                donation['title'],
                donation['category'],
                donation['condition'],
                f"{donation['city']}, {donation['state']}",
                donation['donor_name'],
                donation['status'],
                donation['donor_email']
            ))
            # Store donation ID in the item
            self.donations_tree.set(item_id, 'unique_id', donation['unique_id'])
            
            # Show delete button if user is the donor
            selected_items = self.donations_tree.selection()
            if selected_items:
                donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
                if donation.get('donor_id') == self.user_info['unique_id']:
                    self.delete_btn.pack(side='left', padx=5)
                else:
                    self.delete_btn.pack_forget()
    
    def request_item(self, donation):
        """Send a request for the selected donation"""
        if not self.user_info:
            messagebox.showerror("Error", "Please log in to request items")
            return
            
        # Create request in database
        success, message = self.db.create_donation_request(
            donation_id=donation['unique_id'],
            requester_id=self.user_info['unique_id'],
            requester_name=self.user_info['full_name'],
            requester_email=self.user_info['email']
        )
        
        if success:
            # Send email notification to donor
            EmailValidator.send_communication_email(
                self.user_info['full_name'],
                self.user_info['email'],
                donation['donor_email'],
                "New Donation Request",
                f"A new request has been made for your donation: {donation['title']}"
            )
            messagebox.showinfo("Success", "Request sent successfully")
        else:
            messagebox.showerror("Error", message)
    
    def view_donation_details(self):
        """Display detailed information about the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to view")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        donation = self.db.get_donation_details(donation_id)
        
        if not donation:
            messagebox.showerror("Error", "Could not fetch donation details")
            return
        
        # Create details window with improved styling
        details_window = tk.Toplevel(self.frame)
        details_window.title("Donation Details")
        details_window.geometry("600x600")
        
        # Add details to window with enhanced layout
        content_frame = ttk.Frame(details_window, style='Card.TFrame', padding=25)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title with larger font and emphasis
        title_label = ttk.Label(content_frame, text=donation['title'], style='Title.TLabel', font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Information section with improved spacing and organization
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill='x', pady=(0, 20))
        
        # Left column
        left_frame = ttk.Frame(info_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(left_frame, text="Category", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['category']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Condition", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=donation['condition']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(left_frame, text="Location", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(left_frame, text=f"{donation['city']}, {donation['state']}").pack(anchor='w', pady=(0, 10))
        
        # Right column
        right_frame = ttk.Frame(info_frame)
        right_frame.pack(side='right', fill='x', expand=True)
        
        ttk.Label(right_frame, text="Donor", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_name']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Status", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['status']).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(right_frame, text="Contact", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        ttk.Label(right_frame, text=donation['donor_email']).pack(anchor='w', pady=(0, 10))
        
        # Description section with improved visibility
        description_frame = ttk.LabelFrame(content_frame, text="Description", padding=15)
        description_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        description_text = tk.Text(description_frame, wrap='word', height=6, width=50, font=('Segoe UI', 10))
        description_text.insert('1.0', donation['description'])
        description_text.configure(state='disabled')
        description_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Request button (only visible if user is not the donor)
        if donation.get('donor_id') != self.user_info['unique_id'] and donation['status'] == 'available':
            ModernUI.create_button(
                button_frame,
                "Request Item",
                lambda: self.request_item(donation),
                style='Primary.TButton'
            ).pack(side='left', padx=5)
        
        # Close button
        ModernUI.create_button(
            button_frame,
            "Close",
            details_window.destroy,
            style='Secondary.TButton'
        ).pack(side='right', padx=5)
    
    def delete_donation(self):
        """Delete the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to delete")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this donation?"):
            return
        
        # Delete donation
        if self.db.delete_donation(donation_id, self.user_info['unique_id']):
            messagebox.showinfo("Success", "Donation deleted successfully")
            self.refresh_donations()
        else:
            messagebox.showerror("Error", "Failed to delete donation")
    
    def send_email_dialog(self):
        """Open dialog to send email"""
        # Get selected item
        selected_item = self.donations_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a donation to contact")
            return
        
        # Get email from selected row
        values = self.donations_tree.item(selected_item[0])['values']
        recipient_email = values[6]
        
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

    def refresh_donations(self, donations=None):
        """Populate the treeview with donations"""
        # Clear existing items
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
        
        if donations is None:
            donations = self.db.search_donations()
        
        # Add donations to treeview
        for donation in donations:
            item_id = self.donations_tree.insert('', 'end', values=(
                donation['unique_id'],
                donation['title'],
                donation['category'],
                donation['condition'],
                f"{donation['city']}, {donation['state']}",
                donation['donor_name'],
                donation['status'],
                donation['donor_email']
            ))
            # Store donation ID in the item
            self.donations_tree.set(item_id, 'unique_id', donation['unique_id'])
            
            # Show delete button if user is the donor
            selected_items = self.donations_tree.selection()
            if selected_items:
                donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
                if donation.get('donor_id') == self.user_info['unique_id']:
                    self.delete_btn.pack(side='left', padx=5)
                else:
                    self.delete_btn.pack_forget()
    
    def request_item(self, donation):
        """Send a request for the selected donation"""
        if not self.user_info:
            messagebox.showerror("Error", "Please log in to request items")
            return
            
        # Create request in database
        success, message = self.db.create_donation_request(
            donation_id=donation['unique_id'],
            requester_id=self.user_info['unique_id'],
            requester_name=self.user_info['full_name'],
            requester_email=self.user_info['email']
        )
        
        if success:
            # Send email notification to donor
            EmailValidator.send_communication_email(
                self.user_info['full_name'],
                self.user_info['email'],
                donation['donor_email'],
                "New Donation Request",
                f"A new request has been made for your donation: {donation['title']}"
            )
            messagebox.showinfo("Success", "Request sent successfully")
        else:
            messagebox.showerror("Error", message)
    
    def view_donation_details(self):
        """Display detailed information about the selected donation"""
        selected_items = self.donations_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a donation to view")
            return
        
        donation_id = self.donations_tree.set(selected_items[0], 'unique_id')
        donation = self.db.get_donation_details(donation_id)
        
        if not donation:
            messagebox.showerror("Error", "Could not fetch donation details")
            return
        
        # Create details window
        details_window = tk.Toplevel(self.frame)
        details_window.title("Donation Details")
        details_window.geometry("500x400")
        
        # Add details to window
        content_frame = ttk.Frame(details_window, padding=20)
        content_frame.pack(fill='both', expand=True)
        
        ttk.Label(content_frame, text=donation['title'], style='Title.TLabel').pack(pady=(0, 10))
        ttk.Label(content_frame, text=f"Category: {donation['category']}").pack(anchor='w')
        ttk