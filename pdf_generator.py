"""
PDF Generator for Invoice Generator.

Uses ReportLab to create professional, print-friendly PDF invoices with:
- Company logo and details
- Invoice metadata (order number, date, currency)
- Billing information
- Itemized table with alternating row colors
- Totals block (subtotal, tax, discount, grand total)
- Footer with thank you message

Layout: A4 page size, clean design with proper spacing and typography.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from PIL import Image as PILImage
import utils


class InvoicePDF:
    """Generate professional invoice PDFs using ReportLab."""
    
    def __init__(self, filename: str):
        """
        Initialize PDF generator.
        
        Args:
            filename: Output PDF file path
        """
        self.filename = filename
        self.width, self.height = A4
        self.margin = 0.75 * inch
        
        # Color scheme
        self.color_primary = colors.HexColor('#2C3E50')
        self.color_secondary = colors.HexColor('#3498DB')
        self.color_accent = colors.HexColor('#E74C3C')
        self.color_light_gray = colors.HexColor('#ECF0F1')
        self.color_dark_gray = colors.HexColor('#7F8C8D')
        
        # Styles
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles."""
        # Company name style
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=self.color_primary,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Invoice title style
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.color_secondary,
            spaceAfter=12,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=11,
            textColor=self.color_primary,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Normal text style
        self.styles.add(ParagraphStyle(
            name='InvoiceText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            spaceAfter=3
        ))
        
        # Small text style (footer)
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=self.color_dark_gray,
            alignment=TA_CENTER
        ))
    
    def _process_logo(self, logo_path: str, max_width: float = 150) -> Optional[Image]:
        """
        Process logo image: validate, scale while preserving aspect ratio.
        
        Args:
            logo_path: Path to logo image file
            max_width: Maximum width in points (default: 150)
            
        Returns:
            ReportLab Image object or None if invalid
        """
        try:
            logo_file = Path(logo_path)
            if not logo_file.exists():
                print(f"Logo file not found: {logo_path}")
                return None
            
            # Open with PIL to get dimensions
            with PILImage.open(logo_file) as img:
                width, height = img.size
                
                # Calculate scaled dimensions
                aspect_ratio = height / width
                scaled_width = max_width
                scaled_height = max_width * aspect_ratio
                
                # Create ReportLab Image
                logo = Image(str(logo_file), width=scaled_width, height=scaled_height)
                return logo
                
        except Exception as e:
            print(f"Error processing logo: {e}")
            return None
    
    def generate(self, invoice_data: Dict, company_data: Dict, items: List[Dict]) -> bool:
        """
        Generate the invoice PDF.
        
        Args:
            invoice_data: Dict with keys:
                - order_number: str
                - invoice_date: datetime
                - billing_name: str
                - billing_address: str
                - billing_phone: str
                - currency: str
                - tax_rate: float (percentage)
                - discount_amount: float
            company_data: Dict with keys:
                - company_name: str
                - company_address: str
                - company_phone: str
                - logo_path: str (optional)
            items: List of dicts with keys:
                - description: str
                - quantity: int
                - unit_price: float
                
        Returns:
            True if PDF generated successfully, False otherwise.
        """
        try:
            # Create document
            doc = SimpleDocTemplate(
                self.filename,
                pagesize=A4,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            
            # Build content
            story = []
            
            # Header section
            story.extend(self._build_header(company_data, invoice_data))
            story.append(Spacer(1, 0.3 * inch))
            
            # Billing section
            story.extend(self._build_billing_section(invoice_data))
            story.append(Spacer(1, 0.3 * inch))
            
            # Items table
            story.extend(self._build_items_table(items, invoice_data['currency']))
            story.append(Spacer(1, 0.2 * inch))
            
            # Totals section
            story.extend(self._build_totals_section(
                items, 
                invoice_data['currency'],
                invoice_data.get('tax_rate', 0),
                invoice_data.get('discount_amount', 0)
            ))
            story.append(Spacer(1, 0.4 * inch))
            
            # Footer
            story.extend(self._build_footer())
            
            # Build PDF
            doc.build(story, onFirstPage=self._add_page_number, 
                     onLaterPages=self._add_page_number)
            
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
    
    def _build_header(self, company_data: Dict, invoice_data: Dict) -> List:
        """Build the header section with logo, company info, and invoice metadata."""
        elements = []
        
        # Create table for header layout (logo + company info | invoice info)
        header_data = []
        
        # Left side: Logo and company info
        left_content = []
        
        # Add logo if available
        logo = None
        if company_data.get('logo_path'):
            logo = self._process_logo(company_data['logo_path'])
        
        if logo:
            left_content.append(logo)
        
        # Company details
        company_name = Paragraph(
            f"<b>{company_data['company_name']}</b>",
            self.styles['CompanyName']
        )
        left_content.append(company_name)
        
        company_address = Paragraph(
            company_data['company_address'].replace('\n', '<br/>'),
            self.styles['InvoiceText']
        )
        left_content.append(company_address)
        
        company_phone = Paragraph(
            f"Phone: {company_data['company_phone']}",
            self.styles['InvoiceText']
        )
        left_content.append(company_phone)
        
        # Right side: Invoice metadata
        right_content = []
        
        invoice_title = Paragraph("<b>INVOICE</b>", self.styles['InvoiceTitle'])
        right_content.append(invoice_title)
        
        order_num = Paragraph(
            f"<b>Order #:</b> {invoice_data['order_number']}",
            self.styles['InvoiceText']
        )
        right_content.append(order_num)
        
        date_formatted = utils.format_date_display(invoice_data['invoice_date'])
        invoice_date = Paragraph(
            f"<b>Date:</b> {date_formatted}",
            self.styles['InvoiceText']
        )
        right_content.append(invoice_date)
        
        currency = Paragraph(
            f"<b>Currency:</b> {invoice_data['currency']}",
            self.styles['InvoiceText']
        )
        right_content.append(currency)
        
        # Create nested tables for left and right content
        left_table = Table([[item] for item in left_content], colWidths=[3 * inch])
        left_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        right_table = Table([[item] for item in right_content], colWidths=[2.5 * inch])
        right_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        # Main header table
        header_table = Table(
            [[left_table, right_table]],
            colWidths=[4 * inch, 2.5 * inch]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(header_table)
        
        return elements
    
    def _build_billing_section(self, invoice_data: Dict) -> List:
        """Build the billing information section."""
        elements = []
        
        # Section heading
        heading = Paragraph("<b>BILL TO:</b>", self.styles['SectionHeading'])
        elements.append(heading)
        
        # Billing details
        billing_name = Paragraph(
            f"<b>{invoice_data['billing_name']}</b>",
            self.styles['InvoiceText']
        )
        elements.append(billing_name)
        
        billing_address = Paragraph(
            invoice_data['billing_address'].replace('\n', '<br/>'),
            self.styles['InvoiceText']
        )
        elements.append(billing_address)
        
        billing_phone = Paragraph(
            f"Phone: {invoice_data['billing_phone']}",
            self.styles['InvoiceText']
        )
        elements.append(billing_phone)
        
        return elements
    
    def _build_items_table(self, items: List[Dict], currency: str) -> List:
        """Build the itemized table with descriptions, quantities, and prices."""
        elements = []
        
        # Table headers
        headers = ['#', 'Description', 'Qty', 'Unit Price', 'Total']
        
        # Build table data
        table_data = [headers]
        
        for i, item in enumerate(items, 1):
            line_total = utils.calculate_line_total(
                item['quantity'], 
                item['unit_price']
            )
            
            row = [
                str(i),
                item['description'],
                str(item['quantity']),
                utils.format_currency(item['unit_price'], currency),
                utils.format_currency(line_total, currency)
            ]
            table_data.append(row)
        
        # Create table
        col_widths = [0.4 * inch, 3.5 * inch, 0.6 * inch, 1 * inch, 1 * inch]
        
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Style the table
        table_style = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), self.color_primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # # column
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Description
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Qty
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),  # Prices
            
            # Grid and padding
            ('GRID', (0, 0), (-1, -1), 0.5, self.color_dark_gray),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]
        
        # Alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(
                    ('BACKGROUND', (0, i), (-1, i), self.color_light_gray)
                )
        
        items_table.setStyle(TableStyle(table_style))
        elements.append(items_table)
        
        return elements
    
    def _build_totals_section(self, items: List[Dict], currency: str, 
                              tax_rate: float, discount_amount: float) -> List:
        """Build the totals section (subtotal, tax, discount, grand total)."""
        elements = []
        
        # Calculate totals
        totals = utils.calculate_invoice_totals(items, tax_rate, discount_amount)
        
        # Create totals table (right-aligned)
        totals_data = []
        
        # Subtotal
        totals_data.append([
            Paragraph('<b>Subtotal:</b>', self.styles['InvoiceText']),
            Paragraph(
                utils.format_currency(totals['subtotal'], currency),
                self.styles['InvoiceText']
            )
        ])
        
        # Tax
        if tax_rate > 0:
            totals_data.append([
                Paragraph(f'<b>Tax ({tax_rate}%):</b>', self.styles['InvoiceText']),
                Paragraph(
                    utils.format_currency(totals['tax_amount'], currency),
                    self.styles['InvoiceText']
                )
            ])
        
        # Discount
        if discount_amount > 0:
            totals_data.append([
                Paragraph('<b>Discount:</b>', self.styles['InvoiceText']),
                Paragraph(
                    f"- {utils.format_currency(totals['discount_amount'], currency)}",
                    self.styles['InvoiceText']
                )
            ])
        
        # Grand Total
        totals_data.append([
            Paragraph('<b>GRAND TOTAL:</b>', self.styles['SectionHeading']),
            Paragraph(
                f"<b>{utils.format_currency(totals['total'], currency)}</b>",
                self.styles['SectionHeading']
            )
        ])
        
        # Create table
        totals_table = Table(
            totals_data,
            colWidths=[1.5 * inch, 1.2 * inch],
            hAlign='RIGHT'
        )
        
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -2), 9),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, -1), (-1, -1), 2, self.color_primary),
            ('BACKGROUND', (0, -1), (-1, -1), self.color_light_gray),
        ]))
        
        elements.append(totals_table)
        
        return elements
    
    def _build_footer(self) -> List:
        """Build the footer with thank you message."""
        elements = []
        
        footer_text = Paragraph(
            "<i>Thank you for your business!</i>",
            self.styles['SmallText']
        )
        elements.append(footer_text)
        
        return elements
    
    def _add_page_number(self, canvas_obj, doc):
        """Add page number to bottom of page."""
        page_num = canvas_obj.getPageNumber()
        text = f"Page {page_num}"
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(self.color_dark_gray)
        canvas_obj.drawRightString(
            self.width - self.margin,
            self.margin / 2,
            text
        )
        canvas_obj.restoreState()


