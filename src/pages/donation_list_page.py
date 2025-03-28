import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from src.ui.modern_ui import ModernUI
from src.utils.email_validator import EmailValidator
from src.constants import COLORS, CATEGORIES, CONDITIONS, LOCATIONS, STATES
from src.database.database_handler import DatabaseHandler
import os
from PIL import Image, ImageTk
import io

class DonationListPage:
    def __init__(self, parent, user_info, show_frame_callback):
        """Initialize the donation list page"""
        self.parent = parent
        self.user_info = user_info
        self.show_frame = show_frame_callback
        self.db = DatabaseHandler()
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create and pack components
        self._create_header()
        self._create_search_area()
        self._create_donations_table()
        self._create_action_buttons()
        
        # Load initial donations
        self.refresh_donations()

    def _create_header(self):
        """Create page header"""
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', pady=10)
        
        # Title
        ttk.Label(
            header_frame, 
            text="Available Donations", 
            font=('Segoe UI', 16, 'bold')
        ).pack(side='left', padx=20)
        
        # User greeting
        ttk.Label(
            header_frame, 
            text=f"Welcome, {self.user_info.get('name', 'Donor')}!", 
            font=('Segoe UI', 12)
        ).pack(side='right', padx=20)

    def _create_search_area(self):
        """Create search and filter components"""
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill='x', pady=10, padx=20)
        
        # Search entry
        self.search_var = tk.StringVar()
        ttk.Label(search_frame, text="Search:").pack(side='left')
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=10)
        
        # Category dropdown
        self.category_var = tk.StringVar()
        ttk.Label(search_frame, text="Category:").pack(side='left')
        category_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.category_var, 
            values=['All Categories'] + list(CATEGORIES), 
            width=20
        )
        category_combo.pack(side='left', padx=10)
        category_combo.set('All Categories')
        
        # Location dropdown
        self.location_var = tk.StringVar()
        ttk.Label(search_frame, text="Location:").pack(side='left')
        location_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.location_var, 
            values=['All Locations'] + list(STATES.keys()), 
            width=20
        )
        location_combo.pack(side='left', padx=10)
        location_combo.set('All Locations')
        
        # Search button
        ttk.Button(
            search_frame, 
            text="Search", 
            command=self.search_donations
        ).pack(side='left', padx=10)

        # Clear filters button
        ttk.Button(
            search_frame, 
            text="Clear Filters", 
            command=self.clear_filters
        ).pack(side='left', padx=10)

    def _create_donations_table(self):
        """Create treeview for donations"""
        # Donations table frame
        donations_frame = ttk.Frame(self.frame)
        donations_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Create treeview
        self.donations_tree = ttk.Treeview(
            donations_frame, 
            columns=(
                'ID', 
                'Title', 
                'Category', 
                'Description', 
                'Quantity', 
                'Status'
            ), 
            show='headings'
        )
        
        # Configure column headings
        for col in self.donations_tree['columns']:
            self.donations_tree.heading(col, text=col)
            self.donations_tree.column(col, width=100, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            donations_frame, 
            orient='vertical', 
            command=self.donations_tree.yview
        )
        self.donations_tree.configure(yscroll=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.donations_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind double-click event to view details
        self.donations_tree.bind('<Double-1>', self.view_donation_details)
        
        # Refresh button
        refresh_btn = ttk.Button(
            donations_frame, 
            text="Refresh", 
            command=self.refresh_donations
        )
        refresh_btn.pack(side='bottom', padx=5, pady=5)

    def _create_action_buttons(self):
        """Create action buttons for the donations table"""
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill='x', pady=10, padx=20)
        
        # View Details button
        ModernUI.create_button(
            action_frame,
            "View Details", 
            self.view_donation_details_btn,
            style='Primary.TButton'
        ).pack(side='left', padx=5)
        
        # Contact Donor button
        ModernUI.create_button(
            action_frame,
            "Contact Donor", 
            self.contact_donor,
            style='Secondary.TButton'
        ).pack(side='left', padx=5)
        
        # Delete Donation button (only for donors)
        if self.user_info.get('role') == 'donor':
            ModernUI.create_button(
                action_frame,
                "Delete Donation", 
                self.delete_donation,
                style='Danger.TButton'
            ).pack(side='left', padx=5)
        
        # Back to Dashboard button
        ModernUI.create_button(
            action_frame,
            "Back to Dashboard", 
            lambda: self.show_frame('dashboard'),
            style='Neutral.TButton'
        ).pack(side='right', padx=5)

    def refresh_donations(self, donations=None):
        """Refresh donations in treeview"""
        # Clear existing items
        for i in self.donations_tree.get_children():
            self.donations_tree.delete(i)
        
        # Fetch donations if not provided
        if donations is None:
            donations = self.db.search_donations()
        
        # Debug: print donations type and first item
        print("Donations type:", type(donations))
        if donations:
            print("First donation type:", type(donations[0]))
            print("First donation keys:", list(donations[0].keys()) if isinstance(donations[0], dict) else "Not a dictionary")
        
        # Populate treeview
        for donation in donations:
            # Debug: check donation type
            if not isinstance(donation, dict):
                print("WARNING: Donation is not a dictionary:", type(donation))
                continue
            
            self.donations_tree.insert('', 'end', values=(
                donation.get('title', ''),
                donation.get('category', ''),
                donation.get('condition', ''),
                f"{donation.get('city', '')}, {donation.get('state', '')}",
                donation.get('donor_name', '')
            ))

    def copy_to_clipboard(self, text):
        """Copy text to clipboard and show feedback"""
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        self.parent.update()
        
        # Show feedback tooltip
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry("+%d+%d" % (self.parent.winfo_pointerx(), self.parent.winfo_pointery()))
        
        label = ttk.Label(tooltip, text="Email copied!", padding=5, background='#4CAF50', foreground='white')
        label.pack()
        
        # Auto-close tooltip after 1.5 seconds
        self.parent.after(1500, tooltip.destroy)

    def update_cities(self, event=None):
        """Update city dropdown based on selected state"""
        selected_state = self.state_var.get()
        if selected_state and selected_state != 'All Locations':
            cities = STATES.get(selected_state, [])
            self.city_combo['values'] = ['All Cities'] + cities
            self.city_combo.set('All Cities')
        else:
            self.city_combo['values'] = []
            self.city_combo.set('')

    def clear_filters(self):
        """Clear all search filters and reset donations view"""
        # Reset search variables
        self.search_var.set('')
        self.category_var.set('All Categories')
        self.location_var.set('All Locations')

        # Refresh donations to show all
        self.refresh_donations()

    def search_donations(self):
        """Search and filter donations based on user input"""
        # Get search parameters
        search_query = self.search_var.get().strip()
        category = self.category_var.get()
        location = self.location_var.get()

        # Prepare filter conditions
        filter_conditions = {}
        
        # Add search query filter
        if search_query:
            filter_conditions['search_query'] = search_query

        # Add category filter
        if category and category != 'All Categories':
            filter_conditions['category'] = category

        # Add location filter
        if location and location != 'All Locations':
            filter_conditions['location'] = location

        # Fetch filtered donations
        try:
            # Fetch donations based on filter conditions
            filtered_donations = self.db.search_donations(**filter_conditions)
            
            # Refresh donations treeview
            self.refresh_donations(filtered_donations)
            
            # Optional: Show message if no donations found
            if not filtered_donations:
                messagebox.showinfo("Search Results", "No donations found matching your criteria.")
        
        except Exception as e:
            messagebox.showerror("Search Error", f"An error occurred while searching: {e}")

    def view_donation_details_btn(self):
        """
        View donation details when button is clicked
        Handles multiple selection scenarios
        """
        # Get selected item
        selected_item = self.donations_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a donation to view details.")
            return
        
        # Get the first selected item
        item = selected_item[0]
        
        # Get donation details from the selected row
        donation_details = self.donations_tree.item(item, 'values')
        
        if not donation_details or len(donation_details) < 1:
            messagebox.showerror("Invalid Selection", "Unable to retrieve donation details from treeview.")
            return
        
        # Assuming the first column is the unique ID
        donation_id = donation_details[0]
        
        # Verify donation exists and is valid
        try:
            # Fetch donation details from database
            donation = self.db.get_donation_details(donation_id)
            
            if not donation:
                messagebox.showerror("Invalid Donation", f"No details found for donation ID: {donation_id}")
                return
            
            # Create a details window
            details_window = tk.Toplevel(self.frame)
            details_window.title(f"Donation Details - {donation.get('title', 'N/A')}")
            details_window.geometry("800x600")
            
            # Main container
            main_frame = ttk.Frame(details_window, padding="20 20 20 20")
            main_frame.pack(fill='both', expand=True)
            
            # Create two columns
            left_frame = ttk.Frame(main_frame)
            left_frame.pack(side='left', fill='both', expand=True, padx=10)
            
            right_frame = ttk.Frame(main_frame)
            right_frame.pack(side='right', fill='both', expand=True, padx=10)
            
            # Donation Image
            image_data = donation.get('image_data')
            image_type = donation.get('image_type')
            if image_data:
                try:
                    # Convert bytes to image
                    image_stream = io.BytesIO(image_data)
                    original_image = Image.open(image_stream)
                    resized_image = original_image.resize((400, 400), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_image)
                    
                    # Display image
                    image_label = ttk.Label(left_frame, image=photo)
                    image_label.image = photo  # Keep a reference
                    image_label.pack(pady=20)
                except Exception as img_err:
                    print(f"Error loading image: {img_err}")
                    messagebox.showwarning("Image Error", "Could not load donation image.")
            elif donation.get('image_path') and os.path.exists(donation.get('image_path', '')):
                # Fallback to old image path method
                try:
                    original_image = Image.open(donation['image_path'])
                    resized_image = original_image.resize((400, 400), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_image)
                    
                    # Display image
                    image_label = ttk.Label(left_frame, image=photo)
                    image_label.image = photo  # Keep a reference
                    image_label.pack(pady=20)
                except Exception as img_err:
                    print(f"Error loading image: {img_err}")
            
            # Donation Details
            details = [
                ("Donation ID", donation.get('unique_id', 'N/A')),
                ("Title", donation.get('title', 'N/A')),
                ("Description", donation.get('description', 'N/A')),
                ("Category", donation.get('category', 'N/A')),
                ("Condition", donation.get('condition', 'N/A')),
                ("Location", f"{donation.get('city', 'N/A')}, {donation.get('state', 'N/A')}"),
                ("Status", donation.get('status', 'N/A')),
                ("Created At", str(donation.get('created_at', 'N/A'))),
                ("Donor Name", donation.get('donor_name', 'N/A')),
                ("Donor Email", donation.get('donor_email', 'N/A'))
            ]
            
            # Display details in right frame
            for label_text, value in details:
                detail_frame = ttk.Frame(right_frame)
                detail_frame.pack(fill='x', pady=5)
                
                label = ttk.Label(detail_frame, text=f"{label_text}:", font=('Segoe UI', 10, 'bold'), width=15)
                label.pack(side='left', anchor='w')
                
                value_label = ttk.Label(
                    detail_frame, 
                    text=value, 
                    font=('Segoe UI', 10), 
                    wraplength=300,
                    justify='left'
                )
                value_label.pack(side='left', anchor='w')
            
            # Action buttons frame
            action_frame = ttk.Frame(details_window)
            action_frame.pack(fill='x', pady=10, padx=20)
            
            # Close Button
            ttk.Button(
                action_frame, 
                text="Close", 
                command=details_window.destroy
            ).pack(side='right', padx=5)
        
        except Exception as e:
            print(f"Error creating donation details window: {e}")
            messagebox.showerror("Error", f"Could not display donation details: {e}")

    def view_donation_details(self, event=None):
        """
        View donation details on double-click or button press
        Handles both treeview events and button clicks
        """
        # Determine the selected item
        if event:
            # Double-click event
            selected_item = self.donations_tree.identify_row(event.y)
            if not selected_item:
                return
        else:
            # Button click
            selected_item = self.donations_tree.selection()
            if not selected_item:
                messagebox.showwarning("Selection Error", "Please select a donation to view details.")
                return
            selected_item = selected_item[0]
        
        # Get donation details from the selected row
        donation_details = self.donations_tree.item(selected_item, 'values')
        
        if not donation_details or len(donation_details) < 1:
            messagebox.showerror("Invalid Selection", "Unable to retrieve donation details.")
            return
        
        # Assuming the first column is the unique ID
        donation_id = donation_details[0]
        
        # Open donation details view
        if hasattr(self, 'parent') and hasattr(self.parent, 'show_donation_details'):
            # If there's a specific method for showing donation details
            self.parent.show_donation_details(donation_id)
        elif hasattr(self, 'show_frame'):
            # If show_frame is a method of the parent or current object
            try:
                self.show_frame('donation_details', donation_id)
            except TypeError:
                # Fallback to creating a details window
                self._create_donation_details_window(donation_id)
        else:
            # Fallback to creating a details window
            self._create_donation_details_window(donation_id)
    
    def _create_donation_details_window(self, donation_id):
        """
        Create a standalone details window when show_frame is not available
        """
        try:
            # Fetch donation details from database
            donation = self.db.get_donation_details(donation_id)
            
            if not donation:
                messagebox.showerror("Error", f"Donation with ID {donation_id} not found.")
                return
            
            # Create details window
            details_window = tk.Toplevel(self.frame)
            details_window.title(f"Donation Details - {donation.get('title', 'N/A')}")
            details_window.geometry("600x500")
            
            # Main container
            main_frame = ttk.Frame(details_window, padding="20 20 20 20")
            main_frame.pack(fill='both', expand=True)
            
            # Create two columns
            left_frame = ttk.Frame(main_frame)
            left_frame.pack(side='left', fill='both', expand=True, padx=10)
            
            right_frame = ttk.Frame(main_frame)
            right_frame.pack(side='right', fill='both', expand=True, padx=10)
            
            # Donation Image
            image_data = donation.get('image_data')
            image_type = donation.get('image_type')
            if image_data:
                try:
                    # Convert bytes to image
                    image_stream = io.BytesIO(image_data)
                    original_image = Image.open(image_stream)
                    resized_image = original_image.resize((400, 400), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_image)
                    
                    # Display image
                    image_label = ttk.Label(left_frame, image=photo)
                    image_label.image = photo  # Keep a reference
                    image_label.pack(pady=20)
                except Exception as img_err:
                    print(f"Error loading image: {img_err}")
            elif donation.get('image_path') and os.path.exists(donation.get('image_path', '')):
                # Fallback to old image path method
                try:
                    original_image = Image.open(donation['image_path'])
                    resized_image = original_image.resize((400, 400), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_image)
                    
                    # Display image
                    image_label = ttk.Label(left_frame, image=photo)
                    image_label.image = photo  # Keep a reference
                    image_label.pack(pady=20)
                except Exception as img_err:
                    print(f"Error loading image: {img_err}")
            
            # Donation Details
            details = [
                ("Title", donation.get('title', 'N/A')),
                ("Description", donation.get('description', 'N/A')),
                ("Category", donation.get('category', 'N/A')),
                ("Condition", donation.get('condition', 'N/A')),
                ("Location", f"{donation.get('city', 'N/A')}, {donation.get('state', 'N/A')}"),
                ("Status", donation.get('status', 'N/A')),
                ("Donor Name", donation.get('donor_name', 'N/A')),
                ("Donor Email", donation.get('donor_email', 'N/A')),
                ("Created At", str(donation.get('created_at', 'N/A')))
            ]
            
            # Display details in right frame
            for label_text, value in details:
                detail_frame = ttk.Frame(right_frame)
                detail_frame.pack(fill='x', pady=5)
                
                label = ttk.Label(detail_frame, text=f"{label_text}:", font=('Segoe UI', 10, 'bold'), width=15)
                label.pack(side='left', anchor='w')
                
                value_label = ttk.Label(
                    detail_frame, 
                    text=value, 
                    font=('Segoe UI', 10), 
                    wraplength=300,
                    justify='left'
                )
                value_label.pack(side='left', anchor='w')
            
            # Action buttons frame
            action_frame = ttk.Frame(details_window)
            action_frame.pack(fill='x', pady=10, padx=20)
            
            # Close Button
            ttk.Button(
                action_frame, 
                text="Close", 
                command=details_window.destroy
            ).pack(side='right', padx=5)
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not create donation details window: {e}")

    def contact_donor(self):
        """
        Contact the donor of a selected donation
        """
        # Get selected item
        selected_item = self.donations_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a donation to contact the donor.")
            return
        
        # Get the first selected item
        item = selected_item[0]
        
        # Get donation details from the selected row
        donation_details = self.donations_tree.item(item, 'values')
        
        if not donation_details or len(donation_details) < 1:
            messagebox.showerror("Invalid Selection", "Unable to retrieve donation details.")
            return
        
        # Assuming the first column is the unique ID
        donation_id = donation_details[0]
        
        # Verify donation exists
        try:
            # Fetch donation details including donor information
            donation = self.db.get_donation_details(donation_id)
            
            if not donation:
                messagebox.showerror("Invalid Donation", "Unable to find donation details.")
                return
            
            # Check donation status
            status, status_message = self.db.get_donation_status(donation_id)
            if status == 'withdrawn':
                messagebox.showinfo("Donation Unavailable", "This donation has been withdrawn.")
                return
            
            # Get donor contact information
            donor_email = donation.get('donor_email')
            donor_name = donation.get('donor_name')
            
            if not donor_email:
                messagebox.showerror("Contact Error", "Donor contact information not available.")
                return
            
            # Open email composition dialog
            subject = f"Inquiry about Donation: {donation.get('title', 'Untitled Donation')}"
            default_message = f"Hello {donor_name},\n\nI am interested in the donation: {donation.get('title', 'Untitled Donation')}.\n\nCould you provide more information?\n\nBest regards,\n{self.user_info.get('name', 'Potential Recipient')}"
            
            # Use simpledialog to allow user to edit message
            message = simpledialog.askstring(
                "Contact Donor", 
                "Edit your message:", 
                initialvalue=default_message,
                parent=self.frame
            )
            
            if message:
                # Send email or trigger email sending mechanism
                try:
                    email_sent = self.db.send_donor_contact_email(
                        sender_id=self.user_info['unique_id'],
                        recipient_email=donor_email,
                        subject=subject,
                        message=message
                    )
                    
                    if email_sent:
                        messagebox.showinfo("Email Sent", "Your message has been sent to the donor.")
                    else:
                        messagebox.showerror("Email Error", "Failed to send email. Please try again later or contact support.")
                
                except Exception as email_err:
                    messagebox.showerror("Email Error", f"An unexpected error occurred: {str(email_err)}")
        
        except Exception as e:
            messagebox.showerror("Contact Error", f"An error occurred: {str(e)}")

    def request_donation(self, donation_id=None):
        """Request the selected donation"""
        # If no donation_id provided, try to get from selected item
        if donation_id is None:
            selected_item = self.donations_tree.selection()
            if not selected_item:
                messagebox.showwarning("No Selection", "Please select a donation to request.")
                return
            
            # Extract donation details
            donation_details = self.donations_tree.item(selected_item[0])['values']
            donation_id = donation_details[0]
            donation_title = donation_details[1]
        else:
            # Fetch donation details using the provided ID
            try:
                donation = self.db.get_donation_details(donation_id)
                if not donation:
                    messagebox.showerror("Error", f"Donation with ID {donation_id} not found.")
                    return
                donation_title = donation.get('title', 'Unknown Donation')
            except Exception as e:
                messagebox.showerror("Error", f"Could not verify donation: {str(e)}")
                return
        
        # Prompt for request message
        request_message = simpledialog.askstring(
            "Request Donation", 
            f"Enter your request message for '{donation_title}':",
            parent=self.parent
        )
        
        if not request_message:
            messagebox.showwarning("Cancelled", "Donation request cancelled.")
            return
        
        try:
            # Verify user is not the donor
            donation_details = self.db.get_donation_details(donation_id)
            if donation_details.get('donor_id') == self.user_info['unique_id']:
                messagebox.showerror("Error", "You cannot request your own donation.")
                return
            
            # Create donation request
            request_id = self.db.create_request(
                requester_id=self.user_info['unique_id'], 
                donation_id=donation_id, 
                request_message=request_message
            )
            
            if request_id:
                messagebox.showinfo(
                    "Success", 
                    f"Request for '{donation_title}' sent successfully!\nRequest ID: {request_id}"
                )
            else:
                messagebox.showerror(
                    "Error", 
                    f"Failed to create request for '{donation_title}'. Please try again."
                )
        
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"An error occurred while requesting the donation: {str(e)}"
            )

    def send_email_dialog(self):
        """Open dialog to send email to donation owner"""
        selected_item = self.donations_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a donation to contact.")
            return

        # Get donor's email
        donor_email = self.donations_tree.item(selected_item[0])['values'][7]

        # Open email composition dialog
        email_window = tk.Toplevel(self.parent)
        email_window.title("Send Email")
        email_window.geometry("400x300")

        # Subject
        ttk.Label(email_window, text="Subject:").pack(anchor='w', padx=20, pady=(10,0))
        subject_var = tk.StringVar()
        subject_entry = ttk.Entry(email_window, textvariable=subject_var, width=50)
        subject_entry.pack(padx=20, pady=(0,10))

        # Message body
        ttk.Label(email_window, text="Message:").pack(anchor='w', padx=20, pady=(10,0))
        message_text = tk.Text(email_window, height=10, width=50)
        message_text.pack(padx=20, pady=(0,10))

        def send_email():
            """Send the composed email"""
            subject = subject_var.get()
            message = message_text.get("1.0", tk.END).strip()

            if not subject or not message:
                messagebox.showwarning("Incomplete", "Please enter both subject and message.")
                return

            try:
                # Use the current user's name from user_info
                sender_name = self.user_info.get('name', self.user_info.get('username', 'CrowdNest User'))
                
                EmailValidator.send_communication_email(
                    sender_name=sender_name,
                    sender_email=self.user_info['email'],
                    recipient_email=donor_email,
                    subject=subject,
                    body=message
                )
                messagebox.showinfo("Success", "Email sent successfully!")
                email_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send email: {str(e)}")

        # Send button
        ttk.Button(email_window, text="Send Email", command=send_email).pack(pady=10)

    def delete_donation(self):
        """Delete the selected donation"""
        selected_item = self.donations_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a donation to delete.")
            return

        # Get donation ID
        donation_id = self.donations_tree.item(selected_item[0])['values'][0]

        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this donation?")
        if confirm:
            try:
                self.db.delete_donation(donation_id)
                messagebox.showinfo("Success", "Donation deleted successfully.")
                self.refresh_donations()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete donation: {str(e)}")

    def sort_column(self, col, reverse):
        """Sort treeview column when header is clicked"""
        l = [(self.donations_tree.set(k, col), k) for k in self.donations_tree.get_children('')]
        l.sort(reverse=reverse)
        
        for index, (val, k) in enumerate(l):
            self.donations_tree.move(k, '', index)
        
        # Toggle sort direction
        self.donations_tree.heading(col, command=lambda: self.sort_column(col, not reverse))