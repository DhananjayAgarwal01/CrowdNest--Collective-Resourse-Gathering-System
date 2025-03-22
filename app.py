import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.styles import CustomStyle
from src.ui.navigation import NavigationPane
from src.database_handler import DatabaseHandler
from src.pages.login_page import LoginPage
from src.pages.register_page import RegisterPage
from src.pages.dashboard_page import DashboardPage
from src.pages.donation_form_page import DonationFormPage
from src.pages.donation_list_page import DonationListPage
from src.pages.chat_page import ChatPage
from src.pages.profile_page import ProfilePage
import base64
import os
import sys
import webbrowser
from urllib.parse import quote

class CrowdNestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CrowdNest")
        self.root.state('zoomed')
        
        # Initialize database handler
        self.db = DatabaseHandler()
        
        # Initialize current user
        self.current_user = None
        
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
        
        # Create all pages
        self.create_pages()
        
        # Show login frame
        self.show_frame('login')
    
    def create_pages(self):
        # Create login page
        self.login_page = LoginPage(self.content_frame, self.login, self.show_frame)
        self.frames['login'] = self.login_page.frame
        
        # Create register page
        self.register_page = RegisterPage(self.content_frame, self.register, lambda: self.show_frame('login'))
        self.frames['register'] = self.register_page.frame
        
        # Create dashboard page
        self.dashboard_page = DashboardPage(self.content_frame, self.show_frame, self.current_user, self.get_notifications)
        self.frames['dashboard'] = self.dashboard_page.frame
        
        # Create donation form page
        self.donation_form_page = DonationFormPage(self.content_frame, self.submit_donation, self.show_frame)
        self.frames['donation_form'] = self.donation_form_page.frame
        
        # Create donation list page
        self.donation_list_page = DonationListPage(
            self.content_frame,
            self.get_donations,
            self.contact_donor
        )
        self.frames['donation_list'] = self.donation_list_page.frame
        
        # Create chat page
        self.chat_page = ChatPage(
            self.content_frame, 
            self.get_contacts, 
            self.get_messages, 
            self.send_message,
            self.show_frame
        )
        self.frames['chat'] = self.chat_page.frame
        
        # Create profile page
        self.profile_page = ProfilePage(
            self.content_frame, 
            self.save_profile_changes, 
            self.change_password,
            self.show_frame,
            self.current_user
        )
        self.frames['profile'] = self.profile_page.frame
    
    def login(self, username, password):
        user_data = self.db.verify_user(username, password)
        user, message = user_data if isinstance(user_data, tuple) else (user_data, None)
        
        if user:
            self.current_user = user
            
            # Update profile page with current user
            if hasattr(self, 'profile_page'):
                self.profile_page.current_user = self.current_user
                self.profile_page.update_profile()
            
            self.nav_pane.pack(fill='y', side='left')
            self.show_frame('dashboard')
            self.update_dashboard()
        else:
            messagebox.showerror("Error", message or "Invalid credentials")
    
    def register(self, username, password, email, location):
        success, message = self.db.create_user(username, password, email, location)
        if success:
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.show_frame('login')
        else:
            messagebox.showerror("Error", message)
    
    def submit_donation(self, donation_data):
        if not self.current_user:
            messagebox.showerror("Error", "You must be logged in to submit a donation")
            return
        
        # Add user_id to donation data
        donation_data['user_id'] = self.current_user['unique_id']
        
        # Handle images
        images = []
        if 'images' in donation_data and donation_data['images']:
            for image_path in donation_data['images']:
                try:
                    # Read the image file and convert to base64
                    with open(image_path, 'rb') as img_file:
                        img_data = img_file.read()
                        # Encode the binary data to base64 for storage
                        encoded_img = base64.b64encode(img_data).decode('utf-8')
                        images.append(encoded_img)
                except Exception as e:
                    print(f"Error processing image {image_path}: {str(e)}")
        
        # Add encoded images to donation data
        donation_data['image_data'] = images
        
        # Create the donation
        success = self.db.create_donation(donation_data)
        
        if success:
            messagebox.showinfo("Success", "Donation submitted successfully")
            return True
        else:
            messagebox.showerror("Error", "Failed to submit donation")
            return False
    
    def get_donations(self, search_query=None, category=None, condition=None, location=None, donation_id=None):
        """Get donations based on search criteria"""
        return self.db.get_donations(
            search_query=search_query,
            category=category,
            location=location,
            donation_id=donation_id
        )

    def contact_donor(self, donation_id):
        """Contact a donor about their donation"""
        try:
            donations = self.db.get_donations(donation_id=donation_id)
            if not donations:
                messagebox.showerror("Error", "Donation not found")
                return False
                
            donation = donations[0]
            donor_email = donation['donor_email']
            donor_name = donation['donor_name']
            
            # Open default email client
            subject = f"Interest in your donation: {donation['title']}"
            body = f"Hi {donor_name},\n\nI am interested in your donation: {donation['title']}."
            webbrowser.open(f'mailto:{donor_email}?subject={quote(subject)}&body={quote(body)}')
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to contact donor: {str(e)}")
            return False
    
    def get_contacts(self):
        if not self.current_user:
            return []
            
        return self.db.get_contacts(self.current_user['unique_id'])
    
    def get_messages(self, other_user_id):
        if not self.current_user:
            return []
            
        return self.db.get_messages(self.current_user['unique_id'], other_user_id)
    
    def send_message(self, receiver_id, content, donation_id=None):
        if not self.current_user:
            messagebox.showerror("Error", "You must be logged in to send messages")
            return False
            
        success, message = self.db.send_message(
            self.current_user['unique_id'],
            receiver_id,
            content,
            donation_id
        )
        
        if success:
            return True, "Message sent successfully"
        else:
            return False, message
            
    def update_dashboard(self):
        if hasattr(self, 'dashboard_page') and self.current_user:
            self.dashboard_page.update_user_info(self.current_user)
            
    def save_profile_changes(self, email, full_name, location):
        """Save user profile changes"""
        if not self.current_user:
            messagebox.showerror("Error", "You must be logged in to update your profile")
            return
            
        success, result = self.db.save_profile_changes(
            self.current_user['unique_id'],
            email,
            full_name,
            location
        )
        
        if success:
            # Update current user data
            self.current_user = result
            # Update profile page
            self.profile_page.current_user = self.current_user
            self.profile_page.update_profile()
            messagebox.showinfo("Success", "Profile updated successfully")
        else:
            messagebox.showerror("Error", result)
            
    def change_password(self, current_password, new_password):
        """Change user password"""
        if not self.current_user:
            messagebox.showerror("Error", "You must be logged in to change your password")
            return False
            
        if len(new_password) < 6:
            messagebox.showerror("Error", "New password must be at least 6 characters long")
            return False
            
        success, message = self.db.change_password(
            self.current_user['unique_id'],
            current_password,
            new_password
        )
        
        if success:
            messagebox.showinfo("Success", message)
            return True
        else:
            messagebox.showerror("Error", message)
            return False
            
    def get_notifications(self, user_id=None):
        """Get recent notifications for the current user"""
        if not user_id and self.current_user:
            user_id = self.current_user['unique_id']
            
        if not user_id:
            return []
            
        return self.db.get_notifications(user_id)
            
    def show_frame(self, frame_name):
        """Show the specified frame"""
        if frame_name == 'login':
            # Hide navigation pane and clear current user
            self.nav_pane.pack_forget()
            self.current_user = None
            
        elif frame_name == 'profile' and self.current_user:
            # Update profile display when showing profile page
            self.profile_page.update_profile()
            
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
            
        # Show selected frame
        self.frames[frame_name].pack(fill='both', expand=True)
    
if __name__ == '__main__':
    # Create and run Tkinter app
    root = tk.Tk()
    app = CrowdNestApp(root)
    root.mainloop()