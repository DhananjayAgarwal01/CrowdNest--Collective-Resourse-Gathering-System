import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from flask import Flask
from threading import Thread
import webbrowser
from PIL import Image, ImageTk
import os
import requests
import json
from flask_routes import app  # Import the Flask app with routes

# Modern Color scheme
COLORS = {
    'primary': '#6C63FF',        # Modern Purple
    'primary_dark': '#5A52E0',   # Darker Purple
    'secondary': '#FF6B6B',      # Coral
    'accent': '#4ECDC4',         # Turquoise
    'success': '#2ECC71',        # Emerald Green
    'warning': '#F1C40F',        # Sunflower Yellow
    'error': '#E74C3C',          # Alizarin Red
    'text': '#2C3E50',           # Dark Blue Gray
    'text_light': '#7F8C8D',     # Light Gray
    'background': '#F8F9FA',     # Light Background
    'card': '#FFFFFF',           # White
    'border': '#E9ECEF'          # Light Border
}

# Add these constants after the COLORS dictionary
LOCATIONS = [
    "Mumbai",
    "Delhi",
    "Bangalore",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Pune",
    "Ahmedabad",
    "Jaipur",
    "Surat"
]

CONDITIONS = [
    "New",
    "Like New",
    "Very Good",
    "Good",
    "Acceptable"
]

CATEGORIES = [
    "Clothing",
    "Electronics",
    "Books",
    "Furniture",
    "Home & Kitchen",
    "Sports & Fitness",
    "Toys & Games",
    "School Supplies",
    "Medical Supplies",
    "Other"
]

# Location data structure
STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal"
]

# Major cities by state
CITIES_BY_STATE = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Kakinada"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum", "Gulbarga"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Malappuram", "Kannur"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain", "Sagar"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner", "Ajmer"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli", "Tiruppur"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Ramagundam"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Prayagraj"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri", "Bardhaman"]
}
    
class NavigationPane:
    def __init__(self, parent, show_frame_callback):
        self.frame = ttk.Frame(parent, style='Navigation.TFrame')
        self.show_frame = show_frame_callback
        
        # Configure navigation frame style
        style = ttk.Style()
        style.configure('Navigation.TFrame', 
                       background=COLORS['primary'],
                       relief='flat')
        
        # Logo section
        logo_frame = ttk.Frame(self.frame, style='Navigation.TFrame')
        logo_frame.pack(fill='x', pady=(20, 40))
        ttk.Label(logo_frame, 
                 text="🎁", 
                 font=('Segoe UI', 32),
                 background=COLORS['primary'],
                 foreground='white').pack()
        ttk.Label(logo_frame, 
                 text="CrowdNest", 
                 font=('Segoe UI', 16, 'bold'),
                 background=COLORS['primary'],
                 foreground='white').pack()
        
        # Navigation buttons
        self.nav_buttons = [
            ("Dashboard", 'dashboard', '🏠'),
            ("My Profile", 'profile', '👤'),
            ("Donate Item", 'donation_form', '📦'),
            ("Browse Donations", 'donation_list', '🔍'),
            ("Messages", 'chat', '💬'),
            ("Logout", 'login', '🚪')
        ]
        
        for text, target, icon in self.nav_buttons:
            self.create_nav_button(text, target, icon)
    
    def create_nav_button(self, text, target, icon):
        btn = tk.Button(self.frame,
                       text=f"{icon} {text}",
                       font=('Segoe UI', 11),
                       bg=COLORS['primary'],
                       fg='white',
                       activebackground=COLORS['primary_dark'],
                       activeforeground='white',
                       relief='flat',
                       bd=0,
                       padx=20,
                       pady=10,
                       anchor='w',
                       width=20,
                       cursor='hand2',
                       command=lambda: self.show_frame(target))
        btn.pack(fill='x', pady=2)
        
        # Add hover effect
        btn.bind('<Enter>', lambda e: btn.configure(bg=COLORS['primary_dark']))
        btn.bind('<Leave>', lambda e: btn.configure(bg=COLORS['primary']))

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        
    def pack_forget(self):
        self.frame.pack_forget()

