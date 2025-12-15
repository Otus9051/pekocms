import datetime
import io
import os
import sys
from typing import List, Optional
from pydantic import BaseModel, Field
from fpdf import FPDF

# Add app directory to path for branding import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from branding import CLINIC_NAME, CLINIC_NAME_FORMAL, LOGO_PNG, REPORT_DELIVERY_TIMES, PATIENT_ID_LABEL

# --- Pydantic Data Models for Validation ---

class PatientDetails(BaseModel):
    name: str
    sex: str
    age: int
    phone: str
    patientId: str
    address: str

class InvoiceItem(BaseModel):
    testCode: str
    testName: str
    testFees: float
    testDescription: str = ""
    isSpecial: bool = False

class InvoiceData(BaseModel):
    patient: PatientDetails
    items: List[InvoiceItem]
    discount_percentage: float = Field(ge=0.0, le=100.0)
    home_collection_fee: float = Field(ge=0.0)
    is_paid: bool
    # Server-provided static info
    address: str
    contact: str
    # Server-calculated fields
    subtotal: float
    discount_amount: float
    round_off: float
    final_total: float

# --- PDF Generation Class (Black & White Theme) ---

class InvoicePDF(FPDF):
    def __init__(self, invoice_data: InvoiceData):
        super().__init__('P', 'mm', 'A4')
        self.invoice = invoice_data
        self.w_page = self.w - self.l_margin - self.r_margin
        self.set_auto_page_break(True, 25) # Increased footer margin
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)

    def header(self):
        # --- Center Logo ---
        logo_w = 30
        logo_x = (self.w - logo_w) / 2
        logo_y = 10
        
        # Calculate text start height (below logo)
        text_y_start = logo_y + logo_w * 2  # Estimate height or just pad
        # Better: let image draw, then move Y. But FPDF image doesn't move Y automatically.
        # We'll reserve space. Assuming square-ish logo or just using fixed height padding.
        # Let's check image existence first.
        
        try:
            # Get base path
            from app.utils import get_asset_path
            png_path = get_asset_path(LOGO_PNG)
            
            if os.path.exists(png_path):
                self.image(png_path, x=logo_x, y=logo_y, w=logo_w)
                # Move cursor down after logo (logo_y=10, assuming roughly square logo w=30 -> max_y=40)
                # Setting y to 45 gives 5mm padding
                self.set_y(logo_y + 35) 
            else:
                self.set_y(logo_y)
                self.set_font('Helvetica', 'B', 16)
                self.cell(0, 10, CLINIC_NAME, 0, 1, 'C')
                
        except Exception as e:
            print(f"Error processing logo: {e}")
            self.set_y(logo_y)
            self.set_font('Helvetica', 'B', 16)
            self.cell(0, 10, CLINIC_NAME, 0, 1, 'C')

        # --- Clinic Name and Details (CENTERED) ---
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 7, CLINIC_NAME_FORMAL, 0, 1, 'C')
        
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 5, self.invoice.address, 0, 'C')
        
        # Reset x to ensure center alignment works for the next cell
        self.set_x(10)
        self.cell(0, 5, f"Contact: {self.invoice.contact}", 0, 1, 'C')
        
        # --- Separator Line ---
        self.ln(5)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-20) 
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 5, REPORT_DELIVERY_TIMES, 0, 1, 'C')
        self.set_y(-15)
        self.cell(0, 5, 'This is a computer-generated invoice.', 0, 1, 'C')
        self.cell(0, 5, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        
    def patient_details(self, invoice_number: str):
        self.set_font('Helvetica', 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(self.w_page, 8, 'INVOICE', border=1, ln=1, align='C', fill=True)
        self.ln(2)

        col_width = self.w_page / 2
        
        self.set_font('Helvetica', 'B', 10)
        self.cell(col_width, 6, f"Patient: {self.invoice.patient.name}", 0, 0)
        self.set_font('Helvetica', '', 10)
        self.cell(col_width, 6, f"Invoice No: {invoice_number}", 0, 1, 'R')
        
        self.cell(col_width, 6, f"{PATIENT_ID_LABEL}: {self.invoice.patient.patientId}", 0, 0)
        self.cell(col_width, 6, f"Date: {datetime.date.today().strftime('%d-%b-%Y')}", 0, 1, 'R')

        self.cell(col_width, 6, f"Age/Sex: {self.invoice.patient.age}/{self.invoice.patient.sex}", 0, 0)
        self.cell(col_width, 6, f"Phone: {self.invoice.patient.phone}", 0, 1, 'R')
        self.ln(5)

    def line_items(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_fill_color(230, 230, 230)
        
        w_code, w_fees = 30, 35
        w_name = self.w_page - w_code - w_fees
        
        self.cell(w_code, 7, 'Code', 1, 0, 'C', True)
        self.cell(w_name, 7, 'Test/Service Name', 1, 0, 'L', True)
        self.cell(w_fees, 7, 'Amount (INR)', 1, 1, 'R', True)

        self.set_font('Helvetica', '', 10)
        for item in self.invoice.items:
            self.cell(w_code, 6, item.testCode, 1, 0, 'C')
            self.cell(w_name, 6, item.testName, 1, 0, 'L')
            self.cell(w_fees, 6, f"{item.testFees:,.2f}", 1, 1, 'R')
            
            # Add description only for special tests
            if item.isSpecial and item.testDescription:
                self.set_font('Helvetica', 'I', 9)
                self.cell(w_code, 4, '', 1, 0)  # Empty cell under code
                self.cell(w_name, 4, f"Description: {item.testDescription}", 1, 0, 'L')
                self.cell(w_fees, 4, '', 1, 1)  # Empty cell under fees
                self.set_font('Helvetica', '', 10)
        
        self.ln(5)

    def totals_summary(self):
        w_label = self.w_page - 45
        w_amount = 45
        
        def add_summary_line(label: str, value: float, is_bold: bool = False):
            # set_font takes (family, style, size). Build style separately.
            style = 'B' if is_bold else ''
            self.set_font('Helvetica', style, 10)
            self.cell(w_label, 6, label, 0, 0, 'R')
            self.cell(w_amount, 6, f"{value:,.2f}", 0, 1, 'R')

        add_summary_line('Subtotal:', self.invoice.subtotal)
        if self.invoice.home_collection_fee > 0:
            add_summary_line('Home Collection Fee:', self.invoice.home_collection_fee)
        if self.invoice.discount_amount > 0:
            add_summary_line(f'Discount ({self.invoice.discount_percentage:.0f}%):', -self.invoice.discount_amount)
        if self.invoice.round_off != 0:
            add_summary_line('Round Off:', self.invoice.round_off)

        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(230, 230, 230)
        self.cell(w_label, 8, 'TOTAL AMOUNT:', 1, 0, 'R', True)
        self.cell(w_amount, 8, f"{self.invoice.final_total:,.2f}", 1, 1, 'R', True)
        
        self.ln(5)
        self.set_font('Helvetica', 'B', 12)
        # Invoices are always created as PAID
        self.cell(self.w_page, 8, "STATUS: PAID IN FULL", 1, 1, 'C', True)

def generate_invoice(invoice_data: InvoiceData, invoice_number: str) -> bytes:
    """Generates the invoice PDF and returns its bytes."""
    pdf = InvoicePDF(invoice_data)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.patient_details(invoice_number)
    pdf.line_items()
    pdf.totals_summary()
    
    out = pdf.output(dest='S')
    # fpdf2 may return a str in some versions/environments; ensure bytes
    if isinstance(out, str):
        try:
            out = out.encode('latin-1')
        except Exception:
            out = out.encode('utf-8', errors='replace')
    return out