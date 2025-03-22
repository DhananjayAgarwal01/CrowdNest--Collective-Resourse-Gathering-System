import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.components import ModernUI

class ProfilePage:
    def __init__(self, parent, save_profile_callback, change_password_callback, show_frame_callback, current_user=None):
        self.parent = parent
        self.save_profile_callback = save_profile_callback
        self.change_password_callback = change_password_callback
        self.show_frame = show_frame_callback
        self.current_user = current_user
        self.frame = None
        self.profile_entries = {}
        self.profile_labels = {}
        self.create_frame()
        
    def create_frame(self):
        """Create the profile page frame"""
        self.frame = ModernUI.create_card(self.parent)
        
        # Create a scrollable canvas for the content
        canvas = tk.Canvas(self.frame, bg='#FFFFFF', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
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
        
        self.avatar_label = ttk.Label(
            avatar_frame,
            text="👤",
            font=('Segoe UI', 48),
            background='#0077B6',
            foreground='white'
        )
        self.avatar_label.pack(pady=10)
        
        ttk.Label(header_frame, text="My Profile", style='Title.TLabel').pack()
        
        # Profile Information Section
        info_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        info_frame.pack(fill='x', padx=40, pady=20)
        
        # Profile fields
        self.profile_entries = {}
        self.profile_labels = {}
        fields = [
            ('Username:', False),  # (field_name, is_editable)
            ('Email:', True),
            ('Full Name:', True),
            ('Location:', True),
            ('Join Date:', False),
            ('Total Donations:', False),
            ('Total Requests:', False),
            ('Total Messages:', False)
        ]
        
        for field, editable in fields:
            field_frame = ttk.Frame(info_frame, style='Card.TFrame')
            field_frame.pack(fill='x', pady=5)
            
            label = ttk.Label(field_frame, text=field, style='Subtitle.TLabel')
            label.pack(anchor='w')
            
            if editable:
                entry = ModernUI.create_entry(field_frame, width=40)
                entry.pack(pady=(5, 10))
                self.profile_entries[field] = entry
            else:
                value_label = ttk.Label(field_frame, text="", style='Subtitle.TLabel')
                value_label.pack(pady=(5, 10))
                self.profile_labels[field] = value_label
        
        # Action Buttons
        button_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
        button_frame.pack(fill='x', padx=40, pady=20)
        
        # Save button
        ModernUI.create_button(
            button_frame,
            "Save Changes",
            self.save_profile,
            width=20
        ).pack(side='left', padx=5)
        
        # Change Password button
        ModernUI.create_button(
            button_frame,
            "Change Password",
            self.show_change_password_dialog,
            style='Secondary.TButton',
            width=20
        ).pack(side='right', padx=5)
        
        # Initialize with current user data if available
        if self.current_user:
            self.update_profile()
            
    def update_profile(self):
        """Update profile display with current user data"""
        if not self.current_user:
            return
            
        try:
            # Update read-only labels
            for field, label in self.profile_labels.items():
                if field == 'Username:':
                    label.configure(text=str(self.current_user.get('username', 'N/A')))
                elif field == 'Join Date:':
                    created_at = self.current_user.get('created_at', 'N/A')
                    if isinstance(created_at, str):
                        label.configure(text=created_at)
                    else:
                        label.configure(text=created_at.strftime('%Y-%m-%d %H:%M:%S'))
                elif field == 'Total Donations:':
                    label.configure(text=str(self.current_user.get('total_donations', 0)))
                elif field == 'Total Requests:':
                    label.configure(text=str(self.current_user.get('total_requests', 0)))
                elif field == 'Total Messages:':
                    label.configure(text=str(self.current_user.get('total_messages', 0)))
            
            # Update editable fields
            if 'Email:' in self.profile_entries:
                self.profile_entries['Email:'].delete(0, tk.END)
                self.profile_entries['Email:'].insert(0, str(self.current_user.get('email', '')))
            
            if 'Full Name:' in self.profile_entries:
                self.profile_entries['Full Name:'].delete(0, tk.END)
                self.profile_entries['Full Name:'].insert(0, str(self.current_user.get('full_name', '')))
            
            if 'Location:' in self.profile_entries:
                self.profile_entries['Location:'].delete(0, tk.END)
                self.profile_entries['Location:'].insert(0, str(self.current_user.get('location', '')))
                
        except Exception as e:
            print(f"Error updating profile display: {e}")
            
    def save_profile(self):
        email = self.profile_entries['Email:'].get()
        full_name = self.profile_entries['Full Name:'].get()
        location = self.profile_entries['Location:'].get()
        
        # Call the save profile callback function provided by the main app
        self.save_profile_callback(email, full_name, location)
        
    def upload_profile_picture(self):
        from tkinter import filedialog
        from PIL import Image, ImageTk
        import os
        
        # Open file dialog for image selection
        filetypes = [('Image files', '*.png *.jpg *.jpeg *.gif *.bmp')]
        filename = filedialog.askopenfilename(title='Select Profile Picture', filetypes=filetypes)
        
        if filename:
            try:
                # Open and resize image
                image = Image.open(filename)
                # Calculate new size maintaining aspect ratio
                max_size = (200, 200)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image)
                
                # Update avatar label
                self.avatar_label.configure(image=photo, text='')
                self.avatar_label.image = photo  # Keep a reference
                
                # Save image path or data to user profile
                # TODO: Implement image saving to database
                messagebox.showinfo('Success', 'Profile picture updated successfully!')
                
            except Exception as e:
                messagebox.showerror('Error', f'Failed to upload image: {str(e)}')

    
    def show_change_password_dialog(self):
        # Create a password change dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Change Password")
        dialog.geometry("400x300")
        dialog.configure(bg='#FFFFFF')
        
        # Center the dialog
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Content frame
        content = ttk.Frame(dialog, style='Card.TFrame')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(content, text="Change Password", style='Title.TLabel').pack(pady=(0, 20))
        
        # Password fields
        current_password = ModernUI.create_entry(content, "Current Password", show="•", width=30)
        current_password.pack(pady=10)
        
        new_password = ModernUI.create_entry(content, "New Password", show="•", width=30)
        new_password.pack(pady=10)
        
        confirm_password = ModernUI.create_entry(content, "Confirm New Password", show="•", width=30)
        confirm_password.pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(content, style='Card.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        def submit_password_change():
            current = current_password.get()
            new = new_password.get()
            confirm = confirm_password.get()
            
            if not all([current, new, confirm]):
                messagebox.showerror("Error", "All fields are required")
                return
                
            if new != confirm:
                messagebox.showerror("Error", "New passwords do not match")
                return
                
            if len(new) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long")
                return
            
            # Call the change password callback function provided by the main app
            result = self.change_password_callback(current, new)
            
            if result:
                messagebox.showinfo("Success", "Password changed successfully")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Current password is incorrect")
        
        ModernUI.create_button(button_frame, "Change Password", submit_password_change, width=15).pack(side='left', padx=5)
        ModernUI.create_button(button_frame, "Cancel", dialog.destroy, style='Secondary.TButton', width=15).pack(side='right', padx=5)