"""
Utility functions for Invoice Generator.

Includes:
- Order number generation (INV-YYYYMMDD-00001 format)
- Currency formatting with proper symbols and thousand separators
- Date formatting helpers
- Validation functions
"""

from datetime import datetime
from typing import Tuple
import re


# Currency configuration
CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'LKR': 'Rs. '
}

CURRENCY_NAMES = {
    'USD': 'US Dollar',
    'EUR': 'Euro',
    'LKR': 'Sri Lankan Rupee'
}


def generate_order_number(date: datetime, sequence: int) -> str:
    """
    Generate a unique order number in format INV-YYYYMMDD-00001.
    
    Args:
        date: DateTime object for the invoice date
        sequence: Sequence number for that day (1-based)
        
    Returns:
        Formatted order number string (e.g., "INV-20251118-00001")
        
    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2025, 11, 18)
        >>> generate_order_number(dt, 1)
        'INV-20251118-00001'
        >>> generate_order_number(dt, 42)
        'INV-20251118-00042'
    """
    date_str = date.strftime("%Y%m%d")
    return f"INV-{date_str}-{sequence:05d}"


def get_date_string_for_sequence(date: datetime) -> str:
    """
    Get the date string used for sequence lookups.
    
    Args:
        date: DateTime object
        
    Returns:
        Date string in YYYYMMDD format
        
    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2025, 11, 18)
        >>> get_date_string_for_sequence(dt)
        '20251118'
    """
    return date.strftime("%Y%m%d")


def format_currency(amount: float, currency_code: str) -> str:
    """
    Format amount with appropriate currency symbol and thousand separators.
    
    Args:
        amount: Numeric amount to format
        currency_code: Currency code (USD, EUR, LKR)
        
    Returns:
        Formatted currency string
        
    Example:
        >>> format_currency(1234.56, 'USD')
        '$1,234.56'
        >>> format_currency(1234.56, 'EUR')
        '€1.234,56'
        >>> format_currency(1234.56, 'LKR')
        'Rs. 1,234.56'
    """
    symbol = CURRENCY_SYMBOLS.get(currency_code, '$')
    
    if currency_code == 'EUR':
        # European format: 1.234,56
        formatted = f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"{symbol}{formatted}"
    else:
        # US/LKR format: 1,234.56
        formatted = f"{amount:,.2f}"
        return f"{symbol}{formatted}"


def parse_currency_input(value: str) -> float:
    """
    Parse a currency string input to float, handling various formats.
    
    Args:
        value: String representation of amount (may include commas, currency symbols)
        
    Returns:
        Float value of the amount
        
    Raises:
        ValueError: If the string cannot be parsed as a number
        
    Example:
        >>> parse_currency_input("1,234.56")
        1234.56
        >>> parse_currency_input("$1,234.56")
        1234.56
        >>> parse_currency_input("1234.56")
        1234.56
    """
    # Remove currency symbols and whitespace
    cleaned = re.sub(r'[^\d.,\-]', '', value.strip())
    
    # Handle empty string
    if not cleaned:
        return 0.0
    
    # Remove commas (thousand separators)
    cleaned = cleaned.replace(',', '')
    
    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(f"Cannot parse '{value}' as a number")


def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    """
    Format a datetime object as a string.
    
    Args:
        date: DateTime object to format
        format_str: strftime format string (default: YYYY-MM-DD)
        
    Returns:
        Formatted date string
        
    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2025, 11, 18)
        >>> format_date(dt)
        '2025-11-18'
        >>> format_date(dt, "%B %d, %Y")
        'November 18, 2025'
    """
    return date.strftime(format_str)


