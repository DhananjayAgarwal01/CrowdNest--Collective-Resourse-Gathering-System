import tkinter as tk
from tkinter import ttk
from src.constants import COLORS

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
                       activebackground=COLORS['accent'],
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
        btn.bind('<Enter>', lambda e: btn.configure(bg=COLORS['accent']))
        btn.bind('<Leave>', lambda e: btn.configure(bg=COLORS['primary']))

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        
    def pack_forget(self):
        self.frame.pack_forget()