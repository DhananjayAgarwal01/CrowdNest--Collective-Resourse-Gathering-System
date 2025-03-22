import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.components import ModernUI

class LoginPage:
    def __init__(self, parent, login_callback, show_frame_callback):
        self.parent = parent
        self.login_callback = login_callback
        self.show_frame = show_frame_callback
        self.frame = None
        self.login_username = None
        self.login_password = None
        self.create_frame()
        
    def create_frame(self):
        self.frame = ModernUI.create_card(self.parent)
        
        # Center content
        content = ttk.Frame(self.frame, style='Card.TFrame')
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
    
    def login(self):
        username = self.login_username.get()
        password = self.login_password.get()
        
        # Call the login callback function provided by the main app
        self.login_callback(username, password)