def format_date_display(date: datetime) -> str:
    """
    Format a date for display in PDFs and UI (e.g., "November 18, 2025").
    
    Args:
        date: DateTime object to format
        
    Returns:
        Human-readable date string
        
    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2025, 11, 18)
        >>> format_date_display(dt)
        'November 18, 2025'
    """
    return date.strftime("%B %d, %Y")


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number (basic validation - non-empty).
    
    Args:
        phone: Phone number string
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Example:
        >>> validate_phone("+1-555-0123")
        (True, '')
        >>> validate_phone("")
        (False, 'Phone number is required')
    """
    phone = phone.strip()
    if not phone:
        return False, "Phone number is required"
    
    return True, ""


def validate_positive_number(value: str, field_name: str = "Value") -> Tuple[bool, str]:
    """
    Validate that a string represents a positive number.
    
    Args:
        value: String to validate
        field_name: Name of the field (for error messages)
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Example:
        >>> validate_positive_number("123.45", "Price")
        (True, '')
        >>> validate_positive_number("-10", "Price")
        (False, 'Price must be a positive number')
        >>> validate_positive_number("abc", "Price")
        (False, 'Price must be a valid number')
    """
    try:
        num = parse_currency_input(value)
        if num < 0:
            return False, f"{field_name} must be a positive number"
        return True, ""
    except ValueError:
        return False, f"{field_name} must be a valid number"


def validate_quantity(value: str) -> Tuple[bool, str]:
    """
    Validate quantity (must be positive integer).
    
    Args:
        value: String to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Example:
        >>> validate_quantity("5")
        (True, '')
        >>> validate_quantity("0")
        (False, 'Quantity must be greater than 0')
        >>> validate_quantity("-1")
        (False, 'Quantity must be greater than 0')
    """
    try:
        qty = int(value.strip())
        if qty <= 0:
            return False, "Quantity must be greater than 0"
        return True, ""
    except ValueError:
        return False, "Quantity must be a valid integer"


def calculate_line_total(quantity: int, unit_price: float) -> float:
    """
    Calculate line item total.
    
    Args:
        quantity: Quantity of items
        unit_price: Price per unit
        
    Returns:
        Total amount (quantity * unit_price)
        
    Example:
        >>> calculate_line_total(5, 10.50)
        52.5
    """
    return quantity * unit_price


def calculate_invoice_totals(items: list, tax_rate: float = 0.0, 
                             discount: float = 0.0) -> dict:
    """
    Calculate invoice totals (subtotal, tax, discount, grand total).
    
    Args:
        items: List of dicts with 'quantity' and 'unit_price' keys
        tax_rate: Tax rate as percentage (e.g., 10 for 10%)
        discount: Discount amount (fixed amount, not percentage)
        
    Returns:
        Dictionary with 'subtotal', 'tax_amount', 'discount_amount', 'total'
        
    Example:
        >>> items = [{'quantity': 2, 'unit_price': 50.0}, {'quantity': 1, 'unit_price': 30.0}]
        >>> totals = calculate_invoice_totals(items, tax_rate=10, discount=5)
        >>> totals['subtotal']
        130.0
        >>> totals['tax_amount']
        13.0
        >>> totals['total']
        138.0
    """
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax_amount = subtotal * (tax_rate / 100.0)
    discount_amount = discount
    total = subtotal + tax_amount - discount_amount
    
    return {
        'subtotal': round(subtotal, 2),
        'tax_amount': round(tax_amount, 2),
        'discount_amount': round(discount_amount, 2),
        'total': round(total, 2)
    }


def get_available_currencies() -> list:
    """
    Get list of available currency codes.
    
    Returns:
        List of currency codes
        
    Example:
        >>> get_available_currencies()
        ['USD', 'EUR', 'LKR']
    """
    return list(CURRENCY_SYMBOLS.keys())


def get_currency_name(currency_code: str) -> str:
    """
    Get full name of a currency.
    
    Args:
        currency_code: Currency code (USD, EUR, LKR)
        
    Returns:
        Full currency name
        
    Example:
        >>> get_currency_name('USD')
        'US Dollar'
        >>> get_currency_name('LKR')
        'Sri Lankan Rupee'
    """
    return CURRENCY_NAMES.get(currency_code, currency_code)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length, adding suffix if truncated.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated (default: "...")
        
    Returns:
        Truncated text
        
    Example:
        >>> truncate_text("This is a long description", 10)
        'This is...'
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


# Testing and examples
if __name__ == "__main__":
    print("Testing Utils Module...")
    print()
    
    # Test order number generation
    print("=== Order Number Generation ===")
    from datetime import datetime
    test_date = datetime(2025, 11, 18)
    print(f"Order 1: {generate_order_number(test_date, 1)}")
    print(f"Order 42: {generate_order_number(test_date, 42)}")
    print(f"Order 9999: {generate_order_number(test_date, 9999)}")
    print()
    
    # Test currency formatting
    print("=== Currency Formatting ===")
    amount = 1234.56
    print(f"USD: {format_currency(amount, 'USD')}")
    print(f"EUR: {format_currency(amount, 'EUR')}")
    print(f"LKR: {format_currency(amount, 'LKR')}")
    print()
    
    # Test currency parsing
    print("=== Currency Parsing ===")
    print(f"Parse '$1,234.56': {parse_currency_input('$1,234.56')}")
    print(f"Parse '1234.56': {parse_currency_input('1234.56')}")
    print(f"Parse 'Rs. 1,234.56': {parse_currency_input('Rs. 1,234.56')}")
    print()
    
    # Test date formatting
    print("=== Date Formatting ===")
    print(f"ISO format: {format_date(test_date)}")
    print(f"Display format: {format_date_display(test_date)}")
    print()
    
    # Test validation
    print("=== Validation ===")
    print(f"Valid phone: {validate_phone('+1-555-0123')}")
    print(f"Empty phone: {validate_phone('')}")
    print(f"Valid number: {validate_positive_number('123.45', 'Price')}")
    print(f"Negative number: {validate_positive_number('-10', 'Price')}")
    print(f"Valid quantity: {validate_quantity('5')}")
    print(f"Zero quantity: {validate_quantity('0')}")
    print()
    
    # Test invoice calculations
    print("=== Invoice Calculations ===")
    test_items = [
        {'quantity': 2, 'unit_price': 50.0},
        {'quantity': 1, 'unit_price': 30.0},
        {'quantity': 3, 'unit_price': 15.0}
    ]
    totals = calculate_invoice_totals(test_items, tax_rate=10, discount=5)
    print(f"Subtotal: ${totals['subtotal']:.2f}")
    print(f"Tax (10%): ${totals['tax_amount']:.2f}")
    print(f"Discount: ${totals['discount_amount']:.2f}")
    print(f"Total: ${totals['total']:.2f}")
    print()
    
    print("Utils module tests completed!")
