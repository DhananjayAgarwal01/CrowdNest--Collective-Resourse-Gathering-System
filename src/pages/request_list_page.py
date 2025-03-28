import tkinter as tk
from tkinter import ttk, messagebox
from src.ui.modern_ui import ModernUI
from src.constants import COLORS, CATEGORIES, LOCATIONS, STATES
from src.database.database_handler import DatabaseHandler

class RequestListPage:
    def __init__(self, parent, user_info, show_frame_callback):
        """Initialize the request list page"""
        self.parent = parent
        self.user_info = user_info
        self.show_frame = show_frame_callback
        self.db = DatabaseHandler()
        
        # Create frame
        self.frame = ModernUI.create_card(parent)
        self.frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(
            self.frame,
            text="Resource Requests",
            style='Title.TLabel'
        ).pack(pady=(0, 20))
        
        # Search and filter frame
        self._create_search_frame()
        
        # Requests treeview
        self._create_requests_treeview()
        
        # Load initial requests
        self.refresh_requests()
    
    def _create_search_frame(self):
        """Create search and filter components"""
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        # Search entry
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=5)
        search_entry.insert(0, "Search requests...")
        search_entry.bind('<FocusIn>', lambda e: search_entry.delete(0, tk.END) if search_entry.get() == "Search requests..." else None)
        search_entry.bind('<FocusOut>', lambda e: search_entry.insert(0, "Search requests...") if not search_entry.get() else None)
        
        # Category dropdown
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.category_var, 
            values=['All'] + list(CATEGORIES), 
            width=15, 
            state='readonly'
        )
        category_combo.set('All')
        category_combo.pack(side='left', padx=5)
        
        # Status dropdown
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.status_var, 
            values=['All', 'Open', 'Fulfilled', 'Closed'], 
            width=10, 
            state='readonly'
        )
        status_combo.set('All')
        status_combo.pack(side='left', padx=5)
        
        # Search button
        search_btn = ModernUI.create_button(
            search_frame,
            "Search",
            self.search_requests,
            style='Primary.TButton'
        )
        search_btn.pack(side='left', padx=5)
    
    def _create_requests_treeview(self):
        """Create treeview for displaying requests"""
        # Columns
        columns = ('title', 'category', 'requester', 'status', 'date')
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.requests_tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show='headings', 
            style='Treeview'
        )
        
        # Define column headings
        self.requests_tree.heading('title', text='Request Title', command=lambda: self.sort_column('title', False))
        self.requests_tree.heading('category', text='Category', command=lambda: self.sort_column('category', False))
        self.requests_tree.heading('requester', text='Requester', command=lambda: self.sort_column('requester', False))
        self.requests_tree.heading('status', text='Status', command=lambda: self.sort_column('status', False))
        self.requests_tree.heading('date', text='Date', command=lambda: self.sort_column('date', False))
        
        # Define column widths
        self.requests_tree.column('title', width=250, anchor='w')
        self.requests_tree.column('category', width=100, anchor='center')
        self.requests_tree.column('requester', width=150, anchor='w')
        self.requests_tree.column('status', width=100, anchor='center')
        self.requests_tree.column('date', width=150, anchor='center')
        
        # Scrollbars
        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient='vertical', command=self.requests_tree.yview)
        tree_scrollbar_x = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.requests_tree.xview)
        self.requests_tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)
        
        # Pack treeview and scrollbars
        self.requests_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar_y.pack(side='right', fill='y')
        tree_scrollbar_x.pack(side='bottom', fill='x')
        
        # Bind double-click event
        self.requests_tree.bind('<Double-1>', self.view_request_details)
    
    def search_requests(self):
        """Search and filter requests based on user input"""
        search_term = self.search_var.get().lower()
        category = self.category_var.get()
        status = self.status_var.get()
        
        # Fetch requests from database with filters
        try:
            requests = self.db.search_requests(
                search_query=search_term if search_term != "search requests..." else None,
                category=category if category != 'All' else None,
                status=status.lower() if status != 'All' else None
            )
            
            # Clear existing items
            for item in self.requests_tree.get_children():
                self.requests_tree.delete(item)
            
            # Populate treeview
            for request in requests:
                self.requests_tree.insert('', 'end', values=(
                    request['title'], 
                    request['category'], 
                    request.get('requester_name', 'Unknown'),
                    request['status'].capitalize(), 
                    request['created_at'].strftime('%Y-%m-%d %H:%M')
                ))
        except Exception as e:
            messagebox.showerror("Search Error", str(e))
    
    def view_request_details(self, event):
        """View details of selected request"""
        selected_item = self.requests_tree.selection()
        if not selected_item:
            return
        
        # Get request details
        request_details = self.requests_tree.item(selected_item)['values']
        
        # Show details in a popup
        details_window = tk.Toplevel(self.frame)
        details_window.title("Request Details")
        details_window.geometry("400x300")
        
        # Details display
        details_frame = ttk.Frame(details_window)
        details_frame.pack(padx=20, pady=20, fill='both', expand=True)
        
        details = [
            ("Title", request_details[0]),
            ("Category", request_details[1]),
            ("Requester", request_details[2]),
            ("Status", request_details[3]),
            ("Date", request_details[4])
        ]
        
        for label, value in details:
            ttk.Label(details_frame, text=f"{label}:", font=('Segoe UI', 10, 'bold')).pack(anchor='w')
            ttk.Label(details_frame, text=value).pack(anchor='w', pady=(0, 10))
    
    def sort_column(self, col, reverse):
        """Sort treeview column"""
        l = [(self.requests_tree.set(k, col), k) for k in self.requests_tree.get_children('')]
        l.sort(reverse=reverse)
        
        for index, (val, k) in enumerate(l):
            self.requests_tree.move(k, '', index)
        
        # Toggle sort direction
        self.requests_tree.heading(col, command=lambda: self.sort_column(col, not reverse))
    
    def refresh_requests(self):
        """Refresh requests list"""
        # Reset search and filters
        self.search_var.set("Search requests...")
        self.category_var.set('All')
        self.status_var.set('All')
        
        # Fetch and display requests
        self.search_requests()
