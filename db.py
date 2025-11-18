"""
Database module for Invoice Generator.

Handles SQLite database operations for storing:
- Company settings (name, address, logo, currency, output folder)
- Invoice records (order number, date, billing info, amounts, PDF path)

Uses pathlib for cross-platform file path handling.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime


class Database:
    """SQLite database wrapper for invoice and settings management."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. Defaults to 'invoice_data.db' in current directory.
        """
        if db_path is None:
            db_path = Path.cwd() / "invoice_data.db"
        
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Settings table - stores company configuration (single row)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                company_name TEXT NOT NULL,
                company_address TEXT NOT NULL,
                company_phone TEXT NOT NULL,
                logo_path TEXT,
                default_currency TEXT DEFAULT 'USD',
                output_folder TEXT NOT NULL,
                invoice_sequence INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Invoices table - stores all generated invoices
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                invoice_date TEXT NOT NULL,
                billing_name TEXT NOT NULL,
                billing_address TEXT,
                billing_phone TEXT NOT NULL,
                currency TEXT NOT NULL,
                subtotal REAL NOT NULL,
                tax_amount REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                total REAL NOT NULL,
                pdf_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on order_number for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_order_number 
            ON invoices(order_number)
        """)
        
        # Create index on invoice_date for sorting
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_invoice_date 
            ON invoices(invoice_date DESC)
        """)
        
        self.conn.commit()
    
    def is_first_run(self) -> bool:
        """
        Check if this is the first run (no company settings exist).
        
        Returns:
            True if no company settings exist, False otherwise.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM settings")
        count = cursor.fetchone()[0]
        return count == 0
    
    def save_company_settings(self, name: str, address: str, phone: str, 
                             logo_path: Optional[str], currency: str, 
                             output_folder: str) -> bool:
        """
        Save or update company settings.
        
        Args:
            name: Company name
            address: Company address
            phone: Company phone number
            logo_path: Path to company logo image (can be None)
            currency: Default currency code (USD, EUR, LKR)
            output_folder: Path to folder where PDFs are saved
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            
            # Check if settings exist
            cursor.execute("SELECT id FROM settings WHERE id = 1")
            exists = cursor.fetchone()
            
            if exists:
                # Update existing settings
                cursor.execute("""
                    UPDATE settings 
                    SET company_name = ?, 
                        company_address = ?, 
                        company_phone = ?,
                        logo_path = ?,
                        default_currency = ?,
                        output_folder = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = 1
                """, (name, address, phone, logo_path, currency, output_folder))
            else:
                # Insert new settings
                cursor.execute("""
                    INSERT INTO settings 
                    (id, company_name, company_address, company_phone, 
                     logo_path, default_currency, output_folder)
                    VALUES (1, ?, ?, ?, ?, ?, ?)
                """, (name, address, phone, logo_path, currency, output_folder))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error saving settings: {e}")
            return False
    
    def get_company_settings(self) -> Optional[Dict]:
        """
        Retrieve company settings.
        
        Returns:
            Dictionary with company settings or None if not found.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM settings WHERE id = 1")
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_next_invoice_sequence(self, date_str: str) -> int:
        """
        Get the next invoice sequence number for a given date.
        
        Args:
            date_str: Date in format YYYYMMDD
            
        Returns:
            Next sequence number for that date (1 if first invoice of the day).
        """
        cursor = self.conn.cursor()
        
        # Find the highest sequence number for invoices with this date prefix
        cursor.execute("""
            SELECT order_number FROM invoices 
            WHERE order_number LIKE ? 
            ORDER BY order_number DESC 
            LIMIT 1
        """, (f"INV-{date_str}-%",))
        
        row = cursor.fetchone()
        
        if row:
            # Extract sequence number from order_number (e.g., INV-20251118-00001 -> 1)
            order_num = row['order_number']
            sequence = int(order_num.split('-')[-1])
            return sequence + 1
        
        return 1  # First invoice of the day
    
    def save_invoice(self, order_number: str, invoice_date: str, 
                    billing_name: str, billing_address: str, 
                    billing_phone: str, currency: str, 
                    subtotal: float, tax_amount: float, 
                    discount_amount: float, total: float, 
                    pdf_path: str) -> bool:
        """
        Save an invoice record to the database.
        
        Args:
            order_number: Unique order number (e.g., INV-20251118-00001)
            invoice_date: Invoice date string
            billing_name: Customer name
            billing_address: Customer address
            billing_phone: Customer phone
            currency: Currency code
            subtotal: Subtotal amount
            tax_amount: Tax amount
            discount_amount: Discount amount
            total: Grand total
            pdf_path: Path to generated PDF file
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO invoices 
                (order_number, invoice_date, billing_name, billing_address,
                 billing_phone, currency, subtotal, tax_amount, 
                 discount_amount, total, pdf_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_number, invoice_date, billing_name, billing_address,
                  billing_phone, currency, subtotal, tax_amount, 
                  discount_amount, total, pdf_path))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error saving invoice: {e}")
            return False
    
    def get_invoice_by_order_number(self, order_number: str) -> Optional[Dict]:
        """
        Retrieve an invoice by order number.
        
        Args:
            order_number: Order number to search for
            
        Returns:
            Dictionary with invoice data or None if not found.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM invoices WHERE order_number = ?
        """, (order_number,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_all_invoices(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve all invoices, ordered by date (newest first).
        
        Args:
            limit: Optional limit on number of results
            
        Returns:
            List of invoice dictionaries.
        """
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM invoices ORDER BY invoice_date DESC, created_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_invoices_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Retrieve invoices within a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of invoice dictionaries.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM invoices 
            WHERE invoice_date >= ? AND invoice_date <= ?
            ORDER BY invoice_date DESC
        """, (start_date, end_date))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_total_invoices_count(self) -> int:
        """
        Get total number of invoices in database.
        
        Returns:
            Count of invoices.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM invoices")
        return cursor.fetchone()[0]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - closes connection."""
        self.close()


# Example usage and testing
if __name__ == "__main__":
    # Test database operations
    print("Testing Database Module...")
    
    # Create test database
    test_db_path = Path("test_invoice.db")
    if test_db_path.exists():
        test_db_path.unlink()  # Delete existing test database
    
    db = Database(test_db_path)
    
    # Test first run check
    print(f"Is first run: {db.is_first_run()}")
    
    # Test saving company settings
    success = db.save_company_settings(
        name="Acme Corporation",
        address="123 Business St\nSuite 100\nNew York, NY 10001",
        phone="+1-555-0123",
        logo_path="/path/to/logo.png",
        currency="USD",
        output_folder="/path/to/invoices"
    )
    print(f"Settings saved: {success}")
    
    # Test retrieving settings
    settings = db.get_company_settings()
    print(f"Retrieved settings: {settings['company_name']}")
    
    # Test invoice sequence
    date_str = "20251118"
    seq = db.get_next_invoice_sequence(date_str)
    print(f"Next sequence for {date_str}: {seq}")
    
    # Test saving invoice
    order_num = f"INV-{date_str}-{seq:05d}"
    success = db.save_invoice(
        order_number=order_num,
        invoice_date="2025-11-18",
        billing_name="John Doe",
        billing_address="456 Customer Ave",
        billing_phone="+1-555-9999",
        currency="USD",
        subtotal=100.0,
        tax_amount=10.0,
        discount_amount=5.0,
        total=105.0,
        pdf_path=f"/path/to/{order_num}.pdf"
    )
    print(f"Invoice saved: {success}")
    
    # Test retrieving invoice
    invoice = db.get_invoice_by_order_number(order_num)
    print(f"Retrieved invoice: {invoice['order_number']} - {invoice['billing_name']}")
    
    # Test getting all invoices
    all_invoices = db.get_all_invoices()
    print(f"Total invoices: {len(all_invoices)}")
    
    # Cleanup
    db.close()
    test_db_path.unlink()
    print("\nDatabase module tests completed!")
