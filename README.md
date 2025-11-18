# Invoice Generator

A professional, cross-platform (Windows + macOS) invoice generator application built with Python, Tkinter, and ReportLab.

## Features

- 🧾 **Automatic Order Numbers**: Unique invoice numbers in format `INV-YYYYMMDD-00001` (date + padded sequence)
- 💾 **Persistent Storage**: All invoices and company settings stored in SQLite database
- 📄 **Professional PDFs**: Eye-catching, print-friendly invoices with logo, company details, and itemized billing
- 💱 **Multi-Currency Support**: USD, EUR, LKR with proper formatting (thousands separators)
- 🎨 **Modern GUI**: Clean Tkinter interface with dynamic line item management
- ⚙️ **First-Time Setup**: Easy company configuration wizard on first run
- 📁 **Configurable Output**: Choose where to save generated invoice PDFs
- 🔍 **Invoice Records**: All invoices stored with metadata for easy retrieval and sorting
- ✅ **Validation**: Input validation for required fields and data integrity

## Requirements

- Python 3.10 or higher
- Works on Windows and macOS (cross-platform)

## Installation

### Step 1: Clone or Download

Download this project to your local machine.

### Step 2: Install Dependencies

Open a terminal/command prompt in the project directory and run:

**On macOS/Linux:**
```bash
python3 -m pip install -r requirements.txt
```

**On Windows:**
```cmd
python -m pip install -r requirements.txt
```

This will install:
- `reportlab` - For PDF generation
- `pillow` - For image handling (logo)

## Usage

### Running the Application

**On macOS/Linux:**
```bash
python3 main.py
```

**On Windows:**
```cmd
python main.py
```

### First-Time Setup

When you run the application for the first time, you'll see a **Company Setup** window:

1. **Company Name**: Enter your business name
2. **Company Address**: Enter your business address (use line breaks for multiple lines)
3. **Company Phone**: Enter your contact number
4. **Default Currency**: Select your preferred currency (USD, EUR, or LKR)
5. **Choose Logo**: Click to select your company logo (PNG or JPG, max 150px width recommended)
6. **Output Folder**: Click to select where invoice PDFs will be saved

Click **Save** to complete setup. These settings are stored locally and can be updated later.

### Creating an Invoice

1. **Billing Information**:
   - Enter customer name
   - Enter billing address
   - Enter customer phone number

2. **Invoice Details**:
   - Select currency (if different from default)
   - Date is auto-filled (editable)
   - Tax rate (optional, default 0%)
   - Discount amount (optional)

3. **Line Items**:
   - Click **Add Item** to add a new line
   - Enter description, quantity, and unit price
   - Click **Remove** to delete an item
   - Add as many items as needed

4. **Generate Invoice**:
   - Click **Preview** to validate without saving
   - Click **Generate Invoice** to create and save the PDF
   - Success dialog shows order number and file location
   - Click **Open Output Folder** to view saved invoices

### Settings

Click the **Settings** button to:
- Update company name, address, phone, and currency
- Change logo image
- Change output folder for PDFs
- View current invoice sequence number

## Project Structure

```
Invoice-generator/
├── main.py              # Main GUI application
├── pdf_generator.py     # PDF creation logic using ReportLab
├── db.py                # SQLite database operations
├── utils.py             # Helper functions (order numbers, currency formatting)
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── invoice_data.db     # SQLite database (created on first run)
```

## Invoice Number Format

Invoices are numbered sequentially with the format:
```
INV-YYYYMMDD-00001
```

Where:
- `INV` - Prefix
- `YYYYMMDD` - Current date (e.g., 20251118)
- `00001` - Zero-padded sequence number (resets daily)

## PDF Layout

Generated PDFs include:
- **Header**: Company logo and details on the left, invoice metadata on the right
- **Billing Section**: Customer information
- **Items Table**: Description, quantity, unit price, and line totals with alternating row colors
- **Totals Block**: Subtotal, tax, discount, and grand total (highlighted)
- **Footer**: Thank you message

## Currency Formatting

- **USD**: $1,234.56
- **EUR**: €1.234,56
- **LKR**: Rs. 1,234.56

## Database Schema

### Settings Table
Stores company configuration (name, address, phone, logo path, currency, output folder).

### Invoices Table
Stores invoice records with:
- Order number
- Date
- PDF file path
- Billing name and phone
- Currency
- Subtotal and total amounts

## Troubleshooting

### "No module named 'reportlab'"
Run: `pip install -r requirements.txt`

### Logo not appearing in PDF
- Ensure the logo file exists at the specified path
- Supported formats: PNG, JPG/JPEG
- Try selecting the logo again in Settings

### Permission errors when saving PDF
- Ensure the output folder exists and is writable
- Choose a different output folder in Settings

### Database locked errors
- Close any other instances of the application
- If the issue persists, close and restart the application

## Development

The code is modular and well-commented for easy customization:

- **db.py**: Modify database schema or add new queries
- **utils.py**: Adjust order number format or add new currencies
- **pdf_generator.py**: Customize PDF layout, colors, fonts
- **main.py**: Modify UI layout or add new features

## License

This project is provided as-is for personal and commercial use.

## Support

For issues or questions, please refer to the inline code comments or modify the code to suit your needs.

---

**Built with Python 🐍 | Tkinter | ReportLab**
