import tkinter as tk
from tkinter import ttk, messagebox
from database_handler import DatabaseHandler
from PIL import Image, ImageTk
import os
from datetime import datetime

# Modern Color scheme
COLORS = {
    'primary': '#0077B6',        # Deep Ocean Blue
    'primary_dark': '#023E8A',   # Darker Blue
    'secondary': '#F77F00',      # Warm Sunset Orange
    'accent': '#00B4D8',         # Vibrant Teal
    'success': '#38A3A5',        # Calming Green
    'warning': '#FFBA08',        # Golden Yellow
    'error': '#D62828',          # Rich Red
    'text': '#1B1B1E',           # Dark Charcoal
    'text_light': '#6C757D',     # Muted Gray
    'background': '#F1F3F5',     # Soft Light Gray
    'card': '#FFFFFF',           # Crisp White
    'border': '#DEE2E6'          # Subtle Border Gray
}

# Add these constants after the COLORS dictionary
LOCATIONS = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune",
    "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur", "Nagpur", "Indore",
    "Thane", "Bhopal", "Visakhapatnam", "Vadodara", "Ghaziabad", "Ludhiana",
    "Patna", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Varanasi",
    "Srinagar", "Aurangabad", "Dhanbad"
]

CONDITIONS = [
    "New", "Like New", "Very Good", "Good", "Acceptable"
]

CATEGORIES = [
    "Clothing", "Electronics", "Books", "Furniture", "Home & Kitchen",
    "Sports & Fitness", "Toys & Games", "School Supplies", "Medical Supplies",
    "Automobiles", "Music Instruments", "Beauty & Personal Care", "Other"
]

STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal"
]
# Major cities by state
CITIES_BY_STATE = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Kakinada"],
    "Arunachal Pradesh": ["Itanagar", "Naharlagun", "Tawang", "Pasighat", "Roing", "Ziro"],
    "Assam": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Tezpur", "Nagaon"],
    "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia", "Darbhanga"],
    "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg", "Rajnandgaon"],
    "Goa": ["Panaji", "Vasco da Gama", "Margao", "Mapusa", "Ponda", "Bicholim"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar"],
    "Haryana": ["Chandigarh", "Faridabad", "Gurugram", "Ambala", "Panipat", "Hisar"],
    "Himachal Pradesh": ["Shimla", "Manali", "Dharamshala", "Solan", "Mandi", "Bilaspur"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Hazaribagh", "Deoghar"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum", "Gulbarga"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Malappuram", "Kannur"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain", "Sagar"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad"],
    "Manipur": ["Imphal", "Thoubal", "Bishnupur", "Churachandpur", "Senapati", "Ukhrul"],
    "Meghalaya": ["Shillong", "Tura", "Jowai", "Nongstoin", "Baghmara", "Williamnagar"],
    "Mizoram": ["Aizawl", "Lunglei", "Champhai", "Serchhip", "Kolasib", "Saiha"],
    "Nagaland": ["Kohima", "Dimapur", "Mokokchung", "Tuensang", "Wokha", "Zunheboto"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Sambalpur", "Brahmapur", "Balasore"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner", "Ajmer"],
    "Sikkim": ["Gangtok", "Namchi", "Gyalshing", "Mangan", "Jorethang", "Rangpo"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli", "Tiruppur"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Ramagundam"],
    "Tripura": ["Agartala", "Udaipur", "Dharmanagar", "Kailashahar", "Ambassa", "Belonia"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Prayagraj"],
    "Uttarakhand": ["Dehradun", "Haridwar", "Rishikesh", "Haldwani", "Nainital", "Rudrapur"],
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
        # Create a canvas with vertical and horizontal scrollbars
        canvas = tk.Canvas(parent, bg=COLORS['card'], highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)

        # Create a frame inside the canvas
        scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')
        
        # Update the scroll region when the frame changes size
        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", update_scroll_region)

        # Attach the frame to the canvas
        frame_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Configure scrolling
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Pack scrollbars and canvas
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

    # Enable scrolling with the mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)  # For Windows
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # For Linux (scroll up)
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # For Linux (scroll down)

        return scrollable_frame, canvas

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
        city_label = ttk.Label(location_frame, text="🏙 City", style='Subtitle.TLabel')
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
    def __init__(self, root):  # ✅ Corrected
        self.root = root
        self.root.title("CrowdNest")
        self.root.state('zoomed')
        
        # Initialize database handler
        self.db = DatabaseHandler()
        
        # Initialize current user
        self.current_user = None
        
        # Initialize dictionaries
        self.profile_labels = {}
        self.profile_entries = {}
        self.donation_entries = {}
        
        # Initialize location variables
        self.reg_state_var = tk.StringVar()
        self.reg_city_var = tk.StringVar()
        self.donation_state_var = tk.StringVar()
        self.donation_city_var = tk.StringVar()
        self.profile_state_var = tk.StringVar()
        self.profile_city_var = tk.StringVar()
        
        # Initialize filter variables
        self.category_filter = tk.StringVar()
        self.condition_filter = tk.StringVar()
        self.location_filter = tk.StringVar()
        
        # Configure styles
        CustomStyle.configure_styles()
        
        # Create main container
        self.container = ttk.Frame(root)
        self.container.pack(fill='both', expand=True)
        
        # Create frames dictionary
        self.frames = {}
        
        # Create and show login frame
        self.content_frame = ttk.Frame(self.container, style='Content.TFrame')
        self.content_frame.pack(fill='both', expand=True, side='right')
        
        # Create navigation pane (initially hidden)
        self.nav_pane = NavigationPane(self.container, self.show_frame)
        
        
        # Create all frames
        self.create_login_frame()
        self.create_register_frame()
        self.create_dashboard_frame()
        self.create_donation_form_frame()
        self.create_donation_list_frame()
        self.create_chat_frame()
        self.create_profile_frame()
        
        # Show login frame
        self.show_frame('login')

    def login(self):
        username = self.login_username.get()
        password = self.login_password.get()
        
        user = self.db.verify_user(username, password)
        if user:
            self.current_user = user
            self.nav_pane.pack(fill='y', side='left')
            self.show_frame('dashboard')
            self.update_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def register(self):
        # Get form data from dictionary
        username = self.reg_entries["Username"].get()
        email = self.reg_entries["Email"].get()
        password = self.reg_entries["Password"].get()
        confirm_password = self.reg_entries["Confirm Password"].get()

        # Get location data
        state = self.reg_state_var.get()
        city = self.reg_city_var.get()

        # Validate inputs
        if not all([username, email, password, confirm_password, state, city]):
            messagebox.showerror("Error", "All fields are required")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
            return

        if '@' not in email:
            messagebox.showerror("Error", "Invalid email format")
            return

        # Combine state and city
        location = f"{city}, {state}"

        # Create user in the database
        if self.db.create_user(username, password, email, location):
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.show_frame('login')
        else:
            messagebox.showerror("Error", "Username or email already exists")


    def submit_donation(self):
        # Get form data
        title = self.donation_title.get()
        description = self.donation_description.get("1.0", "end-1c")
        category = self.donation_category_var.get()
        condition = self.donation_condition_var.get()
        state = self.donation_state_var.get()
        city = self.donation_city_var.get()
        
        # Validate inputs
        if not all([title, description, category, condition, state, city]):
            messagebox.showerror("Error", "All fields are required")
            return
            
        # Combine state and city
        location = f"{city}, {state}"
        
        # Create donation
        if self.db.create_donation(
            self.current_user['unique_id'],
            title,
            description,
            category,
            condition,
            location,
            None  # image_path
        ):
            messagebox.showinfo("Success", "Donation created successfully!")
            self.show_frame('donation_list')
        else:
            messagebox.showerror("Error", "Failed to create donation")

    def search_donations(self):
        search_term = self.search_entry.get()
        donations = self.db.get_donations(search_term)
        self.update_donation_list(donations)

    def send_message(self):
        if not self.message_entry.get():
            return
            
        if self.db.send_message(
            self.current_user['unique_id'],
            self.selected_chat_user['unique_id'],
            self.message_entry.get()
        ):
            self.message_entry.delete(0, 'end')
            self.update_chat_messages()
        else:
            messagebox.showerror("Error", "Failed to send message")

    def save_profile_changes(self):
        email = self.profile_email.get()
        state = self.profile_state_var.get()
        city = self.profile_city_var.get()
        location = f"{city}, {state}"
        
        if self.db.update_profile(
            self.current_user['unique_id'],
            email=email,
            location=location
        ):
            messagebox.showinfo("Success", "Profile updated successfully!")
            self.current_user['email'] = email
            self.current_user['location'] = location
            self.update_profile_display()
        else:
            messagebox.showerror("Error", "Failed to update profile")

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
        self.login_username = ModernUI.create_entry(content, "Username", width=40)
        self.login_username.pack(pady=10)
        
        self.login_password = ModernUI.create_entry(content, "Password", show="•", width=40)
        self.login_password.pack(pady=10)
        
        # Buttons
        ModernUI.create_button(content, "Sign In", self.login, width=40).pack(pady=20)
        ttk.Label(content, text="Don't have an account?", style='Subtitle.TLabel').pack(pady=(20, 5))
        ModernUI.create_button(content, "Create Account", 
                             lambda: self.show_frame('register'), 
                             style='Secondary.TButton', width=40).pack()
        
        self.frames['login'] = frame

    def create_register_frame(self):
        # Create a main frame inside content_frame
        frame = ModernUI.create_card(self.content_frame, padding=(40, 40))

        # Create a canvas for scrollability
        canvas = tk.Canvas(frame, bg=COLORS['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)

        # Create a scrollable frame inside the canvas
        scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')
        frame_window = canvas.create_window(0, 0, window=scrollable_frame, anchor="n", width=500)

        # Scroll configuration
        def update_window_position():
            canvas.itemconfig(frame_window, width=canvas.winfo_width())

        canvas.after(200, update_window_position)
        canvas.bind("<Configure>", lambda event: update_window_position())

        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", update_scroll_region)

        # Enable mouse scrolling
        def _on_mouse_wheel(event):
            if event.num == 5 or event.delta == -120:
                canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta == 120:
                canvas.yview_scroll(-1, "units")

        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
        canvas.bind_all("<Button-4>", _on_mouse_wheel)
        canvas.bind_all("<Button-5>", _on_mouse_wheel)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Wrapper frame
        wrapper_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        wrapper_frame.pack(fill='both', expand=True)

        # Content frame
        content = ttk.Frame(wrapper_frame, style='Card.TFrame')
        content.pack(pady=40, padx=20, anchor="center")

        # Header section
        ttk.Label(content, text="🎁", font=('Poppins', 40), foreground=COLORS['primary']).pack(anchor="center")
        ttk.Label(content, text="Create Account", font=('Poppins', 20, 'bold'), foreground=COLORS['text']).pack(pady=(5, 2), anchor="center")
        ttk.Label(content, text="Join our community and start sharing!", font=('Poppins', 12), foreground=COLORS['text_light']).pack(anchor="center")

        # Initialize registration entries dictionary
        self.reg_entries = {}

        # Registration form fields
        form_fields = [
            ("👤 Username", "Username", "Enter your username"),
            ("📧 Email", "Email", "Enter your email"),
            ("🔒 Password", "Password", "Enter your password", "•"),
            ("🔒 Confirm Password", "Confirm Password", "Re-enter your password", "•")
        ]

        for label_text, dict_key, placeholder, *password_mode in form_fields:
            field_frame = ttk.Frame(content, style='Card.TFrame')
            field_frame.pack(fill='x', pady=(8, 10), padx=40)

            ttk.Label(field_frame, text=label_text, font=('Poppins', 11, 'bold'), foreground=COLORS['text']).pack(anchor='w')

            show_char = password_mode[0] if password_mode else None
            entry = ModernUI.create_entry(field_frame, placeholder=placeholder, show=show_char, width=40)
            entry.pack(pady=(5, 0), ipadx=5, ipady=10)

            self.reg_entries[dict_key] = entry  # Store in dictionary

            # Password Strength Indicator
            if label_text == "🔒 Password":
                self.password_strength_label = ttk.Label(field_frame, text="Password Strength: Weak", font=('Poppins', 10), foreground="red")
                self.password_strength_label.pack(anchor='w', pady=(5, 10))
                entry.bind('<KeyRelease>', self.check_password_strength)

        # Initialize state and city variables
        self.reg_state_var = tk.StringVar()
        self.reg_city_var = tk.StringVar()

        # Location selector
        ttk.Label(content, text="📍 Location", font=('Poppins', 11, 'bold'), foreground=COLORS['text']).pack(anchor='center', padx=20)
        location_selector = ModernUI.create_location_selector(content, self.reg_state_var, self.reg_city_var)
        location_selector.pack(fill='x', pady=(5, 20), padx=40)

        # Buttons
        button_frame = ttk.Frame(content, style='Card.TFrame')
        button_frame.pack(fill='x', pady=20, padx=40)

        ModernUI.create_button(button_frame, "✅ Create Account", self.register, width=25).pack(side='left', padx=5, pady=5)
        ModernUI.create_button(button_frame, "🔙 Back to Login", lambda: self.show_frame('login'), style='Secondary.TButton', width=25).pack(side='right', padx=5, pady=5)

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
        location_selector = ModernUI.create_location_selector(loc_frame, self.donation_state_var, self.donation_city_var)
        location_selector.pack(fill='x')
        
        # Store the location variables
        self.donation_entries['State:'] = self.donation_state_var
        self.donation_entries['City:'] = self.donation_city_var
        
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
        
        # Location selector
        location_frame = ttk.Frame(info_frame, style='Card.TFrame')
        location_frame.pack(fill='x', pady=5)
        ttk.Label(location_frame, text="Location:", style='Subtitle.TLabel').pack(anchor='w')
        location_selector = ModernUI.create_location_selector(location_frame, self.profile_state_var, self.profile_city_var)
        location_selector.pack(pady=(5, 10))
        
        # Store location variables
        self.profile_entries['State:'] = self.profile_state_var
        self.profile_entries['City:'] = self.profile_city_var
        
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
            "Back to Dashboard",
            lambda: self.show_frame('dashboard'),
            style='Secondary.TButton',
            width=20
        ).pack(side='right', padx=5)
        
        self.frames['profile'] = frame

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
            'state': self.donation_state_var.get(),
            'city': self.donation_city_var.get()
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
        
        response = self.db.send_request(data)
        
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

    def check_password_strength(self, event=None):
        """Check password strength and update the indicator"""
        if not hasattr(self, 'reg_entries') or 'Password' not in self.reg_entries:
            return
            
        password = self.reg_entries['Password'].get()
        strength = 0
        
        # Length check
        if len(password) >= 8:
            strength += 1
            
        # Digit check
        if any(char.isdigit() for char in password):
            strength += 1
            
        # Uppercase check
        if any(char.isupper() for char in password):
            strength += 1
            
        # Lowercase check
        if any(char.islower() for char in password):
            strength += 1
            
        # Special character check
        if any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in password):
            strength += 1
            
        # Update label based on strength
        if strength == 0:
            self.password_strength_label.config(text="Password Strength: Very Weak", foreground=COLORS['error'])
        elif strength == 1 or strength == 2:
            self.password_strength_label.config(text="Password Strength: Weak", foreground=COLORS['warning'])
        elif strength == 3:
            self.password_strength_label.config(text="Password Strength: Moderate", foreground=COLORS['accent'])
        elif strength == 4:
            self.password_strength_label.config(text="Password Strength: Strong", foreground=COLORS['success'])
        else:
            self.password_strength_label.config(text="Password Strength: Very Strong", foreground=COLORS['success'])

if __name__ == "__main__":
    root = tk.Tk()
    app = CrowdNestApp(root)
    root.mainloop()
