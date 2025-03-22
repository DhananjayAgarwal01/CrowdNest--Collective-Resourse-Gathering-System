import tkinter as tk
from tkinter import ttk, messagebox
from src.database_handler import DatabaseHandler
from src.pages.login_page import LoginPage
from src.pages.register_page import RegistrationPage
from src.pages.dashboard_page import DashboardPage
from src.pages.donation_form_page import DonationFormPage
from src.pages.donation_list_page import DonationListPage
from src.pages.profile_page import ProfilePage
from src.pages.chat_page import ChatPage
from src.pages.donation_history_page import DonationHistoryPage
from src.ui.modern_ui import ModernUI
from src.ui.navigation import NavigationPane
from src.constants import COLORS
import uuid
import base64
import os
import sys
import webbrowser
from urllib.parse import quote

class CrowdNestApp:
    def __init__(self, root):
        """Initialize the application"""
        self.root = root
        self.root.title("CrowdNest")
        self.root.state('zoomed')
        
        # Initialize database handler
        self.db = DatabaseHandler()
        
        # Initialize current user
        self.current_user = None
        
        # Configure styles
        ModernUI.setup_styles()
        
        # Create main container
        self.container = ttk.Frame(root)
        self.container.pack(fill='both', expand=True)
        
        # Create frames dictionary
        self.frames = {}
        
        # Create content frame
        self.content_frame = ttk.Frame(self.container, style='Content.TFrame')
        self.content_frame.pack(fill='both', expand=True, side='right')
        
        # Create navigation pane (initially hidden)
        self.nav_pane = NavigationPane(self.container, self.show_frame)
        # Do NOT pack the navigation pane initially
        
        # Create all pages
        self.create_pages()
        
        # Show login frame
        self.show_frame('login')
    
    def create_pages(self):
        """Create all pages for the application"""
        # Login page
        self.login_page = LoginPage(
            self.content_frame, 
            self.login, 
            self.show_frame
        )
        self.frames['login'] = self.login_page

        # Registration page
        self.register_page = RegistrationPage(
            self.content_frame, 
            self.register, 
            self.show_frame
        )
        self.frames['register'] = self.register_page

        # Dashboard page
        self.dashboard_page = DashboardPage(
            self.content_frame, 
            self.show_frame,
            current_user=None  # Explicitly set to None initially
        )
        self.frames['dashboard'] = self.dashboard_page

        # Donation List page
        self.donation_list_page = DonationListPage(
            self.content_frame, 
            self.get_donations, 
            self.contact_donor, 
            self.show_frame,
            update_status_callback=self.update_donation_status,
            mark_as_donated_callback=self.mark_donation_as_donated,
            current_user=self.current_user
        )
        self.frames['browse'] = self.donation_list_page
        
        # Donation form page
        self.donation_form_page = DonationFormPage(
            self.content_frame, 
            self.submit_donation, 
            self.show_frame
        )
        self.frames['donate'] = self.donation_form_page
        
        # Profile page
        self.profile_page = ProfilePage(
            self.content_frame,
            self.update_profile,  # save_profile_callback
            self.change_password,  # change_password_callback
            self.show_frame,  # show_frame_callback
            current_user=None  # Explicitly set to None initially
        )
        self.frames['profile'] = self.profile_page
        
        # Create chat page
        self.chat_page = ChatPage(
            self.content_frame,
            self.get_contacts,
            self.get_messages,
            self.send_message,
            self.show_frame
        )
        self.frames['chat'] = self.chat_page
        
        # Initially show login page
        self.show_frame('login')
    
    def login(self, username, password):
        """Authenticate user and set current user"""
        try:
            # Verify user credentials
            user, message = self.db.verify_user(username, password)
            
            if user:
                # Set current user
                self.current_user = user
                
                # Update pages with current user
                pages_to_update = [
                    'dashboard_page', 
                    'profile_page', 
                    'donation_list_page', 
                    'donation_form_page'
                ]
                
                for page_name in pages_to_update:
                    if hasattr(self, page_name):
                        page = getattr(self, page_name)
                        page.current_user = user
                        
                        # Call update method if exists
                        if hasattr(page, 'update_user_info'):
                            page.update_user_info(user)
                        elif hasattr(page, 'update_profile'):
                            page.update_profile()
                
                # Show navigation pane
                self.nav_pane.pack(fill='y', side='left')
                
                # Show dashboard
                self.show_frame('dashboard')
                
                # Update dashboard
                self.update_dashboard()
                
                return True
            else:
                # Show error message
                messagebox.showerror("Login Failed", message)
                return False
        
        except Exception as e:
            print(f"Login error: {e}")
            messagebox.showerror("Error", "An unexpected error occurred during login")
            return False
    
    def register(self, username, password, email, location):
        success, message = self.db.create_user(username, password, email, location)
        if success:
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.show_frame('login')
        else:
            messagebox.showerror("Error", message)
    
    def submit_donation(self, title, description, category, condition, state, city, image_data=None):
        """Submit a new donation"""
        if not self.current_user:
            messagebox.showwarning("Login Required", "You must be logged in to create a donation")
            self.show_frame('login')
            return False
            
        success, message = self.db.create_donation(
            self.current_user['unique_id'],
            title,
            description,
            category,
            condition,
            state,
            city,
            image_data
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.show_frame('browse')
        else:
            messagebox.showerror("Error", message)
            
        return success
        
    def get_donations(self, category=None, condition=None, location=None, donation_id=None):
        """Retrieve donations with optional filtering"""
        try:
            # Prepare filter parameters
            filters = {}
            if category:
                filters['category'] = category
            if condition:
                filters['condition'] = condition
            if location:
                filters['location'] = location
            if donation_id:
                filters['unique_id'] = donation_id
            
            # Call database method to get donations
            donations = self.db.get_donations(**filters)
            
            return donations
        
        except Exception as e:
            print(f"Error retrieving donations: {e}")
            messagebox.showerror("Error", "Failed to retrieve donations")
            return []
    
    def contact_donor(self, donation_id):
        """Contact a donor about their donation"""
        if not self.current_user:
            messagebox.showwarning("Login Required", "You must be logged in to contact a donor")
            self.show_frame('login')
            return False
        
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
            print(f"Error contacting donor: {e}")
            messagebox.showerror("Error", "Failed to contact donor")
            return False
    
    def update_donation_status(self, donation_id, new_status):
        """Update the status of a donation"""
        if not self.current_user:
            return False, "You must be logged in to update donation status"
            
        return self.db.update_donation_status(donation_id, new_status)
    
    def mark_donation_as_donated(self, donation_id):
        """Mark a donation as donated"""
        if not self.current_user:
            return False, "You must be logged in to mark a donation as donated"
        
        # Verify the current user is the donor of this donation
        return self.db.mark_donation_as_donated(donation_id, self.current_user['unique_id'])

    def get_donation_history(self):
        """Retrieve donation history for the current user"""
        if not self.current_user:
            return []
        
        return self.db.get_user_donation_history(self.current_user['unique_id'])

    def create_donation_history_page(self):
        """Create and show donation history page"""
        # Check if user is logged in
        if not self.current_user:
            messagebox.showwarning("Login Required", "You must be logged in to view donation history")
            self.show_frame('login')
            return
        
        try:
            # Retrieve user's donation history from the database
            user_donations = self.db.get_user_donation_history(self.current_user['unique_id'])
            
            # Create a new page for donation history
            donation_history_page = DonationHistoryPage(
                self.content_frame, 
                user_donations, 
                self.show_frame
            )
            
            # Add the page to frames dictionary
            self.frames['donation_history'] = donation_history_page
            
            # Show the donation history page
            self.show_frame('donation_history')
        
        except Exception as e:
            print(f"Error creating donation history page: {e}")
            messagebox.showerror("Error", "Failed to retrieve donation history")
    
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
            
    def update_profile(self, updated_profile_data):
        """Update user profile"""
        if not self.current_user:
            messagebox.showwarning("Login Required", "You must be logged in to update profile")
            self.show_frame('login')
            return False, "Not logged in"
        
        try:
            # Validate input
            if not updated_profile_data:
                return False, "No profile data provided"
            
            # Update user profile in the database
            success, message = self.db.update_user_profile(
                self.current_user['unique_id'], 
                updated_profile_data
            )
            
            if success:
                # Update current user information
                self.current_user.update(updated_profile_data)
                messagebox.showinfo("Success", "Profile updated successfully")
                return True, "Profile updated"
            else:
                messagebox.showerror("Error", message)
                return False, message
        
        except Exception as e:
            print(f"Error updating profile: {e}")
            messagebox.showerror("Error", "Failed to update profile")
            return False, "Update failed"
            
    def save_profile_changes(self, email, full_name, location):
        """Save user profile changes"""
        if not self.current_user:
            messagebox.showerror("Error", "No user logged in")
            return False
            
        success, result = self.db.save_profile_changes(
            self.current_user['unique_id'],
            email,
            full_name,
            location
        )
        
        if success:
            # Update current user info
            self.current_user['email'] = email
            self.current_user['full_name'] = full_name
            self.current_user['location'] = location
            messagebox.showinfo("Success", result)
        else:
            messagebox.showerror("Error", result)
            
        return success
            
    def change_password(self, old_password, new_password, confirm_password):
        """Change user's password"""
        try:
            # Validate input
            if not old_password or not new_password or not confirm_password:
                messagebox.showerror("Error", "All password fields are required")
                return False
            
            if new_password != confirm_password:
                messagebox.showerror("Error", "New passwords do not match")
                return False
            
            # Verify current user and old password
            if not self.current_user:
                messagebox.showerror("Error", "No user is currently logged in")
                return False
            
            # Use database handler to change password
            success = self.db.change_user_password(
                self.current_user['unique_id'], 
                old_password, 
                new_password
            )
            
            if success:
                messagebox.showinfo("Success", "Password changed successfully")
                return True
            else:
                messagebox.showerror("Error", "Current password is incorrect")
                return False
        
        except Exception as e:
            print(f"Password change error: {e}")
            messagebox.showerror("Error", "Failed to change password")
            return False
    
    def get_notifications(self, user_id=None):
        """Get recent notifications for the current user"""
        if not user_id and self.current_user:
            user_id = self.current_user['unique_id']
            
        if not user_id:
            return []
            
        return self.db.get_notifications(user_id)
            
    def show_frame(self, frame_name):
        """Show a specific frame, with authentication checks"""
        # List of frames that require authentication
        auth_required_frames = [
            'dashboard', 
            'donate', 
            'profile', 
            'chat',
            'donation_history'
        ]
        
        # Check if authentication is required for this frame
        if frame_name in auth_required_frames:
            # If not logged in, redirect to login
            if not self.current_user:
                messagebox.showwarning("Login Required", f"You must be logged in to access {frame_name}")
                frame_name = 'login'
        
        # Hide all frames
        for name, frame in self.frames.items():
            if hasattr(frame, 'frame'):
                frame.frame.pack_forget()
        
        # Hide/show navigation pane based on authentication
        if frame_name in ['login', 'register']:
            # Hide navigation pane for login and register pages
            if hasattr(self, 'nav_pane'):
                self.nav_pane.pack_forget()
        else:
            # Show navigation pane for authenticated pages
            if hasattr(self, 'nav_pane'):
                self.nav_pane.pack(fill='y', side='left')
        
        # Show the selected frame
        if frame_name in self.frames:
            frame = self.frames[frame_name]
            if hasattr(frame, 'frame'):
                frame.frame.pack(fill='both', expand=True)
            
            # Special handling for dashboard to update user info
            if frame_name == 'dashboard' and self.current_user:
                if hasattr(frame, 'update_user_info'):
                    frame.update_user_info(self.current_user)
        
        return frame_name
    
    def logout(self):
        """Logout the current user and reset application state"""
        # Clear current user
        self.current_user = None
        
        # Hide navigation pane
        self.nav_pane.pack_forget()
        
        # Reset pages that depend on user data
        pages_to_reset = [
            'dashboard_page', 
            'profile_page', 
            'donation_list_page', 
            'donation_form_page'
        ]
        
        for page_name in pages_to_reset:
            if hasattr(self, page_name):
                page = getattr(self, page_name)
                
                # Reset current user
                page.current_user = None
                
                # Call reset method if exists
                if hasattr(page, 'reset'):
                    page.reset()
        
        # Show login page
        self.show_frame('login')
        
        # Optional: Clear any session tokens or additional cleanup
        messagebox.showinfo("Logout", "You have been logged out successfully")
    
if __name__ == '__main__':
    # Create and run Tkinter app
    root = tk.Tk()
    app = CrowdNestApp(root)
    root.mainloop()