def create_invoice_pdf(filename: str, invoice_data: Dict, 
                       company_data: Dict, items: List[Dict]) -> bool:
    """
    Convenience function to create an invoice PDF.
    
    Args:
        filename: Output PDF file path
        invoice_data: Invoice metadata and billing info
        company_data: Company details
        items: List of line items
        
    Returns:
        True if successful, False otherwise.
        
    Example:
        >>> from datetime import datetime
        >>> invoice_data = {
        ...     'order_number': 'INV-20251118-00001',
        ...     'invoice_date': datetime(2025, 11, 18),
        ...     'billing_name': 'John Doe',
        ...     'billing_address': '123 Main St',
        ...     'billing_phone': '+1-555-9999',
        ...     'currency': 'USD',
        ...     'tax_rate': 10,
        ...     'discount_amount': 5
        ... }
        >>> company_data = {
        ...     'company_name': 'Acme Corp',
        ...     'company_address': '456 Business Ave',
        ...     'company_phone': '+1-555-0123',
        ...     'logo_path': '/path/to/logo.png'
        ... }
        >>> items = [
        ...     {'description': 'Product A', 'quantity': 2, 'unit_price': 50.0},
        ...     {'description': 'Product B', 'quantity': 1, 'unit_price': 30.0}
        ... ]
        >>> create_invoice_pdf('invoice.pdf', invoice_data, company_data, items)
        True
    """
    pdf = InvoicePDF(filename)
    return pdf.generate(invoice_data, company_data, items)


