import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import base64
from PIL import Image, ImageTk
from src.ui.components import ModernUI
from src.constants import COLORS, CATEGORIES, CONDITIONS

class DonationFormPage:
    def __init__(self, parent, submit_donation_callback, show_frame_callback):
        self.parent = parent
        self.submit_donation_callback = submit_donation_callback
        self.show_frame = show_frame_callback
        self.frame = None
        self.donation_entries = {}
        self.donation_title = None
        self.donation_description = None
        self.donation_category_var = tk.StringVar()
        self.donation_condition_var = tk.StringVar()
        self.donation_state_var = tk.StringVar()
        self.donation_city_var = tk.StringVar()
        self.title_counter = None
        self.desc_counter = None
        self.image_paths = []
        self.image_previews = []
        self.preview_frame = None
        self.create_frame()
        
    def submit_donation(self):
        # Get all the donation details
        title = self.donation_entries['Title:'].get()
        description = self.donation_entries['Description:'].get('1.0', 'end-1c')
        category = self.donation_entries['Category:'].get()
        condition = self.donation_entries['Condition:'].get()
        state = self.donation_state_var.get()
        city = self.donation_city_var.get()

        # Validate required fields
        if not title or not description or not category or not condition or not state or not city:
            messagebox.showerror("Error", "Please fill in all required fields")
            return

        # Validate field lengths
        if len(title) > 100:
            messagebox.showerror("Error", "Title must be less than 100 characters")
            return
        if len(description) > 500:
            messagebox.showerror("Error", "Description must be less than 500 characters")
            return

        # Create donation data dictionary
        donation_data = {
            'title': title,
            'description': description,
            'category': category,
            'condition': condition,
            'state': state,
            'city': city,
            'images': self.image_paths
        }

        try:
            # Call the callback function with the donation data
            self.submit_donation_callback(donation_data)
            messagebox.showinfo("Success", "Donation submitted successfully!")
            # Clear the form
            self.clear_form()
            # Redirect to dashboard
            self.show_frame('dashboard')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit donation: {str(e)}")

    def update_char_counter(self, widget, counter_label, max_chars, is_text=False):
        """Update character counter for text inputs"""
        if is_text:
            current_chars = len(widget.get('1.0', 'end-1c'))
        else:
            current_chars = len(widget.get())
        counter_label.config(text=f"{current_chars}/{max_chars}")
        
        # Visual feedback when approaching/exceeding limit
        if current_chars > max_chars:
            counter_label.config(foreground='red')
        elif current_chars > max_chars * 0.9:  # 90% of limit
            counter_label.config(foreground='orange')
        else:
            counter_label.config(foreground='black')

    def clear_form(self):
        # Clear all form fields
        self.donation_entries['Title:'].delete(0, 'end')
        self.donation_entries['Description:'].delete('1.0', 'end')
        self.donation_entries['Category:'].set('')
        self.donation_entries['Condition:'].set('')
        self.donation_state_var.set('')
        self.donation_city_var.set('')
        # Reset character counters
        self.update_char_counter(self.donation_entries['Title:'], self.title_counter, 100)
        self.update_char_counter(self.donation_entries['Description:'], self.desc_counter, 500, is_text=True)
        # Clear image paths and previews
        self.image_paths = []
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
    def preview_donation(self):
        # Get all the donation details
        title = self.donation_entries['Title:'].get()
        description = self.donation_entries['Description:'].get('1.0', 'end-1c')
        category = self.donation_entries['Category:'].get()
        condition = self.donation_entries['Condition:'].get()
        state = self.donation_state_var.get()
        city = self.donation_city_var.get()
        
        # Create preview window
        preview_window = tk.Toplevel(self.parent)
        preview_window.title("Donation Preview")
        preview_window.geometry("500x400")
        
        # Style the preview window
        preview_frame = ttk.Frame(preview_window, style='Card.TFrame', padding=20)
        preview_frame.pack(fill='both', expand=True)
        
        # Display donation details
        ttk.Label(preview_frame, text="Donation Preview", style='Title.TLabel').pack(pady=(0, 20))
        
        details = [
            ("Title", title),
            ("Description", description),
            ("Category", category),
            ("Condition", condition),
            ("Location", f"{city}, {state}" if city and state else "Not specified")
        ]
        
        for label, value in details:
            detail_frame = ttk.Frame(preview_frame, style='Card.TFrame')
            detail_frame.pack(fill='x', pady=5)
            ttk.Label(detail_frame, text=f"{label}:", style='Subtitle.TLabel').pack(anchor='w')
            ttk.Label(detail_frame, text=value, wraplength=400).pack(anchor='w', padx=20)
        
        # Close button
        ModernUI.create_button(preview_frame, "Close Preview", preview_window.destroy).pack(pady=20)
        
    def upload_image(self):
        # Open file dialog to select image
        file_paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")],
            multiple=True
        )
        
        if not file_paths:
            return
            
        # Add selected images to the list
        for file_path in file_paths:
            if file_path not in self.image_paths:
                self.image_paths.append(file_path)
                self._add_image_preview(file_path)
                
        # Update the preview frame
        self.preview_frame.update()
    
    def _add_image_preview(self, file_path):
        try:
            # Create a thumbnail of the image
            image = Image.open(file_path)
            image.thumbnail((100, 100))  # Resize to thumbnail
            photo = ImageTk.PhotoImage(image)
            
            # Create a frame for the image preview
            img_preview_frame = ttk.Frame(self.preview_frame, style='Card.TFrame')
            img_preview_frame.pack(side='left', padx=5, pady=5)
            
            # Create a label to display the image
            preview_label = ttk.Label(img_preview_frame, image=photo)
            preview_label.image = photo  # Keep a reference
            preview_label.pack(padx=5, pady=5)
            
            # Create a remove button
            remove_btn = ttk.Button(
                img_preview_frame, 
                text="✕", 
                width=2,
                command=lambda fp=file_path, frame=img_preview_frame: self._remove_image(fp, frame)
            )
            remove_btn.pack(pady=(0, 5))
            
            # Add to list of previews
            self.image_previews.append((file_path, img_preview_frame))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def _remove_image(self, file_path, frame):
        # Remove the image from the list
        if file_path in self.image_paths:
            self.image_paths.remove(file_path)
        
        # Remove the preview from the UI
        frame.destroy()
        
        # Remove from previews list
        for i, (path, preview_frame) in enumerate(self.image_previews):
            if path == file_path:
                self.image_previews.pop(i)
                break
        
    def create_frame(self):
        self.frame = ModernUI.create_card(self.parent)
        
        # Create a scrollable canvas for the content
        canvas = tk.Canvas(self.frame, bg=COLORS['card'], highlightthickness=0)
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
        
        # Image upload
        img_frame = ttk.Frame(content, style='Card.TFrame')
        img_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(img_frame, text="📸 Upload Images", style='Subtitle.TLabel').pack(anchor='w')
        
        # Create a frame for upload button and image previews
        upload_section = ttk.Frame(img_frame, style='Card.TFrame')
        upload_section.pack(fill='x', pady=(5, 0))
        
        # Upload button
        ModernUI.create_button(
            upload_section, 
            "Choose Files", 
            self.upload_image, 
            style='Secondary.TButton'
        ).pack(side='left', pady=(5, 0))
        
        # Image preview area
        preview_container = ttk.Frame(img_frame, style='Card.TFrame')
        preview_container.pack(fill='x', pady=(10, 0))
        
        # Create scrollable frame for image previews
        preview_canvas = tk.Canvas(preview_container, height=120, bg=COLORS['card'], highlightthickness=0)
        preview_scrollbar = ttk.Scrollbar(preview_container, orient="horizontal", command=preview_canvas.xview)
        self.preview_frame = ttk.Frame(preview_canvas, style='Card.TFrame')
        
        self.preview_frame.bind(
            "<Configure>",
            lambda e: preview_canvas.configure(scrollregion=preview_canvas.bbox("all"))
        )
        
        preview_canvas.create_window((0, 0), window=self.preview_frame, anchor="nw")
        preview_canvas.configure(xscrollcommand=preview_scrollbar.set)
        
        # Pack the scrollbar and canvas
        preview_scrollbar.pack(side="bottom", fill="x")
        preview_canvas.pack(side="top", fill="both", expand=True)
        
        # Add note about max images
        ttk.Label(
            img_frame, 
            text="Max 5 images, JPG/PNG format only", 
            foreground=COLORS['text_light']
        ).pack(anchor='w', pady=(5, 0))
        
        # Buttons at the bottom
        button_frame = ttk.Frame(content, style='Card.TFrame')
        button_frame.pack(fill='x', pady=30)
        
        ModernUI.create_button(button_frame, "Preview Donation", self.preview_donation, width=20).pack(side='left', padx=5)
        ModernUI.create_button(button_frame, "Submit Donation", self.submit_donation, width=20).pack(side='left', padx=5)
        ModernUI.create_button(button_frame, "Back to Dashboard", 
                             lambda: self.show_frame('dashboard'), 
                             style='Secondary.TButton', width=20).pack(side='right', padx=5)
        
        # No need to store frame in frames dictionary as it's managed by the parent class