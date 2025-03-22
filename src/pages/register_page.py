import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.components import ModernUI
from src.constants import STATES

class RegisterPage:
    def __init__(self, parent, register_callback, show_frame_callback):
        self.parent = parent
        self.register_callback = register_callback
        self.show_frame = show_frame_callback
        self.frame = None
        self.reg_entries = {}
        self.reg_state_var = tk.StringVar()
        self.reg_city_var = tk.StringVar()
        self.password_strength_label = None
        self.create_frame()
        
    def create_frame(self):
        frame = ModernUI.create_card(self.parent)
        
        # Create a canvas for scrollability
        canvas = tk.Canvas(frame, bg='#FFFFFF', highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)

        # Create a scrollable frame inside the canvas
        scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')

        # Attach the scrollable frame to the canvas (set a default width to prevent shifting)
        frame_window = canvas.create_window(0, 0, window=scrollable_frame, anchor="n", width=500)

        def update_window_position():
            """ Ensure content is centered properly on initial load and when resized. """
            canvas.itemconfig(frame_window, width=canvas.winfo_width())

        # Delay to ensure Tkinter has rendered everything before centering
        canvas.after(200, update_window_position)
        canvas.bind("<Configure>", lambda event: update_window_position())

        def update_scroll_region(event):
            """ Adjust scroll region dynamically. """
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", update_scroll_region)

        def _on_mouse_wheel(event):
            """ Enable smooth scrolling using mouse wheel. """
            if event.num == 5 or event.delta == -120:  # Scroll Down (Linux & Windows)
                canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta == 120:  # Scroll Up (Linux & Windows)
                canvas.yview_scroll(-1, "units")

        # Bind mouse scrolling
        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
        canvas.bind_all("<Button-4>", _on_mouse_wheel)   # Linux Scroll Up
        canvas.bind_all("<Button-5>", _on_mouse_wheel)   # Linux Scroll Down

        # Configure canvas and scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # WRAPPER FRAME (Expands fully to center content)
        wrapper_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        wrapper_frame.pack(fill='both', expand=True)  # Ensures no shifting

        # CONTENT FRAME (Holds form elements)
        content = ttk.Frame(wrapper_frame, style='Card.TFrame')
        content.pack(pady=40, padx=40, anchor="center")  # Increased horizontal padding

        # HEADER SECTION
        header_frame = ttk.Frame(content, style='Card.TFrame')
        header_frame.pack(fill='x', pady=(0, 20), anchor="center")

        ttk.Label(header_frame, text="🎁", font=('Poppins', 40), foreground='#0077B6').pack(anchor="center")
        ttk.Label(header_frame, text="Create Account", font=('Poppins', 20, 'bold'), foreground='#1B1B1E').pack(pady=(5, 2), anchor="center")
        ttk.Label(header_frame, text="Join our community and start sharing!", font=('Poppins', 12), foreground='#6C757D').pack(anchor="center")

        # REGISTRATION FORM
        form_frame = ttk.Frame(content, style='Card.TFrame')
        form_frame.pack(fill='x', pady=(0, 20))

        self.reg_entries = {}

        form_fields = [
            ("👤 Username", "Username", "Enter your username"),
            ("📧 Email", "Email", "Enter your email"),
            ("🔒 Password", "Password", "Enter your password", "•"),
            ("🔒 Confirm Password", "Confirm Password", "Re-enter your password", "•")
        ]

        for label_text, dict_key, placeholder, *password_mode in form_fields:
            field_frame = ttk.Frame(form_frame, style='Card.TFrame')
            field_frame.pack(fill='x', pady=(0, 15))  # Consistent vertical spacing

            ttk.Label(field_frame, text=label_text, font=('Poppins', 11, 'bold'), foreground='#1B1B1E').pack(anchor='w')

            show_char = password_mode[0] if password_mode else None
            entry = ModernUI.create_entry(field_frame, placeholder=placeholder, show=show_char)
            entry.pack(fill='x', pady=(5, 0), ipady=8)  # Full width entries with consistent padding

            self.reg_entries[dict_key] = entry

            # Password Strength Indicator
            if label_text == "🔒 Password":
                self.password_strength_label = ttk.Label(field_frame, text="Password Strength: Weak", font=('Poppins', 10), foreground="red")
                self.password_strength_label.pack(anchor='w', pady=(5, 0))
                entry.bind('<KeyRelease>', self.check_password_strength)

        # LOCATION SELECTOR
        location_frame = ttk.Frame(content, style='Card.TFrame')
        location_frame.pack(fill='x', pady=(0, 20))

        ttk.Label(location_frame, text="📍 Location", font=('Poppins', 11, 'bold'), foreground='#1B1B1E').pack(anchor='w')
        location_selector = ModernUI.create_location_selector(location_frame, self.reg_state_var, self.reg_city_var)
        location_selector.pack(fill='x', pady=(5, 0))

        # Store location variables
        self.reg_entries['State'] = self.reg_state_var
        self.reg_entries['City'] = self.reg_city_var

        # BUTTONS
        button_frame = ttk.Frame(content, style='Card.TFrame')
        button_frame.pack(fill='x', pady=(10, 0))

        ModernUI.create_button(button_frame, "✅ Create Account", self.register).pack(side='left', padx=(0, 10))
        ModernUI.create_button(button_frame, "🔙 Back to Login", lambda: self.show_frame('login'), style='Secondary.TButton').pack(side='left')

        self.frame = frame
        
    def check_password_strength(self, event):
        password = self.reg_entries['Password'].get()
        strength = "Weak"
        color = "red"
        
        if len(password) >= 8:
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(not c.isalnum() for c in password)
            
            if has_upper and has_lower and has_digit and has_special:
                strength = "Strong"
                color = "green"
            elif (has_upper or has_lower) and (has_digit or has_special):
                strength = "Medium"
                color = "orange"
        
        self.password_strength_label.config(text=f"Password Strength: {strength}", foreground=color)
    
    def register(self):
        # Get form data
        username = self.reg_entries['Username'].get()
        password = self.reg_entries['Password'].get()
        confirm_password = self.reg_entries['Confirm Password'].get()
        email = self.reg_entries['Email'].get()
        state = self.reg_state_var.get()
        city = self.reg_city_var.get()
        
        # Validate inputs
        if not all([username, password, confirm_password, email, state, city]):
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
        
        # Call the register callback function provided by the main app
        self.register_callback(username, password, email, location)