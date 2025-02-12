import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database_handler import DatabaseHandler
from PIL import Image, ImageTk
import os, io
from datetime import datetime
import uuid
import socket
import json
import threading

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
            if (selected_state in CITIES_BY_STATE):
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
        self.root.state('zoomed')
        
        self.db = DatabaseHandler()
        self.current_user = None
        self.chat_socket = None
        self.selected_chat_user = None
        self.selected_image_path = None
        
        # Initialize UI variables
        self.init_variables()
        
        # Configure styles
        CustomStyle.configure_styles()
        
        # Create main container and frames
        self.setup_main_container()
        self.create_frames()
        
        # Show login frame
        self.show_frame('login')
    
    def init_variables(self):
        """Initialize all UI variables in one place"""
        self.profile_labels = {}
        self.profile_entries = {}
        self.donation_entries = {}
        
        # StringVars
        self.reg_state_var = tk.StringVar()
        self.reg_city_var = tk.StringVar()
        self.donation_state_var = tk.StringVar()
        self.donation_city_var = tk.StringVar()
        self.profile_state_var = tk.StringVar()
        self.profile_city_var = tk.StringVar()
        self.category_filter = tk.StringVar()
        self.condition_filter = tk.StringVar()
        self.location_filter = tk.StringVar()
        self.donation_title = tk.StringVar()
        self.donation_description = tk.StringVar()
        self.donation_category_var = tk.StringVar()
        self.donation_condition_var = tk.StringVar()
    
    def setup_main_container(self):
        """Setup the main container and navigation"""
        self.container = ttk.Frame(self.root)
        self.container.pack(fill='both', expand=True)
        
        self.content_frame = ttk.Frame(self.container, style='Content.TFrame')
        self.content_frame.pack(fill='both', expand=True, side='right')
        
        self.nav_pane = NavigationPane(self.container, self.show_frame)
    
    def create_frames(self):
        """Create all application frames"""
        self.frames = {}
        self.create_login_frame()
        self.create_register_frame()
        self.create_dashboard_frame()
        self.create_donation_form_frame()
        self.create_donation_list_frame()
        self.create_chat_frame()
        self.create_profile_frame()

    def login(self):
        username = self.login_username.get()
        password = self.login_password.get()
        
        user = self.db.verify_user(username, password)
        if user:
            self.current_user = user
            self.nav_pane.pack(fill='y', side='left')
            self.show_frame('dashboard')
            self.update_dashboard()
            self.connect_to_chat_server()
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
        title = self.donation_entries['Title:'].get()
        description = self.donation_entries['Description:'].get("1.0", "end-1c")
        category = self.donation_entries['Category:'].get()
        condition = self.donation_entries['Condition:'].get()
        state = self.donation_state_var.get()
        city = self.donation_city_var.get()
        
        # Validate inputs
        if not all([title, description, category, condition, state, city]):
            messagebox.showerror("Error", "All fields except image are required")
            return
            
        # Process image if selected
        image_data = None
        if self.selected_image_path:
            try:
                with open(self.selected_image_path, 'rb') as img_file:
                    image_data = img_file.read()
            except Exception as e:
                messagebox.showwarning("Warning", f"Could not process image: {e}")
        
        # Combine state and city
        location = f"{city}, {state}"
        
        # Create donation
        success, message = self.db.create_donation(
            self.current_user['unique_id'],
            title,
            description,
            category,
            condition,
            location,
            image_data
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.show_frame('donation_list')
        else:
            messagebox.showerror("Error", message)

    def choose_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            try:
                # Create images directory if it doesn't exist
                image_dir = "donation_images"
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)
                
                # Copy image to application directory with unique name
                file_ext = os.path.splitext(file_path)[1]
                new_filename = f"donation_{uuid.uuid4()}{file_ext}"
                new_path = os.path.join(image_dir, new_filename)
                
                # Copy and resize image
                with Image.open(file_path) as img:
                    # Resize image while maintaining aspect ratio
                    max_size = (800, 800)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(new_path)
                
                self.selected_image_path = new_path
                messagebox.showinfo("Success", "Image uploaded successfully!")
                
                # Update image preview if it exists
                if hasattr(self, 'image_preview_label'):
                    self.update_image_preview()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process image: {str(e)}")
                self.selected_image_path = None

    def update_image_preview(self):
        if self.selected_image_path and os.path.exists(self.selected_image_path):
            try:
                # Load and resize image for preview
                with Image.open(self.selected_image_path) as img:
                    # Resize image for preview
                    preview_size = (200, 200)
                    img.thumbnail(preview_size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    # Update preview label
                    self.image_preview_label.configure(image=photo)
                    self.image_preview_label.image = photo  # Keep a reference
            except Exception as e:
                print(f"Error updating preview: {e}")

    def search_donations(self):
        search_term = self.search_entry.get()
        donations = self.db.get_donations(search_term)
        self.update_donation_list(donations)

    def send_message(self):
        if not self.message_entry.get() or not self.selected_chat_user:
            return
            
        content = self.message_entry.get()
        
        # Send via socket for real-time chat
        try:
            message_data = json.dumps({
                'receiver_id': self.selected_chat_user['unique_id'],
                'content': content
            })
            self.chat_socket.send(message_data.encode())
        except:
            messagebox.showerror("Error", "Failed to send message")
            return
            
        # Store in database
        self.db.send_message(
            self.current_user['unique_id'],
            self.selected_chat_user['unique_id'],
            content
        )
        
        self.message_entry.delete(0, 'end')
        self.add_message_to_chat(self.current_user['unique_id'], content)

    def save_profile_changes(self):
        """Save profile changes to database"""
        # Get values from profile entries
        email = self.profile_entries['Email:'].get()
        state = self.profile_state_var.get()
        city = self.profile_city_var.get()
        
        # Validate inputs
        if not email:
            messagebox.showerror("Error", "Email is required")
            return
            
        if not state or not city or state == "Select State" or city == "Select City":
            messagebox.showerror("Error", "Please select your location")
            return
            
        # Validate email format
        if not self.validate_email(email):
            messagebox.showerror("Error", "Invalid email format")
            return
        
        # Combine location
        location = f"{city}, {state}"
        
        # Update profile in database
        success, message = self.db.update_profile(
            self.current_user['unique_id'],
            email=email,
            location=location
        )
        
        if success:
            messagebox.showinfo("Success", "Profile updated successfully!")
            self.current_user['email'] = email
            self.current_user['location'] = location
            self.update_profile_display()
        else:
            messagebox.showerror("Error", message)

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

    def check_password_strength(self, event):
        """Check password strength and update indicator"""
        password = self.reg_entries["Password"].get()
        
        # Initialize strength score
        strength = 0
        feedback = []
        
        # Length check
        if len(password) >= 8:
            strength += 1
        else:
            feedback.append("Length should be at least 8 characters")
            
        # Check for uppercase
        if any(c.isupper() for c in password):
            strength += 1
        else:
            feedback.append("Should contain uppercase letters")
            
        # Check for lowercase
        if any(c.islower() for c in password):
            strength += 1
        else:
            feedback.append("Should contain lowercase letters")
            
        # Check for numbers
        if any(c.isdigit() for c in password):
            strength += 1
        else:
            feedback.append("Should contain numbers")
            
        # Check for special characters
        if any(not c.isalnum() for c in password):
            strength += 1
        else:
            feedback.append("Should contain special characters")
            
        # Update strength label
        if strength == 0:
            self.password_strength_label.config(
                text="Password Strength: Very Weak",
                foreground="red"
            )
        elif strength == 1:
            self.password_strength_label.config(
                text="Password Strength: Weak",
                foreground="red"
            )
        elif strength == 2:
            self.password_strength_label.config(
                text="Password Strength: Fair",
                foreground="orange"
            )
        elif strength == 3:
            self.password_strength_label.config(
                text="Password Strength: Good",
                foreground=COLORS['warning']
            )
        elif strength == 4:
            self.password_strength_label.config(
                text="Password Strength: Strong",
                foreground=COLORS['success']
            )
        else:
            self.password_strength_label.config(
                text="Password Strength: Very Strong",
                foreground=COLORS['success']
            )

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
        self.donation_title.set(title_entry.get())
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
        self.donation_description.set(desc_text.get("1.0", tk.END).strip())
        self.desc_counter = ttk.Label(desc_frame, text="0/500", style='Subtitle.TLabel')
        self.desc_counter.pack(side='left', padx=10, anchor='n')
        desc_text.bind('<KeyRelease>', lambda e: self.update_char_counter(desc_text, self.desc_counter, 500, is_text=True))
        
        # Category dropdown with icon
        cat_frame = ttk.Frame(content, style='Card.TFrame')
        cat_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(cat_frame, text="📦 Category", style='Subtitle.TLabel').pack(anchor='w')
        self.donation_entries['Category:'] = ModernUI.create_dropdown(cat_frame, CATEGORIES, "Select Category", width=47)
        self.donation_entries['Category:'].pack(pady=(5, 0))
        self.donation_category_var.set(self.donation_entries['Category:'].get())
        
        # Condition dropdown with icon
        cond_frame = ttk.Frame(content, style='Card.TFrame')
        cond_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(cond_frame, text="✨ Condition", style='Subtitle.TLabel').pack(anchor='w')
        self.donation_entries['Condition:'] = ModernUI.create_dropdown(cond_frame, CONDITIONS, "Select Condition", width=47)
        self.donation_entries['Condition:'].pack(pady=(5, 0))
        self.donation_condition_var.set(self.donation_entries['Condition:'].get())
        
        # Replace the old location dropdown with new location selector
        loc_frame = ttk.Frame(content, style='Card.TFrame')
        loc_frame.pack(fill='x', pady=(0, 20))
        location_selector = ModernUI.create_location_selector(loc_frame, self.donation_state_var, self.donation_city_var)
        location_selector.pack(fill='x')
        
        # Store the location variables
        self.donation_entries['State:'] = self.donation_state_var
        self.donation_entries['City:'] = self.donation_city_var
        
        # Image upload section
        img_frame = ttk.Frame(content, style='Card.TFrame')
        img_frame.pack(fill='x', pady=(0, 20))
        
        # Image preview label
        self.image_preview_label = ttk.Label(img_frame)
        self.image_preview_label.pack(pady=10)
        
        # Image upload button
        
        # Image upload (placeholder for future implementation)
        img_frame = ttk.Frame(content, style='Card.TFrame')
        img_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(img_frame, text="📸 Upload Images", style='Subtitle.TLabel').pack(anchor='w')
        upload_button = ModernUI.create_button(
            img_frame, 
            "📸 Choose Image", 
            self.choose_image, 
            style='Secondary.TButton'
        )
        upload_button.pack(pady=5)
        
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
        columns = ('Title', 'Category', 'Condition', 'Location', 'Donor', 'Status', 'Date', 'DonorId')
        self.donations_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure headings and columns
        column_widths = {
            'Title': 200,
            'Category': 150,
            'Condition': 100,
            'Location': 150,
            'Donor': 100,
            'Status': 100,
            'Date': 100
        }
        
        for col, width in column_widths.items():
            self.donations_tree.heading(col, text=col)
            self.donations_tree.column(col, width=width)
        
        # Hide the DonorId column
        self.donations_tree['displaycolumns'] = columns[:-1]
        
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
        
        ModernUI.create_button(
            button_frame,
            "Track Delivery",
            self.track_delivery,
            width=20
        ).pack(side='left', padx=5)
        
        self.frames['donation_list'] = frame

    def create_chat_frame(self):
        frame = ModernUI.create_card(self.content_frame)
        
        # Create scrollable main container
        main_canvas = tk.Canvas(frame, bg=COLORS['card'], highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas, style='Card.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Pack scrollbar and canvas
        main_scrollbar.pack(side="right", fill="y")
        main_canvas.pack(side="left", fill="both", expand=True)
        
        # Header
        header_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        header_frame.pack(fill='x', pady=(20, 30))
        
        ttk.Label(header_frame, text="Messages", style='Title.TLabel').pack()
        ttk.Label(header_frame, text="Chat with donors and recipients", style='Subtitle.TLabel').pack()
        
        # Chat container with contacts and messages
        chat_container = ttk.Frame(scrollable_frame, style='Card.TFrame')
        chat_container.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Contacts section
        contacts_frame = ttk.Frame(chat_container, style='Card.TFrame', width=300)
        contacts_frame.pack_propagate(False)
        contacts_frame.pack(side='left', fill='y', padx=(0, 20))
        
        # Contacts header
        ttk.Label(contacts_frame, text="Recent Chats", style='Subtitle.TLabel').pack(pady=10)
        
        # Contacts list with scrollbar
        contacts_canvas = tk.Canvas(contacts_frame, bg=COLORS['card'], highlightthickness=0)
        contacts_scrollbar = ttk.Scrollbar(contacts_frame, orient="vertical", command=contacts_canvas.yview)
        self.contacts_list = ttk.Frame(contacts_canvas, style='Card.TFrame')
        
        contacts_canvas.create_window((0, 0), window=self.contacts_list, anchor="nw", width=280)
        contacts_canvas.configure(yscrollcommand=contacts_scrollbar.set)
        
        contacts_scrollbar.pack(side="right", fill="y")
        contacts_canvas.pack(side="left", fill="both", expand=True)
        
        # Message area
        message_frame = ttk.Frame(chat_container, style='Card.TFrame')
        message_frame.pack(side='left', fill='both', expand=True)
        
        # Message history with scrollbar
        history_frame = ttk.Frame(message_frame, style='Card.TFrame')
        history_frame.pack(fill='both', expand=True)
        
        self.message_canvas = tk.Canvas(history_frame, bg=COLORS['card'], highlightthickness=0)
        message_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.message_canvas.yview)
        self.message_text = tk.Text(self.message_canvas, wrap='word', state='disabled')
        self.message_text.configure(font=('Segoe UI', 10), padx=10, pady=10)
        
        self.message_canvas.create_window((0, 0), window=self.message_text, anchor="nw")
        self.message_canvas.configure(yscrollcommand=message_scrollbar.set)
        
        message_scrollbar.pack(side="right", fill="y")
        self.message_canvas.pack(side="left", fill="both", expand=True)
        
        # Message input area
        input_frame = ttk.Frame(message_frame, style='Card.TFrame')
        input_frame.pack(fill='x', pady=10)
        
        self.message_entry = ModernUI.create_entry(input_frame, "Type your message...", width=50)
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        ModernUI.create_button(input_frame, "Send", self.send_message).pack(side='right')
        
        self.frames['chat'] = frame

    def update_contacts_list(self):
        """Update the contacts list with recent conversations"""
        # Clear existing contacts
        for widget in self.contacts_list.winfo_children():
            widget.destroy()
        
        # Get conversations
        conversations = self.db.get_user_conversations(self.current_user['unique_id'])
        
        for conv in conversations:
            contact_frame = ttk.Frame(self.contacts_list, style='Card.TFrame')
            contact_frame.pack(fill='x', pady=2)
            
            # Contact button with handler
            contact_btn = tk.Button(
                contact_frame,
                text=conv['username'],
                font=('Segoe UI', 10),
                bg=COLORS['card'],
                fg=COLORS['text'],
                anchor='w',
                padx=10,
                pady=5,
                relief='flat',
                command=lambda u=conv: self.select_contact(u)
            )
            contact_btn.pack(fill='x')
            
            # Add hover effect
            contact_btn.bind('<Enter>', lambda e, btn=contact_btn: btn.configure(bg=COLORS['background']))
            contact_btn.bind('<Leave>', lambda e, btn=contact_btn: btn.configure(bg=COLORS['card']))

    def select_contact(self, user):
        """Handle contact selection"""
        self.selected_chat_user = user
        
        # Get conversation history
        messages = self.db.get_conversation_messages(
            self.current_user['unique_id'],
            user['unique_id']
        )
        
        # Update message display
        self.message_text.configure(state='normal')
        self.message_text.delete('1.0', tk.END)
        for msg in messages:
            sender = "You: " if msg['sender_id'] == self.current_user['unique_id'] else f"{msg['sender_name']}: "
            self.message_text.insert('end', f"{sender}{msg['content']}\n")
        self.message_text.configure(state='disabled')
        self.message_text.see('end')

    def contact_donor(self, item=None):
        """Contact a donor about their donation"""
        if not item:
            selection = self.donations_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a donation first")
                return
            item = selection[0]
        
        donation = self.donations_tree.item(item)
        donor_id = donation['values'][7]  # Get donor_id from values
        
        # Don't allow contacting yourself
        if donor_id == self.current_user['unique_id']:
            messagebox.showwarning("Warning", "This is your own donation")
            return
        
        # Get donor info
        donor = self.db.get_user_by_id(donor_id)
        if donor:
            self.selected_chat_user = donor
            self.show_frame('chat')
            self.update_contacts_list()  # Refresh contacts list
            self.select_contact(donor)  # Show conversation with donor
        else:
            messagebox.showerror("Error", "Could not find donor information")

    def update_messages(self):
        """Update message list and chat area"""
        if not self.current_user:
            return
        
        self.update_contacts_list()
        
        # Clear message area
        self.message_text.configure(state='normal')
        self.message_text.delete('1.0', tk.END)
        self.message_text.configure(state='disabled')

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
            'Title': self.donation_entries['Title:'].get(),
            'Description': self.donation_entries['Description:'].get("1.0", tk.END).strip(),
            'Category': self.donation_entries['Category:'].get(),
            'Condition': self.donation_entries['Condition:'].get(),
            'State': self.donation_state_var.get(),
            'City': self.donation_city_var.get()
        }
        
        # Create preview window
        preview = tk.Toplevel(self.root)
        preview.title("Preview Donation")
        preview.geometry("600x500")
        preview.configure(bg=COLORS['card'])
        
        # Preview content
        content = ttk.Frame(preview, style='Card.TFrame')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(content, text="Donation Preview", style='Title.TLabel').pack(pady=(0, 20))
        
        for key, value in data.items():
            if value and value != "Select Category" and value != "Select Condition" and value != "Select State" and value != "Select City":
                label = key.replace(':', '')
                ttk.Label(content, text=f"{label}:", style='Subtitle.TLabel').pack(anchor='w')
                ttk.Label(content, text=value, style='Subtitle.TLabel', wraplength=500, justify='left').pack(anchor='w', pady=(0, 10))
        
        # Add a close button
        close_button = ModernUI.create_button(content, "Close", preview.destroy, style='Secondary.TButton', width=20)
        close_button.pack(pady=20)

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
        values = donation['values']
        
        details = tk.Toplevel(self.root)
        details.title("Donation Details")
        details.geometry("800x600")
        details.configure(bg=COLORS['card'])
        
        content = ttk.Frame(details, style='Card.TFrame')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(content, text=values[0], style='Title.TLabel').pack(pady=(0, 20))
        
        # Handle image loading more safely
        image_data = donation.get('image_data')
        if image_data:
            try:
                # If image_data is bytes, use BytesIO
                if isinstance(image_data, bytes):
                    image = Image.open(io.BytesIO(image_data))
                # If image_data is a file path, open directly
                elif isinstance(image_data, str) and os.path.exists(image_data):
                    image = Image.open(image_data)
                else:
                    raise ValueError("Invalid image data")
                    
                image.thumbnail((400, 400))
                photo = ImageTk.PhotoImage(image)
                img_label = ttk.Label(content, image=photo)
                img_label.image = photo  # Keep reference
                img_label.pack(pady=10)
            except Exception as e:
                print(f"Error displaying image: {e}")
        
        # Details grid
        details_frame = ttk.Frame(content, style='Card.TFrame')
        details_frame.pack(fill='x', pady=20)
        
        labels = ['Category:', 'Condition:', 'Location:', 'Donor:', 'Posted:']
        for i, (label, value) in enumerate(zip(labels, values[1:-1])):
            row = ttk.Frame(details_frame, style='Card.TFrame')
            row.pack(fill='x', pady=5)
            ttk.Label(row, text=label, style='Subtitle.TLabel', width=15).pack(side='left')
            ttk.Label(row, text=str(value), style='Subtitle.TLabel').pack(side='left', padx=10)
        
        # Description
        desc_frame = ttk.Frame(content, style='Card.TFrame')
        desc_frame.pack(fill='x', pady=20)
        ttk.Label(desc_frame, text="Description:", style='Subtitle.TLabel').pack(anchor='w')
        desc_text = tk.Text(desc_frame, height=4, wrap='word', font=('Segoe UI', 10))
        desc_text.insert('1.0', donation['description'])
        desc_text.configure(state='disabled')
        desc_text.pack(fill='x', pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(content, style='Card.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        if values[4] != self.current_user['username']:  # Don't show request button for own donations
            ModernUI.create_button(
                button_frame, 
                "Request Item", 
                lambda: self.request_donation(item),
                width=20
            ).pack(side='left', padx=5)
            
            ModernUI.create_button(
                button_frame,
                "Contact Donor",
                lambda: self.contact_donor(item),
                width=20
            ).pack(side='left', padx=5)
        
        ModernUI.create_button(
            button_frame,
            "Close",
            details.destroy,
            style='Secondary.TButton',
            width=20
        ).pack(side='right', padx=5)

    def request_donation(self, item):
        donation = self.donations_tree.item(item)
        values = donation['values']
        
        # Create request window
        request_window = tk.Toplevel(self.root)
        request_window.title(f"Request: {values[0]}")
        request_window.geometry("600x500")
        request_window.configure(bg=COLORS['card'])
        
        content = ttk.Frame(request_window, style='Card.TFrame')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Donation summary
        ttk.Label(content, text="Request Donation", style='Title.TLabel').pack(pady=(0, 20))
        
        summary_frame = ttk.Frame(content, style='Card.TFrame')
        summary_frame.pack(fill='x', pady=10)
        
        ttk.Label(summary_frame, text=f"Item: {values[0]}", style='Subtitle.TLabel').pack(anchor='w')
        ttk.Label(summary_frame, text=f"From: {values[4]}", style='Subtitle.TLabel').pack(anchor='w')
        
        # Message input
        ttk.Label(content, text="Your Message:", style='Subtitle.TLabel').pack(anchor='w', pady=(20, 5))
        message = tk.Text(content, height=6, width=50, wrap='word')
        message.configure(font=('Segoe UI', 10))
        message.pack(pady=5)
        
        # Message templates
        templates_frame = ttk.Frame(content, style='Card.TFrame')
        templates_frame.pack(fill='x', pady=10)
        
        ttk.Label(templates_frame, text="Quick Templates", style='Subtitle.TLabel').pack(anchor='w')
        
        templates = [
            "Hi, I'm interested in your donation. Is it still available?",
            "Hello! I would like to request this item. When would be a good time to arrange pickup?",
            "Greetings! I'm in need of this item. Could we discuss the details?"
        ]
        
        for template in templates:
            ModernUI.create_button(
                templates_frame,
                "Use Template",
                lambda t=template: message.delete('1.0', tk.END) or message.insert('1.0', t),
                style='Secondary.TButton'
            ).pack(anchor='w', pady=2)
        
        # Submit button
        ModernUI.create_button(
            content,
            "Send Request",
            lambda: self.submit_request(donation['values'][6], message.get('1.0', tk.END).strip(), request_window),
            width=30
        ).pack(pady=20)

    def submit_request(self, donation_id, message, window):
        if not message:
            messagebox.showwarning("Warning", "Please enter a message")
            return
        
        # Get estimated delivery date
        date_window = tk.Toplevel(self.root)
        date_window.title("Estimated Delivery Date")
        date_window.geometry("400x200")
        date_window.configure(bg=COLORS['card'])
        
        content = ttk.Frame(date_window, style='Card.TFrame')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(content, text="Select Estimated Delivery Date", style='Subtitle.TLabel').pack(pady=(0, 10))
        
        # Date picker (you might want to use a calendar widget here)
        date_entry = ModernUI.create_entry(content, "YYYY-MM-DD", width=30)
        date_entry.pack(pady=10)
        
        def submit_with_date():
            estimated_date = date_entry.get()
            try:
                datetime.strptime(estimated_date, '%Y-%m-%d')
                success, response = self.db.create_request(
                    self.current_user['unique_id'],
                    donation_id,
                    message
                )
                
                if success:
                    # Create delivery record
                    delivery_success, tracking_number = self.db.create_delivery(
                        donation_id,
                        self.current_user['unique_id'],
                        estimated_date
                    )
                    
                    if delivery_success:
                        messagebox.showinfo("Success", f"Request sent successfully!\nTracking Number: {tracking_number}")
                        window.destroy()
                        date_window.destroy()
                        self.search_donations()
                    else:
                        messagebox.showerror("Error", "Failed to create delivery record")
                else:
                    messagebox.showerror("Error", response)
                    
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
        
        ModernUI.create_button(content, "Submit", submit_with_date, width=30).pack(pady=20)

    def validate_email(self, email):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email)

    def track_delivery(self):
        """Track delivery status"""
        # Get tracking number from user
        tracking_window = tk.Toplevel(self.root)
        tracking_window.title("Track Delivery")
        tracking_window.geometry("400x200")
        tracking_window.configure(bg=COLORS['card'])
        
        content = ttk.Frame(tracking_window, style='Card.TFrame')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(content, text="Enter Tracking Number", style='Title.TLabel').pack(pady=(0, 20))
        tracking_entry = ModernUI.create_entry(content, "Enter tracking number", width=30)
        tracking_entry.pack(pady=10)
        
        def check_status():
            tracking_number = tracking_entry.get()
            if not tracking_number:
                messagebox.showwarning("Warning", "Please enter tracking number")
                return
                
            status = self.db.get_delivery_status(tracking_number)
            if status:
                messagebox.showinfo("Delivery Status", 
                    f"Status: {status['status']}\n"
                    f"Item: {status['donation_title']}\n"
                    f"From: {status['donor_name']}\n"
                    f"To: {status['requester_name']}\n"
                    f"Estimated: {status['estimated_date']}\n"
                    f"Actual: {status['actual_date'] or 'Not delivered yet'}"
                )
            else:
                messagebox.showerror("Error", "Invalid tracking number")
                
        ModernUI.create_button(content, "Check Status", check_status, width=30).pack(pady=20)

    def add_message_to_chat(self, sender_id, content):
        """Add a message to the chat window"""
        self.message_text.configure(state='normal')
        sender = "You: " if sender_id == self.current_user['unique_id'] else f"{self.selected_chat_user['username']}: "
        self.message_text.insert('end', f"{sender}{content}\n")
        self.message_text.configure(state='disabled')
        self.message_text.see('end')

    def connect_to_chat_server(self):
        """Connect to chat server"""
        try:
            self.chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.chat_socket.connect(('localhost', 5000))
            
            # Send authentication
            auth = json.dumps({
                'user_id': self.current_user['unique_id']
            })
            self.chat_socket.send(auth.encode())
            
            # Start listening thread
            thread = threading.Thread(target=self.listen_for_messages)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            print(f"Could not connect to chat server: {e}")
            self.chat_socket = None
            
    def listen_for_messages(self):
        """Listen for incoming chat messages"""
        while True:
            try:
                if not self.chat_socket:
                    break
                    
                message = self.chat_socket.recv(1024).decode()
                if message:
                    data = json.loads(message)
                    self.add_message_to_chat(data['sender_id'], data['content'])
            except:
                break

    def update_donation_list(self, donations):
        """Update the donations treeview"""
        # Clear existing items
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
            
        # Add new items
        for donation in donations:
            values = (
                donation['title'],
                donation['category'],
                donation['condition'],
                donation['location'],
                donation['donor_name'],
                donation['status'],
                donation['created_at'],
                donation['donor_id']
            )
            
            # Add description as a hidden value
            tags = ('available',) if donation['status'] == 'available' else ()
            item = self.donations_tree.insert('', 'end', values=values, tags=tags)
            
            # Store description in item dictionary
            self.donations_tree.set(item, 'description', donation.get('description', ''))

if __name__ == "__main__":
    root = tk.Tk()
    app = CrowdNestApp(root)
    root.mainloop()