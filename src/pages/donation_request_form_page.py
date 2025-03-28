import tkinter as tk
from tkinter import ttk, messagebox
from src.database.database_handler import DatabaseHandler
from src.constants import COLORS

class DonationRequestFormPage:
    def __init__(self, parent, user_info, show_frame_callback):
        """
        Initialize the Donation Request Form Page

        :param parent: Parent tkinter widget
        :param user_info: Dictionary containing user information
        :param show_frame_callback: Callback to switch between frames
        """
        # Create main frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Store parameters
        self.user_info = user_info
        self.show_frame = show_frame_callback
        self.db = DatabaseHandler()
        
        # Create page components
        self._create_header()
        self._create_form()
        self._create_action_buttons()

    def _create_header(self):
        """Create page header"""
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', pady=10)
        
        # Title
        ttk.Label(
            header_frame, 
            text="Create Donation Request", 
            font=('Segoe UI', 16, 'bold')
        ).pack(side='left', padx=20)
        
        # User greeting
        ttk.Label(
            header_frame, 
            text=f"Welcome, {self.user_info.get('name', 'Donor')}!", 
            font=('Segoe UI', 12)
        ).pack(side='right', padx=20)

    def _create_form(self):
        """Create donation request form"""
        form_frame = ttk.Frame(self.frame)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Title
        ttk.Label(form_frame, text="Title:", font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.title_entry = ttk.Entry(form_frame, width=50)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Description
        ttk.Label(form_frame, text="Description:", font=('Segoe UI', 10)).grid(row=1, column=0, sticky='nw', padx=5, pady=5)
        self.description_text = tk.Text(form_frame, height=4, width=50)
        self.description_text.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Category
        ttk.Label(form_frame, text="Category:", font=('Segoe UI', 10)).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        categories = ['Clothing', 'Food', 'Books', 'Electronics', 'Furniture', 'Other']
        self.category_var = tk.StringVar()
        category_dropdown = ttk.Combobox(form_frame, textvariable=self.category_var, values=categories, state='readonly')
        category_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        category_dropdown.set('Select Category')

        # Condition
        ttk.Label(form_frame, text="Condition:", font=('Segoe UI', 10)).grid(row=3, column=0, sticky='w', padx=5, pady=5)
        conditions = ['New', 'Like New', 'Good', 'Acceptable']
        self.condition_var = tk.StringVar()
        condition_dropdown = ttk.Combobox(form_frame, textvariable=self.condition_var, values=conditions, state='readonly')
        condition_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        condition_dropdown.set('Select Condition')

        # State
        ttk.Label(form_frame, text="State:", font=('Segoe UI', 10)).grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.state_entry = ttk.Entry(form_frame, width=50)
        self.state_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        # City
        ttk.Label(form_frame, text="City:", font=('Segoe UI', 10)).grid(row=5, column=0, sticky='w', padx=5, pady=5)
        self.city_entry = ttk.Entry(form_frame, width=50)
        self.city_entry.grid(row=5, column=1, padx=5, pady=5, sticky='ew')

        # Urgency
        ttk.Label(form_frame, text="Urgency:", font=('Segoe UI', 10)).grid(row=6, column=0, sticky='w', padx=5, pady=5)
        urgencies = ['Low', 'Medium', 'High']
        self.urgency_var = tk.StringVar()
        urgency_dropdown = ttk.Combobox(form_frame, textvariable=self.urgency_var, values=urgencies, state='readonly')
        urgency_dropdown.grid(row=6, column=1, padx=5, pady=5, sticky='ew')
        urgency_dropdown.set('Select Urgency')

        # Configure grid
        form_frame.grid_columnconfigure(1, weight=1)

    def _create_action_buttons(self):
        """Create action buttons for the form"""
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill='x', padx=20, pady=10)

        # Submit Button
        submit_btn = ttk.Button(
            button_frame, 
            text="Submit Request", 
            command=self._submit_donation_request,
            style='Primary.TButton'
        )
        submit_btn.pack(side='right', padx=10)

        # Cancel Button
        cancel_btn = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self._cancel_request,
            style='Secondary.TButton'
        )
        cancel_btn.pack(side='right')

    def _submit_donation_request(self):
        """Submit the donation request"""
        # Validate inputs
        title = self.title_entry.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        category = self.category_var.get()
        condition = self.condition_var.get()
        state = self.state_entry.get().strip()
        city = self.city_entry.get().strip()
        urgency = self.urgency_var.get()

        # Validate all fields
        if not all([title, description, category != 'Select Category', 
                    condition != 'Select Condition', state, city, 
                    urgency != 'Select Urgency']):
            messagebox.showerror("Validation Error", "Please fill in all fields")
            return

        # Get user ID from user info
        user_id = self.user_info.get('unique_id')
        if not user_id:
            messagebox.showerror("Error", "User information not found")
            return

        # Create donation request
        success, message, request_id = self.db.create_donation_request(
            user_id, title, description, category, condition, 
            state, city, urgency.upper()
        )

        if success:
            messagebox.showinfo("Success", f"Donation request created successfully!\nRequest ID: {request_id}")
            self._clear_form()
        else:
            messagebox.showerror("Error", message)

    def _cancel_request(self):
        """Cancel the donation request form"""
        # Clear the form
        self._clear_form()
        # Optionally, go back to previous page
        # self.show_frame('DonationRequestsPage')

    def _clear_form(self):
        """Clear all form fields"""
        self.title_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)
        self.category_var.set('Select Category')
        self.condition_var.set('Select Condition')
        self.state_entry.delete(0, tk.END)
        self.city_entry.delete(0, tk.END)
        self.urgency_var.set('Select Urgency')

    def destroy(self):
        """Destroy the frame"""
        self.frame.destroy()
