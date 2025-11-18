"""
Main GUI Application for Invoice Generator.

Cross-platform Tkinter-based invoice generator with:
- First-time company setup wizard
- Invoice creation form with dynamic line items
- Settings panel for updating company info and preferences
- PDF generation and management
- SQLite database for persistent storage

Supports Windows and macOS with proper file path handling via pathlib.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import subprocess
import platform
import os

# Import local modules
import db
import utils
import pdf_generator


class InvoiceGeneratorApp:
    """Main application class for the Invoice Generator."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Invoice Generator Pro")
        self.root.geometry("1400x900")
        
        # Set minimum size
        self.root.minsize(1200, 800)
        
        # Ultra-modern color scheme with darker sidebar
        self.colors = {
            'primary': '#4F46E5',      # Indigo 600
            'primary_hover': '#4338CA', # Indigo 700
            'secondary': '#8B5CF6',    # Purple 500
            'success': '#10B981',      # Emerald 500
            'danger': '#EF4444',       # Red 500
            'warning': '#F59E0B',      # Amber 500
            'bg_main': '#F8FAFC',      # Slate 50
            'bg_card': '#FFFFFF',      # White
            'bg_sidebar': '#0F172A',   # Slate 900
            'bg_sidebar_hover': '#1E293B', # Slate 800
            'text_dark': '#0F172A',    # Slate 900
            'text_light': '#64748B',   # Slate 500
            'text_sidebar': '#94A3B8', # Slate 400
            'border': '#E2E8F0',       # Slate 200
            'shadow': '#64748B20',     # Slate 500 with opacity
        }
        
        # Configure root background
        self.root.configure(bg=self.colors['bg_sidebar'])
        
        # Configure custom styles
        self._configure_styles()
        
        # Initialize database
        self.db = db.Database()
        
        # Line items storage
        self.line_items = []
        
        # Check if first run
        if self.db.is_first_run():
            self.show_company_setup()
        else:
            self.load_company_settings()
            self.create_main_window()
    
    def _configure_styles(self):
        """Configure custom ttk styles for modern look."""
        style = ttk.Style()
        
        # Configure theme
        style.theme_use('clam')
        
        # Configure TFrame
        style.configure('TFrame', background=self.colors['bg_main'])
        style.configure('Card.TFrame', background=self.colors['bg_card'], relief='flat')
        
        # Configure TLabel
        style.configure('TLabel', background=self.colors['bg_main'], 
                       foreground=self.colors['text_dark'])
        style.configure('Title.TLabel', font=('Helvetica', 20, 'bold'),
                       foreground=self.colors['primary'])
        style.configure('Subtitle.TLabel', font=('Helvetica', 11),
                       foreground=self.colors['text_light'])
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'),
                       foreground=self.colors['text_dark'])
        style.configure('CardHeader.TLabel', font=('Helvetica', 13, 'bold'),
                       foreground=self.colors['primary'], background=self.colors['bg_card'])
        
        # Configure TButton - Modern flat style
        style.configure('TButton', font=('Helvetica', 10), 
                       padding=10, relief='flat')
        style.map('TButton',
                 background=[('active', self.colors['primary']), 
                           ('!active', self.colors['primary'])],
                 foreground=[('active', 'white'), ('!active', 'white')])
        
        # Primary button
        style.configure('Primary.TButton', font=('Helvetica', 11, 'bold'),
                       background=self.colors['primary'], foreground='white',
                       padding=12)
        style.map('Primary.TButton',
                 background=[('active', '#4f46e5'), ('!active', self.colors['primary'])])
        
        # Success button
        style.configure('Success.TButton', font=('Helvetica', 10, 'bold'),
                       background=self.colors['success'], foreground='white',
                       padding=10)
        style.map('Success.TButton',
                 background=[('active', '#059669'), ('!active', self.colors['success'])])
        
        # Danger button
        style.configure('Danger.TButton', font=('Helvetica', 9),
                       background=self.colors['danger'], foreground='white',
                       padding=6)
        style.map('Danger.TButton',
                 background=[('active', '#dc2626'), ('!active', self.colors['danger'])])
        
        # Configure TEntry
        style.configure('TEntry', fieldbackground='white', 
                       foreground=self.colors['text_dark'],
                       borderwidth=1, relief='solid')
        
        # Configure TCombobox
        style.configure('TCombobox', fieldbackground='white',
                       foreground=self.colors['text_dark'],
                       borderwidth=1)
        
        # Configure TLabelframe
        style.configure('Card.TLabelframe', background=self.colors['bg_card'],
                       foreground=self.colors['primary'], 
                       borderwidth=2, relief='solid')
        style.configure('Card.TLabelframe.Label', font=('Helvetica', 12, 'bold'),
                       foreground=self.colors['primary'], background=self.colors['bg_card'])
    
    def load_company_settings(self):
        """Load company settings from database."""
        self.company_settings = self.db.get_company_settings()
        if not self.company_settings:
            messagebox.showerror("Error", "Failed to load company settings")
            self.root.quit()
    
    def show_company_setup(self):
        """Display the first-time company setup wizard."""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Company Setup - First Time Configuration")
        setup_window.geometry("600x550")
        setup_window.transient(self.root)
        setup_window.grab_set()
        
        # Make it non-closable via X button
        setup_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Title
        title_label = tk.Label(
            setup_window,
            text="Welcome to Invoice Generator!",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            setup_window,
            text="Please enter your company information to get started.",
            font=("Helvetica", 10)
        )
        subtitle_label.pack(pady=5)
        
        # Form frame
        form_frame = ttk.Frame(setup_window, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Company Name
        ttk.Label(form_frame, text="Company Name:*").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        company_name_entry = ttk.Entry(form_frame, width=40)
        company_name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Company Address
        ttk.Label(form_frame, text="Company Address:*").grid(
            row=1, column=0, sticky=tk.NW, pady=5
        )
        company_address_text = tk.Text(form_frame, width=40, height=4)
        company_address_text.grid(row=1, column=1, pady=5, padx=5)
        
        # Company Phone
        ttk.Label(form_frame, text="Company Phone:*").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        company_phone_entry = ttk.Entry(form_frame, width=40)
        company_phone_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Default Currency
        ttk.Label(form_frame, text="Default Currency:*").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        currency_var = tk.StringVar(value="USD")
        currency_combo = ttk.Combobox(
            form_frame,
            textvariable=currency_var,
            values=utils.get_available_currencies(),
            state="readonly",
            width=37
        )
        currency_combo.grid(row=3, column=1, pady=5, padx=5)
        
        # Logo Path
        ttk.Label(form_frame, text="Company Logo:").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        logo_path_var = tk.StringVar(value="")
        logo_frame = ttk.Frame(form_frame)
        logo_frame.grid(row=4, column=1, pady=5, padx=5, sticky=tk.W)
        
        logo_entry = ttk.Entry(logo_frame, textvariable=logo_path_var, width=30)
        logo_entry.pack(side=tk.LEFT)
        
        def choose_logo():
            filename = filedialog.askopenfilename(
                title="Select Company Logo",
                filetypes=[
                    ("Image Files", "*.png *.jpg *.jpeg"),
                    ("All Files", "*.*")
                ]
            )
            if filename:
                logo_path_var.set(filename)
        
        ttk.Button(logo_frame, text="Browse...", command=choose_logo).pack(
            side=tk.LEFT, padx=5
        )
        
        # Output Folder
        ttk.Label(form_frame, text="Invoice Output Folder:*").grid(
            row=5, column=0, sticky=tk.W, pady=5
        )
        output_path_var = tk.StringVar(value=str(Path.home() / "Documents" / "Invoices"))
        output_frame = ttk.Frame(form_frame)
        output_frame.grid(row=5, column=1, pady=5, padx=5, sticky=tk.W)
        
        output_entry = ttk.Entry(output_frame, textvariable=output_path_var, width=30)
        output_entry.pack(side=tk.LEFT)
        
        def choose_output_folder():
            folder = filedialog.askdirectory(title="Select Output Folder")
            if folder:
                output_path_var.set(folder)
        
        ttk.Button(output_frame, text="Browse...", command=choose_output_folder).pack(
            side=tk.LEFT, padx=5
        )
        
        # Save button
        def save_setup():
            # Validate inputs
            name = company_name_entry.get().strip()
            address = company_address_text.get("1.0", tk.END).strip()
            phone = company_phone_entry.get().strip()
            currency = currency_var.get()
            logo = logo_path_var.get().strip()
            output = output_path_var.get().strip()
            
            if not name:
                messagebox.showerror("Validation Error", "Company name is required")
                return
            
            if not address:
                messagebox.showerror("Validation Error", "Company address is required")
                return
            
            if not phone:
                messagebox.showerror("Validation Error", "Company phone is required")
                return
            
            if not output:
                messagebox.showerror("Validation Error", "Output folder is required")
                return
            
            # Create output folder if it doesn't exist
            output_path = Path(output)
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create output folder: {e}")
                return
            
            # Save to database
            logo_value = logo if logo else None
            success = self.db.save_company_settings(
                name=name,
                address=address,
                phone=phone,
                logo_path=logo_value,
                currency=currency,
                output_folder=output
            )
            
            if success:
                messagebox.showinfo("Success", "Company settings saved successfully!")
                setup_window.destroy()
                self.load_company_settings()
                self.create_main_window()
            else:
                messagebox.showerror("Error", "Failed to save company settings")
        
        button_frame = ttk.Frame(setup_window)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Save & Continue",
            command=save_setup,
            style="Accent.TButton"
        ).pack()
    
    def create_main_window(self):
        """Create the main invoice generation window with ultra-modern sidebar layout."""
        # Main container - full window
        main_container = tk.Frame(self.root, bg=self.colors['bg_main'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # === SIDEBAR (LEFT) ===
        sidebar = tk.Frame(main_container, bg=self.colors['bg_sidebar'], width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)  # Fixed width
        
        # Logo/Brand section
        brand_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        brand_frame.pack(fill=tk.X, pady=30, padx=20)
        
        tk.Label(
            brand_frame,
            text="📊",
            font=('SF Pro Display', 32),
            bg=self.colors['bg_sidebar'],
            fg='white'
        ).pack()
        
        tk.Label(
            brand_frame,
            text="Invoice Pro",
            font=('SF Pro Display', 18, 'bold'),
            bg=self.colors['bg_sidebar'],
            fg='white'
        ).pack(pady=(10, 0))
        
        tk.Label(
            brand_frame,
            text=self.company_settings['company_name'][:20],
            font=('SF Pro Display', 10),
            bg=self.colors['bg_sidebar'],
            fg=self.colors['text_sidebar']
        ).pack(pady=(5, 0))
        
        # Menu items
        menu_frame = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        menu_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Active page indicator
        self.active_page = tk.StringVar(value="invoice")
        
        # Menu buttons
        menu_items = [
            ("📄 New Invoice", "invoice", lambda: None),
            ("⚙️ Settings", "settings", self.show_settings),
            ("📁 Open Folder", "folder", self.open_output_folder),
        ]
        
        for label, page_id, command in menu_items:
            self.create_sidebar_button(menu_frame, label, page_id, command)
        
        # === CONTENT AREA (RIGHT) ===
        content_area = tk.Frame(main_container, bg=self.colors['bg_main'])
        content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Header bar with gradient effect simulation
        header_bar = tk.Frame(content_area, bg=self.colors['primary'], height=60)
        header_bar.pack(fill=tk.X)
        header_bar.pack_propagate(False)
        
        header_content = tk.Frame(header_bar, bg=self.colors['primary'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=15)
        
        tk.Label(
            header_content,
            text="Create New Invoice",
            font=('SF Pro Display', 20, 'bold'),
            bg=self.colors['primary'],
            fg='white'
        ).pack(side=tk.LEFT)
        
        # Current date
        current_date = datetime.now().strftime("%B %d, %Y")
        tk.Label(
            header_content,
            text=f"📅 {current_date}",
            font=('SF Pro Display', 11),
            bg=self.colors['primary'],
            fg='white'
        ).pack(side=tk.RIGHT)
        
        # Scrollable form area
        form_container = tk.Frame(content_area, bg=self.colors['bg_main'])
        form_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Create form
        self.create_modern_invoice_form(form_container)
        
        # Action buttons at bottom
        action_bar = tk.Frame(content_area, bg=self.colors['bg_main'])
        action_bar.pack(fill=tk.X, padx=40, pady=(0, 30))
        
        # Import modern components
        from modern_ui import ModernButton
        
        button_container = tk.Frame(action_bar, bg=self.colors['bg_main'])
        button_container.pack()
        
        ModernButton(
            button_container,
            text="✓ Generate Invoice",
            command=self.generate_invoice,
            style='primary'
        ).pack(side=tk.LEFT, padx=5)
        
        ModernButton(
            button_container,
            text="Clear Form",
            command=self.clear_invoice_form,
            style='secondary'
        ).pack(side=tk.LEFT, padx=5)
    
    def create_sidebar_button(self, parent, text, page_id, command):
        """Create a styled sidebar button."""
        def on_click():
            self.active_page.set(page_id)
            # Update all buttons
            for widget in parent.winfo_children():
                if isinstance(widget, tk.Label):
                    if widget.cget('text') == text:
                        widget.configure(
                            bg=self.colors['primary'],
                            fg='white'
                        )
                    else:
                        widget.configure(
                            bg=self.colors['bg_sidebar'],
                            fg=self.colors['text_sidebar']
                        )
            if command:
                command()
        
        is_active = self.active_page.get() == page_id
        
        btn = tk.Label(
            parent,
            text=text,
            font=('SF Pro Display', 12),
            bg=self.colors['primary'] if is_active else self.colors['bg_sidebar'],
            fg='white' if is_active else self.colors['text_sidebar'],
            anchor='w',
            padx=25,
            pady=15,
            cursor='hand2'
        )
        btn.pack(fill=tk.X, pady=2)
        
        # Hover effects
        def on_enter(e):
            if self.active_page.get() != page_id:
                btn.configure(bg=self.colors['bg_sidebar_hover'], fg='white')
        
        def on_leave(e):
            if self.active_page.get() != page_id:
                btn.configure(bg=self.colors['bg_sidebar'], fg=self.colors['text_sidebar'])
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        btn.bind('<Button-1>', lambda e: on_click())
    
    def create_modern_invoice_form(self, parent):
        """Create the ultra-modern invoice form with cards."""
        # Import modern components
        from modern_ui import ModernCard, ModernInput
        
        # Canvas for scrolling
        canvas = tk.Canvas(parent, bg=self.colors['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg_main'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # === CUSTOMER INFORMATION CARD ===
        customer_card = ModernCard(
            scrollable_frame,
            title="Customer Information",
            subtitle="Enter the billing details for this invoice"
        )
        customer_card.pack(fill=tk.X, pady=(0, 25))
        
        self.billing_name_input = ModernInput(
            customer_card.content_frame,
            label="Customer Name",
            placeholder="John Doe",
            required=True
        )
        self.billing_name_input.pack(fill=tk.X, pady=(0, 15))
        
        # Address
        tk.Label(
            customer_card.content_frame,
            text="Billing Address *",
            font=('SF Pro Display', 11, 'bold'),
            bg='white',
            fg='#0F172A',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 8))
        
        self.billing_address_text = tk.Text(
            customer_card.content_frame,
            font=('SF Pro Display', 11),
            relief='solid',
            borderwidth=1,
            bg='white',
            fg='#0F172A',
            height=4
        )
        self.billing_address_text.pack(fill=tk.X, pady=(0, 15), ipady=12, ipadx=15)
        
        self.billing_phone_input = ModernInput(
            customer_card.content_frame,
            label="Phone Number",
            placeholder="+1 (555) 123-4567",
            required=True
        )
        self.billing_phone_input.pack(fill=tk.X)
        
        # === INVOICE DETAILS CARD ===
        details_card = ModernCard(
            scrollable_frame,
            title="Invoice Details",
            subtitle="Configure invoice settings and pricing"
        )
        details_card.pack(fill=tk.X, pady=(0, 25))
        
        # Two-column layout
        details_row1 = tk.Frame(details_card.content_frame, bg='white')
        details_row1.pack(fill=tk.X, pady=(0, 15))
        
        details_left = tk.Frame(details_row1, bg='white')
        details_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        details_right = tk.Frame(details_row1, bg='white')
        details_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0))
        
        # Currency (left)
        tk.Label(
            details_left,
            text="Currency",
            font=('SF Pro Display', 11, 'bold'),
            bg='white',
            fg='#0F172A',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 8))
        
        self.currency_var = tk.StringVar(value=self.company_settings['default_currency'])
        currency_combo = ttk.Combobox(
            details_left,
            textvariable=self.currency_var,
            values=utils.get_available_currencies(),
            state="readonly",
            font=('SF Pro Display', 11)
        )
        currency_combo.pack(fill=tk.X, ipady=12)
        
        # Invoice Date (right)
        tk.Label(
            details_right,
            text="Invoice Date",
            font=('SF Pro Display', 11, 'bold'),
            bg='white',
            fg='#0F172A',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 8))
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(
            details_right,
            textvariable=self.date_var,
            font=('SF Pro Display', 11),
            relief='solid',
            borderwidth=1,
            bg='white',
            fg='#0F172A'
        )
        date_entry.pack(fill=tk.X, ipady=12, ipadx=15)
        
        # Tax and Discount row
        details_row2 = tk.Frame(details_card.content_frame, bg='white')
        details_row2.pack(fill=tk.X)
        
        tax_frame = tk.Frame(details_row2, bg='white')
        tax_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        discount_frame = tk.Frame(details_row2, bg='white')
        discount_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0))
        
        # Tax Rate
        tk.Label(
            tax_frame,
            text="Tax Rate (%)",
            font=('SF Pro Display', 11, 'bold'),
            bg='white',
            fg='#0F172A',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 8))
        
        self.tax_rate_var = tk.StringVar(value="0")
        tax_entry = tk.Entry(
            tax_frame,
            textvariable=self.tax_rate_var,
            font=('SF Pro Display', 11),
            relief='solid',
            borderwidth=1,
            bg='white',
            fg='#0F172A'
        )
        tax_entry.pack(fill=tk.X, ipady=12, ipadx=15)
        
        # Discount
        tk.Label(
            discount_frame,
            text="Discount Amount",
            font=('SF Pro Display', 11, 'bold'),
            bg='white',
            fg='#0F172A',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 8))
        
        self.discount_var = tk.StringVar(value="0")
        discount_entry = tk.Entry(
            discount_frame,
            textvariable=self.discount_var,
            font=('SF Pro Display', 11),
            relief='solid',
            borderwidth=1,
            bg='white',
            fg='#0F172A'
        )
        discount_entry.pack(fill=tk.X, ipady=12, ipadx=15)
        
        # === LINE ITEMS CARD ===
        items_card = ModernCard(
            scrollable_frame,
            title="Invoice Items",
            subtitle="Add products or services to this invoice"
        )
        items_card.pack(fill=tk.BOTH, expand=True, pady=(0, 25))
        
        # Items header
        items_header = tk.Frame(items_card.content_frame, bg='white')
        items_header.pack(fill=tk.X, pady=(0, 15))
        
        headers = [
            ("Description", 350),
            ("Qty", 80),
            ("Unit Price", 120),
            ("Total", 120),
            ("", 100)
        ]
        
        for text, width in headers:
            tk.Label(
                items_header,
                text=text,
                font=('SF Pro Display', 10, 'bold'),
                bg='white',
                fg='#64748B',
                width=width // 8
            ).pack(side=tk.LEFT, padx=5)
        
        # Items container
        self.items_container = tk.Frame(items_card.content_frame, bg='white')
        self.items_container.pack(fill=tk.BOTH, expand=True)
        
        # Add item button
        from modern_ui import ModernButton
        add_btn_frame = tk.Frame(items_card.content_frame, bg='white')
        add_btn_frame.pack(pady=(15, 0))
        
        ModernButton(
            add_btn_frame,
            text="+ Add Item",
            command=self.add_modern_line_item,
            style='success'
        ).pack()
        
        # Pack canvas
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add initial item
        self.line_items = []
        self.add_modern_line_item()
    
    def add_modern_line_item(self):
        """Add a modern styled line item."""
        item_frame = tk.Frame(self.items_container, bg='white')
        item_frame.pack(fill=tk.X, pady=8)
        
        # Description
        desc_entry = tk.Entry(
            item_frame,
            font=('SF Pro Display', 10),
            relief='solid',
            borderwidth=1,
            bg='white',
            fg='#0F172A',
            width=45
        )
        desc_entry.pack(side=tk.LEFT, padx=5, ipady=8, ipadx=10)
        
        # Quantity
        qty_entry = tk.Entry(
            item_frame,
            font=('SF Pro Display', 10),
            relief='solid',
            borderwidth=1,
            bg='white',
            fg='#0F172A',
            width=10
        )
        qty_entry.insert(0, "1")
        qty_entry.pack(side=tk.LEFT, padx=5, ipady=8, ipadx=10)
        
        # Unit Price
        price_entry = tk.Entry(
            item_frame,
            font=('SF Pro Display', 10),
            relief='solid',
            borderwidth=1,
            bg='white',
            fg='#0F172A',
            width=15
        )
        price_entry.insert(0, "0.00")
        price_entry.pack(side=tk.LEFT, padx=5, ipady=8, ipadx=10)
        
        # Total
        total_var = tk.StringVar(value="0.00")
        total_label = tk.Label(
            item_frame,
            textvariable=total_var,
            font=('SF Pro Display', 10, 'bold'),
            bg='white',
            fg='#10B981',
            width=15,
            anchor='w'
        )
        total_label.pack(side=tk.LEFT, padx=5)
        
        # Auto-calculate
        def update_total(*args):
            try:
                qty = int(qty_entry.get())
                price = float(price_entry.get())
                total = qty * price
                total_var.set(f"${total:.2f}")
            except ValueError:
                total_var.set("$0.00")
        
        qty_entry.bind("<KeyRelease>", update_total)
        price_entry.bind("<KeyRelease>", update_total)
        
        # Remove button
        def remove_item():
            item_frame.destroy()
            self.line_items.remove(item_data)
        
        from modern_ui import ModernButton
        ModernButton(
            item_frame,
            text="✕",
            command=remove_item,
            style='danger'
        ).pack(side=tk.LEFT, padx=5)
        
        # Store
        item_data = {
            'frame': item_frame,
            'description': desc_entry,
            'quantity': qty_entry,
            'unit_price': price_entry,
            'total': total_var
        }
        self.line_items.append(item_data)
    
    def validate_invoice_form(self) -> tuple:
        """
        Validate the invoice form inputs.
        
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        # Billing information
        billing_name = self.billing_name_input.get().strip()
        if not billing_name or billing_name in ["John Doe", ""]:
            return False, "Customer name is required"
        
        billing_address = self.billing_address_text.get("1.0", tk.END).strip()
        if not billing_address:
            return False, "Billing address is required"
        
        billing_phone = self.billing_phone_input.get().strip()
        if billing_phone in ["+1 (555) 123-4567", ""]:
            return False, "Phone number is required"
        valid, msg = utils.validate_phone(billing_phone)
        if not valid:
            return False, msg
        
        # Date
        try:
            datetime.strptime(self.date_var.get(), "%Y-%m-%d")
        except ValueError:
            return False, "Invalid date format (use YYYY-MM-DD)"
        
        # Tax rate
        valid, msg = utils.validate_positive_number(self.tax_rate_var.get(), "Tax rate")
        if not valid:
            return False, msg
        
        # Discount
        valid, msg = utils.validate_positive_number(self.discount_var.get(), "Discount")
        if not valid:
            return False, msg
        
        # Line items
        if not self.line_items:
            return False, "At least one line item is required"
        
        valid_items = 0
        for item in self.line_items:
            desc = item['description'].get().strip()
            qty_str = item['quantity'].get().strip()
            price_str = item['unit_price'].get().strip()
            
            if desc:  # Only validate items with description
                valid, msg = utils.validate_quantity(qty_str)
                if not valid:
                    return False, f"Invalid quantity: {msg}"
                
                valid, msg = utils.validate_positive_number(price_str, "Unit price")
                if not valid:
                    return False, f"Invalid price: {msg}"
                
                valid_items += 1
        
        if valid_items == 0:
            return False, "At least one line item with description is required"
        
        return True, ""
    
    def collect_invoice_data(self) -> tuple:
        """
        Collect and format invoice data from form.
        
        Returns:
            Tuple of (invoice_data: dict, items: list)
        """
        # Parse date
        invoice_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d")
        
        # Generate order number
        date_str = utils.get_date_string_for_sequence(invoice_date)
        sequence = self.db.get_next_invoice_sequence(date_str)
        order_number = utils.generate_order_number(invoice_date, sequence)
        
        # Collect invoice data
        invoice_data = {
            'order_number': order_number,
            'invoice_date': invoice_date,
            'billing_name': self.billing_name_input.get().strip(),
            'billing_address': self.billing_address_text.get("1.0", tk.END).strip(),
            'billing_phone': self.billing_phone_input.get().strip(),
            'currency': self.currency_var.get(),
            'tax_rate': float(self.tax_rate_var.get()),
            'discount_amount': float(self.discount_var.get())
        }
        
        # Collect line items (only those with description)
        items = []
        for item in self.line_items:
            desc = item['description'].get().strip()
            if desc:
                items.append({
                    'description': desc,
                    'quantity': int(item['quantity'].get()),
                    'unit_price': float(item['unit_price'].get())
                })
        
        return invoice_data, items
    
    def generate_invoice(self):
        """Generate and save the invoice PDF."""
        # Validate form
        valid, error_msg = self.validate_invoice_form()
        if not valid:
            messagebox.showerror("Validation Error", error_msg)
            return
        
        # Collect data
        invoice_data, items = self.collect_invoice_data()
        
        # Prepare company data
        company_data = {
            'company_name': self.company_settings['company_name'],
            'company_address': self.company_settings['company_address'],
            'company_phone': self.company_settings['company_phone'],
            'logo_path': self.company_settings.get('logo_path')
        }
        
        # Generate PDF path
        output_folder = Path(self.company_settings['output_folder'])
        pdf_filename = f"{invoice_data['order_number']}.pdf"
        pdf_path = output_folder / pdf_filename
        
        # Ensure output folder exists
        try:
            output_folder.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create output folder: {e}")
            return
        
        # Generate PDF
        try:
            success = pdf_generator.create_invoice_pdf(
                str(pdf_path),
                invoice_data,
                company_data,
                items
            )
            
            if not success:
                messagebox.showerror("Error", "Failed to generate PDF")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error generating PDF: {e}")
            return
        
        # Calculate totals for database
        totals = utils.calculate_invoice_totals(
            items,
            invoice_data['tax_rate'],
            invoice_data['discount_amount']
        )
        
        # Save to database
        success = self.db.save_invoice(
            order_number=invoice_data['order_number'],
            invoice_date=invoice_data['invoice_date'].strftime("%Y-%m-%d"),
            billing_name=invoice_data['billing_name'],
            billing_address=invoice_data['billing_address'],
            billing_phone=invoice_data['billing_phone'],
            currency=invoice_data['currency'],
            subtotal=totals['subtotal'],
            tax_amount=totals['tax_amount'],
            discount_amount=totals['discount_amount'],
            total=totals['total'],
            pdf_path=str(pdf_path)
        )
        
        if not success:
            messagebox.showwarning(
                "Warning",
                "PDF generated but failed to save invoice record to database"
            )
        
        # Show success message with print option
        self.show_success_dialog(
            invoice_data['order_number'],
            totals['total'],
            invoice_data['currency'],
            pdf_path
        )
        
        # Clear form for next invoice
        self.clear_invoice_form()
    
    def show_success_dialog(self, order_number: str, total: float, currency: str, pdf_path: Path):
        """
        Show success dialog with options to print or open the invoice.
        
        Args:
            order_number: Invoice order number
            total: Total amount
            currency: Currency code
            pdf_path: Path to the generated PDF
        """
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Invoice Generated Successfully")
        dialog.geometry("450x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Success icon and message
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Success message
        success_label = tk.Label(
            main_frame,
            text="✓ Invoice Generated Successfully!",
            font=("Helvetica", 16, "bold"),
            fg="#10b981"
        )
        success_label.pack(pady=(0, 20))
        
        # Invoice details
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            details_frame,
            text=f"Order Number:",
            font=("Helvetica", 10, "bold")
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(
            details_frame,
            text=order_number,
            font=("Helvetica", 10)
        ).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(
            details_frame,
            text=f"Total Amount:",
            font=("Helvetica", 10, "bold")
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(
            details_frame,
            text=utils.format_currency(total, currency),
            font=("Helvetica", 10)
        ).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(
            details_frame,
            text=f"Saved to:",
            font=("Helvetica", 10, "bold")
        ).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(
            details_frame,
            text=str(pdf_path.name),
            font=("Helvetica", 9)
        ).grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        def print_invoice():
            """Print the generated invoice PDF."""
            success = self.print_pdf(pdf_path)
            if success:
                messagebox.showinfo("Print", "Invoice sent to printer!", parent=dialog)
            else:
                messagebox.showerror("Print Error", "Failed to send invoice to printer.", parent=dialog)
        
        def open_invoice():
            """Open the PDF file."""
            self.open_pdf_file(pdf_path)
            dialog.destroy()
        
        # Print button (primary action)
        print_btn = ttk.Button(
            button_frame,
            text="🖨 Print Invoice",
            command=print_invoice,
            width=20
        )
        print_btn.pack(side=tk.LEFT, padx=5)
        
        # Open button
        open_btn = ttk.Button(
            button_frame,
            text="📄 Open PDF",
            command=open_invoice,
            width=20
        )
        open_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = ttk.Button(
            button_frame,
            text="Close",
            command=dialog.destroy,
            width=15
        )
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # Make print button default (activated by Enter key)
        dialog.bind('<Return>', lambda e: print_invoice())
        print_btn.focus_set()
    
    def print_pdf(self, pdf_path: Path) -> bool:
        """
        Send PDF to the default printer.
        
        Args:
            pdf_path: Path to the PDF file to print
            
        Returns:
            True if successful, False otherwise
        """
        try:
            system = platform.system()
            
            if system == 'Darwin':  # macOS
                subprocess.run(['lpr', str(pdf_path)], check=True)
            elif system == 'Windows':
                # Use default PDF reader to print
                os.startfile(str(pdf_path), 'print')
            else:  # Linux
                subprocess.run(['lpr', str(pdf_path)], check=True)
            
            return True
        except Exception as e:
            print(f"Error printing PDF: {e}")
            return False
    
    def open_pdf_file(self, pdf_path: Path):
        """
        Open PDF file with the default application.
        
        Args:
            pdf_path: Path to the PDF file
        """
        try:
            system = platform.system()
            
            if system == 'Darwin':  # macOS
                subprocess.run(['open', str(pdf_path)])
            elif system == 'Windows':
                os.startfile(str(pdf_path))
            else:  # Linux
                subprocess.run(['xdg-open', str(pdf_path)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF: {e}")
    
    def clear_invoice_form(self):
        """Clear the invoice form for a new invoice."""
        # Clear billing fields
        self.billing_name_input.delete(0, tk.END)
        self.billing_name_input.insert(0, "John Doe")
        self.billing_name_input.entry.configure(fg='#94A3B8')
        
        self.billing_address_text.delete("1.0", tk.END)
        
        self.billing_phone_input.delete(0, tk.END)
        self.billing_phone_input.insert(0, "+1 (555) 123-4567")
        self.billing_phone_input.entry.configure(fg='#94A3B8')
        
        # Reset date to today
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        
        # Reset tax and discount
        self.tax_rate_var.set("0")
        self.discount_var.set("0")
        
        # Clear line items
        for item in self.line_items[:]:
            item['frame'].destroy()
        self.line_items.clear()
        
        # Add one empty line item
        self.add_modern_line_item()
    
    def open_output_folder(self):
        """Open the invoice output folder in the system file explorer."""
        output_folder = Path(self.company_settings['output_folder'])
        
        # Create folder if it doesn't exist
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # Open folder based on platform
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(output_folder)])
            elif platform.system() == 'Windows':
                subprocess.run(['explorer', str(output_folder)])
            else:  # Linux
                subprocess.run(['xdg-open', str(output_folder)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {e}")
    
    def show_settings(self):
        """Show the settings window to update company information."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("600x550")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Title
        title_label = tk.Label(
            settings_window,
            text="Company Settings",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # Form frame
        form_frame = ttk.Frame(settings_window, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Load current settings
        settings = self.company_settings
        
        # Company Name
        ttk.Label(form_frame, text="Company Name:*").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.insert(0, settings['company_name'])
        name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Company Address
        ttk.Label(form_frame, text="Company Address:*").grid(
            row=1, column=0, sticky=tk.NW, pady=5
        )
        address_text = tk.Text(form_frame, width=40, height=4)
        address_text.insert("1.0", settings['company_address'])
        address_text.grid(row=1, column=1, pady=5, padx=5)
        
        # Company Phone
        ttk.Label(form_frame, text="Company Phone:*").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        phone_entry = ttk.Entry(form_frame, width=40)
        phone_entry.insert(0, settings['company_phone'])
        phone_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Default Currency
        ttk.Label(form_frame, text="Default Currency:*").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        currency_var = tk.StringVar(value=settings['default_currency'])
        currency_combo = ttk.Combobox(
            form_frame,
            textvariable=currency_var,
            values=utils.get_available_currencies(),
            state="readonly",
            width=37
        )
        currency_combo.grid(row=3, column=1, pady=5, padx=5)
        
        # Logo Path
        ttk.Label(form_frame, text="Company Logo:").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        logo_path_var = tk.StringVar(value=settings.get('logo_path') or "")
        logo_frame = ttk.Frame(form_frame)
        logo_frame.grid(row=4, column=1, pady=5, padx=5, sticky=tk.W)
        
        logo_entry = ttk.Entry(logo_frame, textvariable=logo_path_var, width=30)
        logo_entry.pack(side=tk.LEFT)
        
        def choose_logo():
            filename = filedialog.askopenfilename(
                title="Select Company Logo",
                filetypes=[
                    ("Image Files", "*.png *.jpg *.jpeg"),
                    ("All Files", "*.*")
                ]
            )
            if filename:
                logo_path_var.set(filename)
        
        ttk.Button(logo_frame, text="Browse...", command=choose_logo).pack(
            side=tk.LEFT, padx=5
        )
        
        # Output Folder
        ttk.Label(form_frame, text="Invoice Output Folder:*").grid(
            row=5, column=0, sticky=tk.W, pady=5
        )
        output_path_var = tk.StringVar(value=settings['output_folder'])
        output_frame = ttk.Frame(form_frame)
        output_frame.grid(row=5, column=1, pady=5, padx=5, sticky=tk.W)
        
        output_entry = ttk.Entry(output_frame, textvariable=output_path_var, width=30)
        output_entry.pack(side=tk.LEFT)
        
        def choose_output_folder():
            folder = filedialog.askdirectory(title="Select Output Folder")
            if folder:
                output_path_var.set(folder)
        
        ttk.Button(output_frame, text="Browse...", command=choose_output_folder).pack(
            side=tk.LEFT, padx=5
        )
        
        # Save button
        def save_settings():
            # Validate inputs
            name = name_entry.get().strip()
            address = address_text.get("1.0", tk.END).strip()
            phone = phone_entry.get().strip()
            currency = currency_var.get()
            logo = logo_path_var.get().strip()
            output = output_path_var.get().strip()
            
            if not name or not address or not phone or not output:
                messagebox.showerror("Validation Error", "All required fields must be filled")
                return
            
            # Create output folder if it doesn't exist
            output_path = Path(output)
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create output folder: {e}")
                return
            
            # Save to database
            logo_value = logo if logo else None
            success = self.db.save_company_settings(
                name=name,
                address=address,
                phone=phone,
                logo_path=logo_value,
                currency=currency,
                output_folder=output
            )
            
            if success:
                messagebox.showinfo("Success", "Settings updated successfully!")
                self.load_company_settings()
                settings_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to save settings")
        
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Save Changes",
            command=save_settings
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=settings_window.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()
    
    def __del__(self):
        """Cleanup: close database connection."""
        if hasattr(self, 'db'):
            self.db.close()


def main():
    """
    Main entry point for the Invoice Generator application.
    
    Creates the Tkinter root window and starts the application.
    """
    # Create root window
    root = tk.Tk()
    
    # Set window icon if available (optional)
    # root.iconbitmap('icon.ico')  # Windows
    # root.iconphoto(True, tk.PhotoImage(file='icon.png'))  # Unix/macOS
    
    # Create and run application
    app = InvoiceGeneratorApp(root)
    app.run()


if __name__ == "__main__":
    """
    Run the application when the script is executed directly.
    
    Example:
        python main.py
    """
    main()
