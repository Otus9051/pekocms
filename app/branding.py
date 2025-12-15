"""
Branding Configuration for PekoCMS

This module contains all branding elements, making them easy to customize:
- Application name and titles
- Contact information
- Logo paths and settings
- Report display times
- ID prefix and formatting
"""
import os
import yaml

# Add parent directory to path to find config.yaml
from app.utils import get_config_path
CONFIG_PATH = get_config_path()

# Default Config
config = {
    "APP_NAME": "PekoCMS",
    "CLINIC_NAME": "PekoCMS",
    "CLINIC_NAME_FORMAL": "PekoCMS",
    "CLINIC_ADDRESS": "Pekoland",
    "CLINIC_CONTACT": "+1 (234)-567-8901",
    "FOOTER_TEXT": "Made by Otus9051 | Powered by PekoCMS",
    "LOGO_SVG": "logo.svg",
    "LOGO_PNG": "logo_print.png",
    "REPORT_DELIVERY_TIMES": "Reports will be given from 12:00 PM to 2:00 PM and 5:00 PM to 8:00 PM.",
    "PATIENT_ID_PREFIX": "PEK",
}

# Load config.yaml if it exists
if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f)
            if user_config:
                config.update(user_config)
    except Exception as e:
        print(f"Warning: Could not load config.yaml: {e}")

# ============================================================================
# APPLICATION BRANDING
# ============================================================================

# Main application name
APP_NAME = config["APP_NAME"]

# Login window title
LOGIN_WINDOW_TITLE = f"{APP_NAME} - Login"

# Login window heading
LOGIN_WINDOW_HEADING = f"{APP_NAME} Login"

# Clinic/Business name (used in headers, PDFs, etc.)
CLINIC_NAME = config["CLINIC_NAME"]

# Full clinic name with department (used in PDFs and formal documents)
CLINIC_NAME_FORMAL = config["CLINIC_NAME_FORMAL"]

# First word of clinic name (used in filenames)
CLINIC_NAME_PREFIX = CLINIC_NAME.split()[0]  # e.g., "Nidaan"

# Footer Text
FOOTER_TEXT = config["FOOTER_TEXT"]

# ============================================================================
# CONTACT & LOCATION INFORMATION
# ============================================================================

# Clinic physical address
CLINIC_ADDRESS = config["CLINIC_ADDRESS"]

# Clinic contact numbers (phone/WhatsApp)
CLINIC_CONTACT = config["CLINIC_CONTACT"]

# ============================================================================
# LOGO & ASSET FILES
# ============================================================================

# Assets directory name (contains logos and images)
from app.constants import ASSETS_DIRECTORY

# Logo SVG file (used in login window and header)
LOGO_SVG = config["LOGO_SVG"]

# Logo PNG file (used in PDF invoices)
LOGO_PNG = config["LOGO_PNG"]

# ============================================================================
# PATIENT ID & NAMING
# ============================================================================

# Patient ID prefix (e.g., NID)
PATIENT_ID_PREFIX = config["PATIENT_ID_PREFIX"]

# Patient ID format: "NID-{next_num:06d}" (6-digit zero-padded number)
# Results in: NID-000001, NID-000002, etc.
PATIENT_ID_FORMAT = "{}-{:06d}"

# Column headers
PATIENT_ID_COLUMN_NAME = "Patient ID"

# Form field label
PATIENT_ID_LABEL = "Patient ID"

# ============================================================================
# REPORT DELIVERY TIMES
# ============================================================================

# Report delivery hours (displayed in PDF footers)
REPORT_DELIVERY_TIMES = config["REPORT_DELIVERY_TIMES"]

# ============================================================================
# FOLDER & DIRECTORY NAMES
# ============================================================================

# Folder name for invoices storage in user's home directory
# Windows: C:\Users\<Username>\Clinic\invoices
# Linux/macOS: ~/Clinic/invoices
from app.constants import INVOICE_FOLDER_NAME, INVOICE_SUBDIRECTORY

# ============================================================================
# USER INTERFACE STRINGS
# ============================================================================

# Mode button labels
MODE_PATHOLOGY = "PATHOLOGY"
MODE_POLYCLINIC = "POLYCLINIC"
MODE_ADMIN = "ADMIN"

# Button labels
BUTTON_SIGN_IN = "Sign In"
BUTTON_SHUTDOWN = "Shutdown"
BUTTON_REGISTER = "Register"
BUTTON_REFRESH = "🔄 Refresh"
BUTTON_EXPORT = "📊 Export Day Data"

# Window titles for different modes
WINDOW_TITLE_PATHOLOGY = APP_NAME
WINDOW_TITLE_POLYCLINIC = APP_NAME
WINDOW_TITLE_ADMIN = APP_NAME

# Form labels
FORM_LABEL_USERNAME = "Username"
FORM_LABEL_PASSWORD = "Password"

# Success/Error messages
MSG_INVOICE_CREATED = "Invoice {invoice_number} created"
MSG_PATIENT_REGISTERED = "Patient {patient_id} created"
MSG_PATIENT_UPDATED = "Patient updated successfully"

# ============================================================================
# TABLE & COLUMN HEADERS
# ============================================================================

# Patient CMS table headers
PATIENT_TABLE_HEADERS = ["PatientId", "Name", "Phone", "Age", "Email", "Address", "Action"]

# Invoice queue table headers
QUEUE_TABLE_HEADERS = [
    "Serial",
    "Patient Name",
    "Patient ID",
    "Doctor",
    "Time Slot",
    "Phone",
    "Payment",
    "Attendance",
    "Delete"
]

# Report tracker table headers
REPORT_TABLE_HEADERS = [
    "InvoiceId",
    "Patient",
    "Patient ID",
    "Status",
    "VID",
    "Created At",
    "Action"
]

# Datasheet export headers
DATASHEET_HEADERS = [
    "Serial",
    "Patient Name",
    "Patient ID",
    "Phone",
    "Payment",
    "Attendance",
    "Fees"
]

# ============================================================================
# DEFAULT FILE NAMES
# ============================================================================

# Default CSV export filename pattern
DEFAULT_CSV_FILENAME = "datasheet_{date}.csv"

# Default XLSX export filename pattern
DEFAULT_XLSX_FILENAME = "datasheet_{date}.xlsx"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_patient_id(number: int) -> str:
    """Generate a formatted patient ID from a number.
    
    Args:
        number: Sequential patient number (e.g., 1, 2, 123)
    
    Returns:
        Formatted patient ID (e.g., "NID-000001")
    """
    return PATIENT_ID_FORMAT.format(PATIENT_ID_PREFIX, number)


def get_invoice_folder_path() -> str:
    """Get the full path for the invoice folder in user's home directory.
    
    Returns:
        Full path like "C:\\Users\\Username\\Nidaan\\invoices"
    """
    import os
    home = os.path.expanduser("~")
    return os.path.join(home, INVOICE_FOLDER_NAME, INVOICE_SUBDIRECTORY)