class ModernUI:
    @staticmethod
    def create_scrollable_frame(parent):
        # Create a canvas with scrollbars
        canvas = tk.Canvas(parent, bg=COLORS['card'], highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
        
        # Create a frame inside the canvas
        scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Configure the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Pack the scrollbars and canvas
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        
        return scrollable_frame, canvas

    def _on_mousewheel(self, event, canvas):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        # In the create_scrollable_frame method:
        canvas.bind_all("<MouseWheel>", lambda e: self._on_mousewheel(e, canvas))

    @staticmethod
    def create_header(parent):
        header = ttk.Frame(parent, style='Header.TFrame')
        header.pack(fill='x', side='top')
        
        # App title
        title = ttk.Label(header, text="CrowdNest", style='HeaderTitle.TLabel')
        title.pack(side='left', padx=20, pady=10)
        
        return header

    @staticmethod
    def create_card(parent, padding=(20, 20)):
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='both', expand=True, padx=padding[0], pady=padding[1])
        return card

    @staticmethod
    def create_button(parent, text, command, style='Primary.TButton', width=None):
        if style == 'Primary.TButton':
            btn = tk.Button(parent, text=text, command=command,
                          bg=COLORS['primary'],
                          fg='white',
                          font=('Segoe UI', 10, 'bold'),
                          relief='flat',
                          activebackground=COLORS['primary_dark'],
                          activeforeground='white',
                          cursor='hand2')
        else:  # Secondary button
            btn = tk.Button(parent, text=text, command=command,
                          bg=COLORS['secondary'],
                          fg='white',
                          font=('Segoe UI', 10),
                          relief='flat',
                          activebackground=COLORS['error'],
                          activeforeground='white',
                          cursor='hand2')
        
        if width:
            btn.configure(width=width)
            
        # Add hover effect
        btn.bind('<Enter>', lambda e: btn.configure(bg=COLORS['primary_dark'] if style == 'Primary.TButton' else COLORS['error']))
        btn.bind('<Leave>', lambda e: btn.configure(bg=COLORS['primary'] if style == 'Primary.TButton' else COLORS['secondary']))
        
        return btn

    @staticmethod
    def create_entry(parent, placeholder="", show=None, width=30):
        entry = ttk.Entry(parent, style='Modern.TEntry', width=width)
        if show:
            entry.configure(show=show)
        entry.insert(0, placeholder)
        entry.bind('<FocusIn>', lambda e: entry.delete(0, 'end') if entry.get() == placeholder else None)
        entry.bind('<FocusOut>', lambda e: entry.insert(0, placeholder) if entry.get() == '' else None)
        return entry

    @staticmethod
    def create_dropdown(parent, values, placeholder="Select", width=37):
        combo = ttk.Combobox(parent, values=values, width=width, state='readonly')
        combo.set(placeholder)
        return combo

    @staticmethod
    def create_location_selector(parent, state_var, city_var):
        # Create frame for location selection
        location_frame = ttk.Frame(parent, style='Card.TFrame')
        
        # State dropdown
        state_label = ttk.Label(location_frame, text="📍 State", style='Subtitle.TLabel')
        state_label.pack(anchor='w')
        
        state_dropdown = ttk.Combobox(location_frame, textvariable=state_var, values=STATES, state='readonly', width=37)
        state_dropdown.pack(pady=(5, 10))
        state_dropdown.set("Select State")
        
        # City dropdown
        city_label = ttk.Label(location_frame, text="🏙️ City", style='Subtitle.TLabel')
        city_label.pack(anchor='w')
        
        city_dropdown = ttk.Combobox(location_frame, textvariable=city_var, state='readonly', width=37)
        city_dropdown.pack(pady=(5, 0))
        city_dropdown.set("Select City")
        
        # Update city dropdown when state changes
        def update_cities(*args):
            selected_state = state_var.get()
            if selected_state in CITIES_BY_STATE:
                cities = CITIES_BY_STATE[selected_state]
                city_dropdown['values'] = cities
                city_dropdown.set("Select City")
            else:
                city_dropdown['values'] = []
                city_dropdown.set("Select City")
        
        state_var.trace('w', update_cities)
        return location_frame

class CustomStyle:
    @staticmethod
    def configure_styles():
        style = ttk.Style()
        
        # Configure main theme
        style.configure('.',
            background=COLORS['background'],
            foreground=COLORS['text'],
            font=('Segoe UI', 10)
        )
        
        # Header styles
        style.configure('Header.TFrame',
            background=COLORS['primary']
        )
        
        style.configure('HeaderTitle.TLabel',
            background=COLORS['primary'],
            foreground='white',
            font=('Segoe UI', 18, 'bold')
        )
        
        # Modern label styles
        style.configure('Title.TLabel',
            font=('Segoe UI', 28, 'bold'),
            foreground=COLORS['primary'],
            background=COLORS['card']
        )
        
        style.configure('Subtitle.TLabel',
            font=('Segoe UI', 14),
            foreground=COLORS['text_light'],
            background=COLORS['card']
        )
        
        # Modern entry style
        style.configure('Modern.TEntry',
            padding=(15, 10),
            font=('Segoe UI', 11)
        )
        
        # Modern frame styles
        style.configure('Card.TFrame',
            background=COLORS['card']
        )
        
        # Modern Treeview
        style.configure('Treeview',
            background=COLORS['card'],
            fieldbackground=COLORS['card'],
            foreground=COLORS['text'],
            font=('Segoe UI', 10),
            rowheight=40
        )
        style.configure('Treeview.Heading',
            background=COLORS['primary'],
            foreground='white',
            font=('Segoe UI', 10, 'bold')
        )
        
        # Add combobox style
        style.configure('TCombobox',
            background=COLORS['card'],
            foreground=COLORS['text'],
            fieldbackground=COLORS['card'],
            selectbackground=COLORS['primary'],
            selectforeground='white',
            padding=(15, 10),
            font=('Segoe UI', 11)
        )
        
        style.map('TCombobox',
            fieldbackground=[('readonly', COLORS['card'])],
            selectbackground=[('readonly', COLORS['primary'])]
        )

class CrowdNestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CrowdNest")
        self.root.geometry("1200x800")
        self.root.configure(bg=COLORS['background'])
        
        # Initialize session data
        self.token = None
        self.current_user = None
        self.api_base_url = "http://127.0.0.1:5000/api"
        
        # Initialize location variables
        self.state_var = tk.StringVar()
        self.city_var = tk.StringVar()
        
        # Initialize profile data
        self.profile_labels = {}
        self.profile_entries = {}
        
        # Configure custom styles
        CustomStyle.configure_styles()
        
        # Create main container with navigation
        self.main_container = ttk.Frame(self.root, style='Card.TFrame')
        self.main_container.pack(fill='both', expand=True)
        
        # Create navigation pane
        self.nav_pane = NavigationPane(self.main_container, self.show_frame)
        
        # Create content frame
        self.content_frame = ttk.Frame(self.main_container, style='Card.TFrame')
        
        # Initialize frames dictionary
        self.frames = {}
        
        # Create frames
        self.create_login_frame()
        self.create_register_frame()
        self.create_dashboard_frame()
        self.create_donation_form_frame()
        self.create_donation_list_frame()
        self.create_chat_frame()
        self.create_profile_frame()
        
        # Show login frame by default
        self.show_frame('login')

    def create_login_frame(self):
        frame = ModernUI.create_card(self.content_frame)
        
        # Center content
        content = ttk.Frame(frame, style='Card.TFrame')
        content.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo/Icon
        ttk.Label(content, text="🎁", font=('Segoe UI', 48)).pack(pady=(0, 20))
        
        # Welcome text
        ttk.Label(content, text="Welcome Back!", style='Title.TLabel').pack()
        ttk.Label(content, text="Sign in to continue", style='Subtitle.TLabel').pack(pady=(0, 30))
        
        # Login form
        self.username_entry = ModernUI.create_entry(content, "Username", width=40)
        self.username_entry.pack(pady=10)
        
        self.password_entry = ModernUI.create_entry(content, "Password", show="•", width=40)
        self.password_entry.pack(pady=10)
        
        # Buttons
        ModernUI.create_button(content, "Sign In", self.login, width=40).pack(pady=20)
        ttk.Label(content, text="Don't have an account?", style='Subtitle.TLabel').pack(pady=(20, 5))
        ModernUI.create_button(content, "Create Account", 
                             lambda: self.show_frame('register'), 
                             style='Secondary.TButton', width=40).pack()
        
        self.frames['login'] = frame
    def check_password_strength(self, event=None):
        password = self.register_entries['Password:'].get()
        strength = 0

        # Criteria for password strength
        if len(password) >= 8:
            strength += 1
        if any(char.isdigit() for char in password):
            strength += 1
        if any(char.isupper() for char in password):
            strength += 1
        if any(char.islower() for char in password):
            strength += 1
        if any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in password):
            strength += 1

        # Update the password strength label
        if strength == 0:
            self.password_strength_label.config(text="Weak", foreground=COLORS['error'])
        elif strength <= 2:
            self.password_strength_label.config(text="Moderate", foreground=COLORS['warning'])
        else:
            self.password_strength_label.config(text="Strong", foreground=COLORS['success'])

    def create_register_frame(self):
        frame = ModernUI.create_card(self.content_frame)
        
        # Center content
        content = ttk.Frame(frame, style='Card.TFrame')
        content.place(relx=0.5, rely=0.5, anchor='center')

        # Header Section
        header_frame = ttk.Frame(content, style='Card.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(header_frame, text="🎁", font=('Segoe UI', 48), foreground=COLORS['primary']).pack()
        ttk.Label(header_frame, text="Create Account", style='Title.TLabel').pack()
        ttk.Label(header_frame, text="Join our community and start sharing!", style='Subtitle.TLabel').pack()

        # Registration Form
        self.register_entries = {}

        # Username Field
        username_frame = ttk.Frame(content, style='Card.TFrame')
        username_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(username_frame, text="👤 Username", style='Subtitle.TLabel').pack(anchor='w')
        self.register_entries['Username:'] = ModernUI.create_entry(username_frame, placeholder="Enter your username", width=40)
        self.register_entries['Username:'].pack(pady=(5, 0))

        # Email Field
        email_frame = ttk.Frame(content, style='Card.TFrame')
        email_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(email_frame, text="📧 Email", style='Subtitle.TLabel').pack(anchor='w')
        self.register_entries['Email:'] = ModernUI.create_entry(email_frame, placeholder="Enter your email", width=40)
        self.register_entries['Email:'].pack(pady=(5, 0))

        # Password Fields
        password_frame = ttk.Frame(content, style='Card.TFrame')
        password_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(password_frame, text="🔒 Password", style='Subtitle.TLabel').pack(anchor='w')
        self.register_entries['Password:'] = ModernUI.create_entry(password_frame, show="•", placeholder="Enter your password", width=40)
        self.register_entries['Password:'].pack(pady=(5, 0))

        confirm_password_frame = ttk.Frame(content, style='Card.TFrame')
        confirm_password_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(confirm_password_frame, text="🔒 Confirm Password", style='Subtitle.TLabel').pack(anchor='w')
        self.register_entries['Confirm Password:'] = ModernUI.create_entry(confirm_password_frame, show="•", placeholder="Re-enter your password", width=40)
        self.register_entries['Confirm Password:'].pack(pady=(5, 0))

        # Password Strength Indicator
        self.password_strength_label = ttk.Label(password_frame, text="", style='Subtitle.TLabel', foreground=COLORS['text_light'])
        self.password_strength_label.pack(anchor='w', pady=(5, 0))
        self.register_entries['Password:'].bind('<KeyRelease>', self.check_password_strength)

        # Location Selector
        location_selector = ModernUI.create_location_selector(content, self.state_var, self.city_var)
        location_selector.pack(fill='x', pady=(0, 20))

        # Store the location variables
        self.register_entries['State:'] = self.state_var
        self.register_entries['City:'] = self.city_var

        # Action Buttons
        button_frame = ttk.Frame(content, style='Card.TFrame')
        button_frame.pack(fill='x', pady=20)
        ModernUI.create_button(button_frame, "Create Account", self.register, width=20).pack(side='left', padx=5)
        ModernUI.create_button(button_frame, "Back to Login", lambda: self.show_frame('login'), style='Secondary.TButton', width=20).pack(side='right', padx=5)

        self.frames['register'] = frame

    def create_dashboard_frame(self):
        frame = ModernUI.create_card(self.content_frame)
        
        # Create a scrollable canvas for the content
        canvas = tk.Canvas(frame, bg=COLORS['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
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
        
        # Welcome section
        welcome_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        welcome_frame.pack(fill='x', pady=(20, 30))
        
        ttk.Label(welcome_frame, text="Welcome Back!", style='Title.TLabel').pack()
        self.welcome_label = ttk.Label(welcome_frame, text="", style='Subtitle.TLabel')
        self.welcome_label.pack()
        
        # Quick Actions
        actions_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        actions_frame.pack(fill='x', padx=40, pady=20)
        
        ttk.Label(actions_frame, text="Quick Actions", style='Title.TLabel').pack(anchor='w', pady=(0, 10))
        
        buttons_frame = ttk.Frame(actions_frame, style='Card.TFrame')
        buttons_frame.pack(fill='x')
        
        quick_actions = [
            ("Donate Item", 'donation_form', '📦'),
            ("Browse Items", 'donation_list', '🔍'),
            ("Messages", 'chat', '💬'),
            ("My Profile", 'profile', '👤')
        ]
        
        for text, target, icon in quick_actions:
            btn = ModernUI.create_button(
                buttons_frame,
                f"{icon} {text}",
                lambda t=target: self.show_frame(t),
                width=20
            )
            btn.pack(side='left', padx=5)
        
        self.frames['dashboard'] = frame

    def create_donation_form_frame(self):
        frame = ModernUI.create_card(self.content_frame)
        
        # Create a scrollable canvas for the content
        canvas = tk.Canvas(frame, bg=COLORS['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
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
        
        ttk.Label(header_frame, text="Donate an Item", style='Title.TLabel').pack()
        ttk.Label(header_frame, text="Share your items with those in need", style='Subtitle.TLabel').pack()
        
        # Main content
        content = ttk.Frame(scrollable_frame, style='Card.TFrame')
        content.pack(fill='x', padx=50)
        
        self.donation_entries = {}
        
        # Title field with character counter
        title_frame = ttk.Frame(content, style='Card.TFrame')
        title_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(title_frame, text="Title", style='Subtitle.TLabel').pack(anchor='w')
        title_entry = ModernUI.create_entry(title_frame, width=50)
        title_entry.pack(side='left', pady=(5, 0))
        self.donation_entries['Title:'] = title_entry
        self.title_counter = ttk.Label(title_frame, text="0/100", style='Subtitle.TLabel')
        self.title_counter.pack(side='left', padx=10)
        title_entry.bind('<KeyRelease>', lambda e: self.update_char_counter(title_entry, self.title_counter, 100))
        
        # Description field with character counter
        desc_frame = ttk.Frame(content, style='Card.TFrame')
        desc_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(desc_frame, text="Description", style='Subtitle.TLabel').pack(anchor='w')
        desc_text = tk.Text(desc_frame, height=4, width=50, wrap='word')
        desc_text.configure(font=('Segoe UI', 10), padx=10, pady=5)
        desc_text.pack(side='left', pady=(5, 0))
        self.donation_entries['Description:'] = desc_text
        self.desc_counter = ttk.Label(desc_frame, text="0/500", style='Subtitle.TLabel')
        self.desc_counter.pack(side='left', padx=10, anchor='n')
        desc_text.bind('<KeyRelease>', lambda e: self.update_char_counter(desc_text, self.desc_counter, 500, is_text=True))
        
        # Category dropdown with icon
        cat_frame = ttk.Frame(content, style='Card.TFrame')
        cat_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(cat_frame, text="📦 Category", style='Subtitle.TLabel').pack(anchor='w')
        self.donation_entries['Category:'] = ModernUI.create_dropdown(cat_frame, CATEGORIES, "Select Category", width=47)
        self.donation_entries['Category:'].pack(pady=(5, 0))
        
        # Condition dropdown with icon
        cond_frame = ttk.Frame(content, style='Card.TFrame')
        cond_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(cond_frame, text="✨ Condition", style='Subtitle.TLabel').pack(anchor='w')
        self.donation_entries['Condition:'] = ModernUI.create_dropdown(cond_frame, CONDITIONS, "Select Condition", width=47)
        self.donation_entries['Condition:'].pack(pady=(5, 0))
        
        # Replace the old location dropdown with new location selector
        loc_frame = ttk.Frame(content, style='Card.TFrame')
        loc_frame.pack(fill='x', pady=(0, 20))
        location_selector = ModernUI.create_location_selector(loc_frame, self.state_var, self.city_var)
        location_selector.pack(fill='x')
        
        # Store the location variables
        self.donation_entries['State:'] = self.state_var
        self.donation_entries['City:'] = self.city_var
        
        # Image upload (placeholder for future implementation)
        img_frame = ttk.Frame(content, style='Card.TFrame')
        img_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(img_frame, text="📸 Upload Images", style='Subtitle.TLabel').pack(anchor='w')
        ModernUI.create_button(img_frame, "Choose Files", lambda: messagebox.showinfo("Info", "Image upload will be available soon"), style='Secondary.TButton').pack(pady=(5, 0))
        
        # Buttons at the bottom
        button_frame = ttk.Frame(content, style='Card.TFrame')
        button_frame.pack(fill='x', pady=30)
        
        ModernUI.create_button(button_frame, "Preview Donation", self.preview_donation, width=20).pack(side='left', padx=5)
        ModernUI.create_button(button_frame, "Submit Donation", self.submit_donation, width=20).pack(side='left', padx=5)
        ModernUI.create_button(button_frame, "Back to Dashboard", 
                             lambda: self.show_frame('dashboard'), 
                             style='Secondary.TButton', width=20).pack(side='right', padx=5)
        
        self.frames['donation_form'] = frame

    def create_donation_list_frame(self):
        frame = ModernUI.create_card(self.content_frame)
        
        # Create a scrollable canvas for the content
        canvas = tk.Canvas(frame, bg=COLORS['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
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
        self.donations_tree.bind('<Double-1>', self.show_donation_details)
        
        # Action buttons
        button_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        button_frame.pack(fill='x', padx=40, pady=20)
        
        ModernUI.create_button(button_frame, "Request Selected", self.request_donation, width=20).pack(side='left', padx=5)
        ModernUI.create_button(button_frame, "Contact Donor", self.contact_donor, width=20).pack(side='left', padx=5)
        ModernUI.create_button(button_frame, "Back to Dashboard", 
                             lambda: self.show_frame('dashboard'), 
                             style='Secondary.TButton', width=20).pack(side='right', padx=5)
        
        self.frames['donation_list'] = frame

    def create_chat_frame(self):
        frame = ModernUI.create_card(self.content_frame)
        
        # Center content
        content = ttk.Frame(frame, style='Card.TFrame')
        content.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Label(content, text="Messages", style='Title.TLabel').pack()
        
        # Chat container
        chat_container = ttk.Frame(content, style='Card.TFrame')
        chat_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Contacts list
        contacts_frame = ttk.Frame(chat_container, style='Card.TFrame', width=250)
        contacts_frame.pack_propagate(False)
        contacts_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        ttk.Label(contacts_frame, text="Contacts", style='Subtitle.TLabel').pack(pady=10)
        
        self.contacts_list = ttk.Treeview(contacts_frame, columns=('Contact'), show='headings', height=20)
        self.contacts_list.heading('Contact', text='Contact')
        self.contacts_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Message area
        message_frame = ttk.Frame(chat_container, style='Card.TFrame')
        message_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Messages display
        self.message_text = tk.Text(message_frame, height=20, wrap=tk.WORD)
        self.message_text.configure(font=('Segoe UI', 10), padx=10, pady=10)
        self.message_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Message input
        input_frame = ttk.Frame(message_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.message_entry = ModernUI.create_entry(input_frame, placeholder="Type your message...", width=40)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ModernUI.create_button(input_frame, text="Send", command=self.send_message, style='Primary.TButton').pack(side=tk.RIGHT)
        
        # Back button
        ModernUI.create_button(content, "Back to Dashboard", lambda: self.show_frame('dashboard'), style='Secondary.TButton', width=40).pack(pady=20)
        
        self.frames['chat'] = frame

    def create_profile_frame(self):
        frame = ModernUI.create_card(self.content_frame)
        
        # Create a scrollable canvas for the content
        canvas = tk.Canvas(frame, bg=COLORS['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
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
        
        # Profile Header
        header_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        header_frame.pack(fill='x', pady=(20, 30))
        
        # Profile Avatar
        avatar_frame = ttk.Frame(header_frame, style='Card.TFrame')
        avatar_frame.pack(pady=20)
        avatar_label = ttk.Label(
            avatar_frame,
            text="👤",
            font=('Segoe UI', 48),
            background=COLORS['primary'],
            foreground='white'
        )
        avatar_label.pack(pady=10)
        
        ttk.Label(header_frame, text="My Profile", style='Title.TLabel').pack()
        
        # Profile Information Section
        info_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        info_frame.pack(fill='x', padx=40, pady=20)
        
        # Profile fields
        self.profile_entries = {}
        fields = [
            ('Username:', False),  # (field_name, is_editable)
            ('Email:', True),
            ('Location:', True),
            ('Join Date:', False),
            ('Total Donations:', False)
        ]
        
        for i, (field, editable) in enumerate(fields):
            field_frame = ttk.Frame(info_frame, style='Card.TFrame')
            field_frame.pack(fill='x', pady=5)
            
            ttk.Label(field_frame, text=field, style='Subtitle.TLabel').pack(anchor='w')
            
            if editable:
                entry = ModernUI.create_entry(field_frame, width=40)
                entry.pack(pady=(5, 10))
                self.profile_entries[field] = entry
            else:
                label = ttk.Label(field_frame, text="", style='Subtitle.TLabel')
                label.pack(pady=(5, 10))
                self.profile_labels[field] = label
        
        # Statistics Section
        stats_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        stats_frame.pack(fill='x', padx=40, pady=20)
        
        ttk.Label(stats_frame, text="Activity Statistics", style='Title.TLabel').pack(anchor='w', pady=(0, 10))
        
        stats_grid = ttk.Frame(stats_frame, style='Card.TFrame')
        stats_grid.pack(fill='x')
        
        stats = [
            ("🎁 Donations Made", "0"),
            ("📦 Items Received", "0"),
            ("💬 Messages Sent", "0"),
            ("⭐ Rating", "N/A")
        ]
        
        for i, (label, value) in enumerate(stats):
            stat_frame = ttk.Frame(stats_grid, style='Card.TFrame')
            stat_frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(stat_frame, text=label, style='Subtitle.TLabel').pack()
            ttk.Label(stat_frame, text=value, font=('Segoe UI', 24, 'bold')).pack()
        
        # Action Buttons
        button_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        button_frame.pack(fill='x', padx=40, pady=20)
        
        ModernUI.create_button(
            button_frame,
            "Save Changes",
            self.save_profile_changes,
            width=20
        ).pack(side='left', padx=5)
        
        ModernUI.create_button(
            button_frame,
            "Change Password",
            self.change_password,
            style='Secondary.TButton',
            width=20
        ).pack(side='left', padx=5)
        
        ModernUI.create_button(
            button_frame,
            "Back to Dashboard",
            lambda: self.show_frame('dashboard'),
            style='Secondary.TButton',
            width=20
        ).pack(side='right', padx=5)
        
        self.frames['profile'] = frame

    def api_request(self, method, endpoint, data=None, params=None):
        url = f"{self.api_base_url}/{endpoint}"
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            
            response.raise_for_status()  # Raise an exception for bad status codes
            
            if response.status_code in (200, 201):
                return response.json()
            else:
                error_msg = response.json().get('message', 'An error occurred')
                messagebox.showerror("Error", error_msg)
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"API request error: {str(e)}")
            if hasattr(e.response, 'json'):
                error_msg = e.response.json().get('message', str(e))
            else:
                error_msg = str(e)
            messagebox.showerror("Error", f"Connection error: {error_msg}")
            return None
        
    def login(self):
        data = {
            'username': self.username_entry.get(),
            'password': self.password_entry.get()
        }
        
        response = self.api_request('POST', 'login', data)
        
        if response:
            self.token = response['token']
            self.current_user = response['user']
            self.show_frame('dashboard')
            self.update_dashboard()
            
    def register(self):
        data = {
            'username': self.register_entries['Username:'].get(),
            'email': self.register_entries['Email:'].get(),
            'password': self.register_entries['Password:'].get(),
            'state': self.state_var.get(),
            'city': self.city_var.get()
        }
        
        # Basic validation
        if not all(data.values()) or data['state'] == "Select State" or data['city'] == "Select City":
            messagebox.showerror("Error", "All fields are required")
            return
            
        # Combine state and city for location
        data['location'] = f"{data['city']}, {data['state']}"
        
        # Remove state and city from data before sending
        del data['state']
        del data['city']
        
        if data['password'] != self.register_entries['Confirm Password:'].get():
            messagebox.showerror("Error", "Passwords do not match")
            return
            
        if len(data['password']) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
            return
            
        if len(data['username']) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters long")
            return
            
        if '@' not in data['email']:
            messagebox.showerror("Error", "Invalid email format")
            return
            
        try:
            response = self.api_request('POST', 'register', data)
            
            if response:
                messagebox.showinfo("Success", "Registration successful! Please login.")
                self.show_frame('login')
                
                # Clear the form
                for entry in self.register_entries.values():
                    entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
            print(f"Registration error: {str(e)}")
            
    def submit_donation(self):
        # Basic validation
        if not self.current_user:
            messagebox.showerror("Error", "Please login first")
            return
            
        data = {
            'title': self.donation_entries['Title:'].get(),
            'description': self.donation_entries['Description:'].get("1.0", tk.END).strip(),
            'category': self.donation_entries['Category:'].get(),
            'condition': self.donation_entries['Condition:'].get(),
            'state': self.state_var.get(),
            'city': self.city_var.get()
        }
        
        # Validate required fields
        if not data['title'] or not data['description']:
            messagebox.showerror("Error", "Title and description are required")
            return
            
        # Validate dropdowns
        if data['category'] == "Select Category":
            messagebox.showerror("Error", "Please select a category")
            return
        if data['condition'] == "Select Condition":
            messagebox.showerror("Error", "Please select a condition")
            return
        if data['state'] == "Select State" or data['city'] == "Select City":
            messagebox.showerror("Error", "Please select both state and city")
            return
            
        # Validate text lengths
        if len(data['title']) > 100:
            messagebox.showerror("Error", "Title must be less than 100 characters")
            return
        if len(data['description']) > 500:
            messagebox.showerror("Error", "Description must be less than 500 characters")
            return
        
        # Combine state and city for location
        data['location'] = f"{data['city']}, {data['state']}"
        
        # Remove state and city from data before sending
        del data['state']
        del data['city']
        
        try:
            print(f"Submitting donation data: {data}")
            response = self.api_request('POST', 'donations', data)
            
            if response:
                messagebox.showinfo("Success", "Donation created successfully!")
                # Clear the form
                self.donation_entries['Title:'].delete(0, tk.END)
                self.donation_entries['Description:'].delete("1.0", tk.END)
                self.donation_entries['Category:'].set("Select Category")
                self.donation_entries['Condition:'].set("Select Condition")
                self.state_var.set("Select State")
                self.city_var.set("Select City")
                # Return to dashboard
                self.show_frame('dashboard')
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('message', str(e))
                except:
                    pass
            messagebox.showerror("Error", f"Failed to create donation: {error_msg}")
            print(f"Donation creation error: {error_msg}")
            
    def search_donations(self):
        search_term = self.search_entry.get()
        donations = self.api_request('GET', 'donations', params={'search': search_term})
        
        if donations:
            self.donations_tree.delete(*self.donations_tree.get_children())
            
            for donation in donations:
                self.donations_tree.insert('', 'end', values=(
                    donation['title'],
                    donation['category'],
                    donation['condition'],
                    donation['location']
                ))
                
    def send_message(self):
        if not hasattr(self, 'selected_contact'):
            messagebox.showerror("Error", "Please select a contact first")
            return
            
        content = self.message_entry.get()
        if not content:
            return
            
        data = {
            'receiver_id': self.selected_contact,
            'content': content
        }
        
        response = self.api_request('POST', 'messages', data)
        
        if response:
            self.message_entry.delete(0, tk.END)
            self.update_messages()
            
    def save_profile_changes(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please login first")
            return
            
        data = {
            'email': self.profile_entries['Email:'].get(),
            'location': self.profile_entries['Location:'].get()
        }
        
        # Basic validation
        if not data['email'] or not data['location']:
            messagebox.showerror("Error", "All fields are required")
            return
            
        if '@' not in data['email']:
            messagebox.showerror("Error", "Invalid email format")
            return
            
        response = self.api_request('PUT', 'profile', data)
        
        if response:
            messagebox.showinfo("Success", "Profile updated successfully!")
            self.current_user.update(data)
            self.update_profile_display()

    def change_password(self):
        # Create password change window
        password_window = tk.Toplevel(self.root)
        password_window.title("Change Password")
        password_window.geometry("400x300")
        password_window.configure(bg=COLORS['card'])
        
        content = ttk.Frame(password_window, style='Card.TFrame')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(content, text="Change Password", style='Title.TLabel').pack(pady=(0, 20))
        
        # Password fields
        ttk.Label(content, text="Current Password", style='Subtitle.TLabel').pack(anchor='w')
        current_password = ModernUI.create_entry(content, show="•", width=30)
        current_password.pack(pady=5)
        
        ttk.Label(content, text="New Password", style='Subtitle.TLabel').pack(anchor='w')
        new_password = ModernUI.create_entry(content, show="•", width=30)
        new_password.pack(pady=5)
        
        ttk.Label(content, text="Confirm New Password", style='Subtitle.TLabel').pack(anchor='w')
        confirm_password = ModernUI.create_entry(content, show="•", width=30)
        confirm_password.pack(pady=5)
        
        def submit_password_change():
            if new_password.get() != confirm_password.get():
                messagebox.showerror("Error", "New passwords do not match")
                return
                
            if len(new_password.get()) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long")
                return
                
            data = {
                'current_password': current_password.get(),
                'new_password': new_password.get()
            }
            
            response = self.api_request('PUT', 'change-password', data)
            
            if response:
                messagebox.showinfo("Success", "Password changed successfully!")
                password_window.destroy()
        
        ModernUI.create_button(
            content,
            "Change Password",
            submit_password_change,
            width=30
        ).pack(pady=20)

    def update_profile_display(self):
        if self.current_user:
            # Update labels
            self.profile_labels['Username:']['text'] = self.current_user['username']
            self.profile_labels['Join Date:']['text'] = self.current_user.get('created_at', 'N/A')
            self.profile_labels['Total Donations:']['text'] = str(self.current_user.get('total_donations', 0))
            
            # Update entries
            self.profile_entries['Email:'].delete(0, tk.END)
            self.profile_entries['Email:'].insert(0, self.current_user['email'])
            self.profile_entries['Location:'].delete(0, tk.END)
            self.profile_entries['Location:'].insert(0, self.current_user['location'])
            
            # Update welcome message in dashboard
            if hasattr(self, 'welcome_label'):
                self.welcome_label.config(text=f"Welcome back, {self.current_user['username']}!")

    def update_dashboard(self):
        # Update any dashboard widgets with current user data
        pass
        
    def show_frame(self, frame_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Show/hide navigation based on login state
        if frame_name in ['login', 'register']:
            self.nav_pane.pack_forget()
            self.content_frame.pack(fill='both', expand=True)
        else:
            self.nav_pane.pack(side='left', fill='y')
            self.content_frame.pack(side='left', fill='both', expand=True)
        
        # Show requested frame
        self.frames[frame_name].pack(fill='both', expand=True)
        
        # Perform any necessary updates
        if frame_name == 'profile':
            self.update_profile_display()
        elif frame_name == 'donation_list':
            self.search_donations()
        elif frame_name == 'chat':
            self.update_messages()

    def update_char_counter(self, widget, counter_label, max_chars, is_text=False):
        if is_text:
            current = len(widget.get("1.0", tk.END).strip())
        else:
            current = len(widget.get())
        counter_label.config(text=f"{current}/{max_chars}")
        if current > max_chars:
            counter_label.config(foreground=COLORS['error'])
        else:
            counter_label.config(foreground=COLORS['text_light'])

    def preview_donation(self):
        # Get the donation data
        data = {
            'title': self.donation_entries['Title:'].get(),
            'description': self.donation_entries['Description:'].get("1.0", tk.END).strip(),
            'category': self.donation_entries['Category:'].get(),
            'condition': self.donation_entries['Condition:'].get(),
            'state': self.state_var.get(),
            'city': self.city_var.get()
        }
        
        # Create preview window
        preview = tk.Toplevel(self.root)
        preview.title("Preview Donation")
        preview.geometry("600x400")
        preview.configure(bg=COLORS['card'])
        
        # Preview content
        content = ttk.Frame(preview, style='Card.TFrame')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(content, text="Donation Preview", style='Title.TLabel').pack(pady=(0, 20))
        
        for key, value in data.items():
            if value and value != "Select Category" and value != "Select Condition" and value != "Select State" and value != "Select City":
                label = key.replace(':', '')
                ttk.Label(content, text=f"{label}:", style='Subtitle.TLabel').pack(anchor='w')
                ttk.Label(content, text=value, style='Subtitle.TLabel').pack(anchor='w', pady=(0, 10))

    def clear_filters(self):
        self.category_filter.set("Category")
        self.condition_filter.set("Condition")
        self.location_filter.set("Location")
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, "Search donations...")
        self.search_donations()

    def show_donation_details(self, event):
        item = self.donations_tree.selection()[0]
        donation = self.donations_tree.item(item)
        
        # Create details window
        details = tk.Toplevel(self.root)
        details.title("Donation Details")
        details.geometry("600x400")
        details.configure(bg=COLORS['card'])
        
        # Details content
        content = ttk.Frame(details, style='Card.TFrame')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(content, text="Donation Details", style='Title.TLabel').pack(pady=(0, 20))
        
        for col, value in zip(self.donations_tree['columns'], donation['values']):
            ttk.Label(content, text=f"{col}:", style='Subtitle.TLabel').pack(anchor='w')
            ttk.Label(content, text=str(value), style='Subtitle.TLabel').pack(anchor='w', pady=(0, 10))
        
        button_frame = ttk.Frame(content, style='Card.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        ModernUI.create_button(button_frame, "Request Item", lambda: self.request_donation(item), width=20).pack(side='left', padx=5)
        ModernUI.create_button(button_frame, "Contact Donor", lambda: self.contact_donor(item), width=20).pack(side='left', padx=5)

    def request_donation(self, item=None):
        if not item:
            selection = self.donations_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a donation first")
                return
            item = selection[0]
        
        # Create request window
        request_window = tk.Toplevel(self.root)
        request_window.title("Request Donation")
        request_window.geometry("500x400")
        request_window.configure(bg=COLORS['card'])
        
        content = ttk.Frame(request_window, style='Card.TFrame')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(content, text="Request Item", style='Title.TLabel').pack(pady=(0, 20))
        
        # Message field
        ttk.Label(content, text="Message to Donor", style='Subtitle.TLabel').pack(anchor='w')
        message = tk.Text(content, height=6, width=40, wrap='word')
        message.configure(font=('Segoe UI', 10), padx=10, pady=5)
        message.pack(pady=10)
        
        # Add some suggested message templates
        templates_frame = ttk.Frame(content, style='Card.TFrame')
        templates_frame.pack(fill='x', pady=10)
        
        ttk.Label(templates_frame, text="Quick Templates:", style='Subtitle.TLabel').pack(anchor='w')
        
        templates = [
            "Hi, I'm interested in your donation. Is it still available?",
            "Hello, I would like to request this item. When can we arrange pickup?",
            "Greetings! I really need this item. Can we discuss the details?"
        ]
        
        for template in templates:
            ModernUI.create_button(
                templates_frame,
                "Use Template",
                lambda t=template: message.insert('1.0', t),
                style='Secondary.TButton'
            ).pack(anchor='w', pady=2)
        
        # Submit button
        ModernUI.create_button(
            content,
            "Submit Request",
            lambda: self.submit_request(item, message.get('1.0', tk.END).strip(), request_window),
            width=30
        ).pack(pady=20)

    def submit_request(self, item, message, window):
        if not message:
            messagebox.showwarning("Warning", "Please enter a message")
            return
            
        donation = self.donations_tree.item(item)
        data = {
            'donation_id': donation['values'][0],  # Assuming first column is ID
            'message': message
        }
        
        response = self.api_request('POST', 'requests', data)
        
        if response:
            messagebox.showinfo("Success", "Request sent successfully!")
            window.destroy()

    def contact_donor(self, item=None):
        if not item:
            selection = self.donations_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a donation first")
                return
            item = selection[0]
        
        donation = self.donations_tree.item(item)
        donor = donation['values'][4]  # Assuming 'Donor' is the 5th column
        
        # Switch to chat frame and start conversation
        self.show_frame('chat')
        # Additional logic to start chat with donor

def run_flask():
    app.run(host='127.0.0.1', port=5000)  # Add explicit host and port

if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Create and run Tkinter app
    root = tk.Tk()
    app = CrowdNestApp(root)
    root.mainloop() 