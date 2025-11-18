"""
Modern UI components and styling for Invoice Generator.
Ultra-modern design with gradients, shadows, and contemporary aesthetics.
"""

import tkinter as tk
from tkinter import ttk


class ModernCard(tk.Frame):
    """Modern card widget with shadow effect."""
    
    def __init__(self, parent, title=None, subtitle=None, **kwargs):
        super().__init__(parent, bg='white', **kwargs)
        
        # Configure card with shadow simulation
        self.configure(relief='flat', bd=0)
        
        # Card content
        content = tk.Frame(self, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Title
        if title:
            title_label = tk.Label(
                content,
                text=title,
                font=('SF Pro Display', 16, 'bold'),
                bg='white',
                fg='#0F172A',
                anchor='w'
            )
            title_label.pack(fill=tk.X, pady=(0, 5))
        
        # Subtitle
        if subtitle:
            subtitle_label = tk.Label(
                content,
                text=subtitle,
                font=('SF Pro Display', 10),
                bg='white',
                fg='#94A3B8',
                anchor='w'
            )
            subtitle_label.pack(fill=tk.X, pady=(0, 20))
        
        self.content_frame = content


class ModernInput(tk.Frame):
    """Modern input field with label and styling."""
    
    def __init__(self, parent, label, placeholder="", required=False, **kwargs):
        super().__init__(parent, bg='white')
        
        # Label
        label_text = f"{label} {'*' if required else ''}"
        label_widget = tk.Label(
            self,
            text=label_text,
            font=('SF Pro Display', 11, 'bold'),
            bg='white',
            fg='#0F172A',
            anchor='w'
        )
        label_widget.pack(fill=tk.X, pady=(0, 8))
        
        # Input field with modern styling
        self.entry = tk.Entry(
            self,
            font=('SF Pro Display', 11),
            relief='solid',
            borderwidth=1,
            bg='white',
            fg='#0F172A',
            insertbackground='#4F46E5'
        )
        self.entry.pack(fill=tk.X, ipady=12, ipadx=15)
        
        # Placeholder
        if placeholder:
            self.entry.insert(0, placeholder)
            self.entry.configure(fg='#94A3B8')
            
            def on_focus_in(event):
                if self.entry.get() == placeholder:
                    self.entry.delete(0, tk.END)
                    self.entry.configure(fg='#0F172A')
            
            def on_focus_out(event):
                if not self.entry.get():
                    self.entry.insert(0, placeholder)
                    self.entry.configure(fg='#94A3B8')
            
            self.entry.bind('<FocusIn>', on_focus_in)
            self.entry.bind('<FocusOut>', on_focus_out)
    
    def get(self):
        """Get entry value."""
        return self.entry.get()
    
    def delete(self, first, last):
        """Delete entry content."""
        self.entry.delete(first, last)
    
    def insert(self, index, string):
        """Insert into entry."""
        self.entry.insert(index, string)


class ModernButton(tk.Label):
    """Modern button with hover effects."""
    
    def __init__(self, parent, text, command, style='primary', **kwargs):
        # Define button styles
        styles = {
            'primary': {
                'bg': '#4F46E5',
                'fg': 'white',
                'hover_bg': '#4338CA'
            },
            'success': {
                'bg': '#10B981',
                'fg': 'white',
                'hover_bg': '#059669'
            },
            'danger': {
                'bg': '#EF4444',
                'fg': 'white',
                'hover_bg': '#DC2626'
            },
            'secondary': {
                'bg': '#F1F5F9',
                'fg': '#0F172A',
                'hover_bg': '#E2E8F0'
            }
        }
        
        style_config = styles.get(style, styles['primary'])
        
        super().__init__(
            parent,
            text=text,
            font=('SF Pro Display', 12, 'bold'),
            bg=style_config['bg'],
            fg=style_config['fg'],
            cursor='hand2',
            padx=30,
            pady=14,
            **kwargs
        )
        
        self.command = command
        self.normal_bg = style_config['bg']
        self.hover_bg = style_config['hover_bg']
        
        # Bind events
        self.bind('<Button-1>', lambda e: self.command())
        self.bind('<Enter>', lambda e: self.configure(bg=self.hover_bg))
        self.bind('<Leave>', lambda e: self.configure(bg=self.normal_bg))


class SidebarButton(tk.Label):
    """Sidebar menu button with hover effect."""
    
    def __init__(self, parent, text, command, **kwargs):
        super().__init__(
            parent,
            text=text,
            font=('SF Pro Display', 11),
            bg='#1E293B',
            fg='#94A3B8',
            anchor='w',
            padx=20,
            pady=12,
            cursor='hand2',
            **kwargs
        )
        
        self.command = command
        
        # Bind events
        self.bind('<Button-1>', lambda e: self.command())
        self.bind('<Enter>', lambda e: self.configure(bg='#334155', fg='white'))
        self.bind('<Leave>', lambda e: self.configure(bg='#1E293B', fg='#94A3B8'))