# Testing
if __name__ == "__main__":
    print("Testing PDF Generator Module...")
    
    from datetime import datetime
    
    # Sample data
    test_invoice_data = {
        'order_number': 'INV-20251118-00001',
        'invoice_date': datetime(2025, 11, 18),
        'billing_name': 'John Doe',
        'billing_address': '123 Customer Street\nApt 4B\nNew York, NY 10001',
        'billing_phone': '+1-555-9999',
        'currency': 'USD',
        'tax_rate': 10,
        'discount_amount': 5.0
    }
    
    test_company_data = {
        'company_name': 'Acme Corporation',
        'company_address': '456 Business Avenue\nSuite 100\nNew York, NY 10002',
        'company_phone': '+1-555-0123',
        'logo_path': None  # No logo for test
    }
    
    test_items = [
        {
            'description': 'Professional Web Design Service',
            'quantity': 1,
            'unit_price': 1500.0
        },
        {
            'description': 'Logo Design (includes 3 revisions)',
            'quantity': 1,
            'unit_price': 500.0
        },
        {
            'description': 'Monthly Hosting (12 months)',
            'quantity': 12,
            'unit_price': 25.0
        },
        {
            'description': 'SEO Optimization Package',
            'quantity': 1,
            'unit_price': 800.0
        }
    ]
    
    # Generate test PDF
    test_pdf_path = Path("test_invoice.pdf")
    success = create_invoice_pdf(
        str(test_pdf_path),
        test_invoice_data,
        test_company_data,
        test_items
    )
    
    if success and test_pdf_path.exists():
        print(f"✓ Test PDF generated successfully: {test_pdf_path}")
        print(f"  File size: {test_pdf_path.stat().st_size} bytes")
    else:
        print("✗ Failed to generate test PDF")
    
    print("\nPDF Generator module tests completed!")
