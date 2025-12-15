import os
import sys
import time
import datetime
from typing import Dict, Any, Optional

# Import pdf_generator from app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.pdf_generator import generate_invoice, InvoiceData
from app.branding import CLINIC_NAME_PREFIX

from . import patient_cms_db
from . import datasheet_db
from . import report_tracker_db


def create_and_save_invoice(data: Dict[str, Any], created_by: Optional[int], address: str, contact: str, invoice_storage_dir: str = 'invoice_storage') -> Dict[str, Any]:
    """Creates an invoice, saves DB records, generates PDF and returns info dict.

    Keeps behavior compatible with the previous Flask implementation.
    """
    data = dict(data)  # shallow copy

    # Add static info and calculate totals
    data['address'] = address
    data['contact'] = contact

    subtotal = sum(item.get('testFees', 0) for item in data.get('items', []))
    home_fee = data.get('home_collection_fee', 0)
    total_before_discount = subtotal + home_fee
    discount_perc = data.get('discount_percentage', 0)
    discount_amount = total_before_discount * (discount_perc / 100.0)
    total_after_discount = total_before_discount - discount_amount
    rounded_total = round(total_after_discount)
    round_off = rounded_total - total_after_discount

    data['subtotal'] = total_before_discount
    data['discount_amount'] = discount_amount
    data['round_off'] = round_off
    data['final_total'] = rounded_total

    invoice_data_model = InvoiceData.model_validate(data)
    invoice_number = f"INV-{datetime.date.today().strftime('%y%m%d')}-{str(int(time.time() * 1000))[-5:]}"

    # Attach creator info
    invoice_dict = invoice_data_model.model_dump()
    invoice_dict['created_by'] = created_by

    # Save to databases
    patient_cms_db.add_invoice(invoice_number, invoice_dict)
    datasheet_db.add_invoice_record(invoice_number, invoice_dict)

    # Generate PDF
    pdf_bytes = generate_invoice(invoice_data_model, invoice_number)

    # Ensure invoice storage directory exists
    os.makedirs(invoice_storage_dir, exist_ok=True)
    patient_name_safe = "".join(c for c in invoice_data_model.patient.name if c.isalnum() or c in " _-").rstrip()
    filename = f"{CLINIC_NAME_PREFIX}_{invoice_number}_{patient_name_safe}.pdf"
    filepath = os.path.join(invoice_storage_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(pdf_bytes)

    # Add to report tracker
    try:
        # Handle both old and new patient ID field names for backwards compatibility
        patient_id = getattr(invoice_data_model.patient, 'patientId', None)
        report_tracker_db.add_report(invoice_number, patient_id, invoice_data_model.patient.name, filename, created_by=created_by)
    except Exception:
        # Don't fail the entire operation if tracker fails
        pass

    return {
        'invoice_number': invoice_number,
        'filename': filename,
        'filepath': os.path.abspath(filepath),
        'pdf_bytes': pdf_bytes
    }
