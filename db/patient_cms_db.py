import sqlite3
import datetime
import json
import os
import sys
from typing import Optional, Dict, Any, List

# Add parent directory to path for branding import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.branding import PATIENT_ID_PREFIX, PATIENT_ID_FORMAT

# Get path to databases folder
from app.utils import get_database_dir
DB_DIR = get_database_dir()
DB_NAME = os.path.join(DB_DIR, 'patient_cms.db')

def _get_db_connection() -> sqlite3.Connection:
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initializes the database and creates/migrates tables."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    try:
        # Create patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patientId TEXT PRIMARY KEY, name TEXT NOT NULL, sex TEXT, age INTEGER,
                phone TEXT UNIQUE NOT NULL, email TEXT, address TEXT, created_at TEXT
            )
        """)
        
        # Create invoices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                invoiceId TEXT PRIMARY KEY, patientId TEXT NOT NULL, invoiceDate TEXT NOT NULL,
                totalAmount REAL NOT NULL, isPaid BOOLEAN NOT NULL,
                FOREIGN KEY (patientId) REFERENCES patients (patientId)
            )
        """)
        
        # Schema Migration for 'invoices' table
        cursor.execute("PRAGMA table_info(invoices)")
        existing_columns = [col['name'] for col in cursor.fetchall()]
        
        if 'invoiceData' not in existing_columns:
            print("Patient DB Migration: Adding column 'invoiceData'...")
            cursor.execute("ALTER TABLE invoices ADD COLUMN invoiceData TEXT")
        if 'discountPercentage' not in existing_columns:
            print("Patient DB Migration: Adding column 'discountPercentage'...")
            cursor.execute("ALTER TABLE invoices ADD COLUMN discountPercentage REAL NOT NULL DEFAULT 0.0")

        conn.commit()
    except sqlite3.Error as e:
        print(f"Patient CMS DB initialization error: {e}")
    finally:
        conn.close()

def _generate_patient_id(cursor: sqlite3.Cursor) -> str:
    """Generates a unique Patient ID using prefix from branding."""
    # Create pattern for searching existing IDs
    search_pattern = f"{PATIENT_ID_PREFIX}-%"
    cursor.execute(f"SELECT patientId FROM patients WHERE patientId LIKE ? ORDER BY patientId DESC LIMIT 1", (search_pattern,))
    last_id_row = cursor.fetchone()
    if last_id_row:
        # Extract number from last ID and increment
        last_id = last_id_row[0]
        # Handle both formats: "PREFIX-000001" or "PREFIX000001"
        parts = last_id.replace(PATIENT_ID_PREFIX, '').replace('-', '').lstrip('0') or '0'
        last_num = int(parts)
        next_num = last_num + 1
    else:
        next_num = 1
    return PATIENT_ID_FORMAT.format(PATIENT_ID_PREFIX, next_num)

def _dict_from_row(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    return dict(row) if row else None

def add_patient(patient_data: Dict[str, Any]) -> str:
    """Adds a new patient to the database."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        patientId = _generate_patient_id(cursor)
        cursor.execute("""
            INSERT INTO patients (patientId, name, sex, age, phone, email, address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patientId, patient_data['name'], patient_data['sex'], patient_data['age'],
            patient_data['phone'], patient_data.get('email'), patient_data['address'],
            datetime.datetime.now().isoformat()
        ))
        conn.commit()
        return patientId
    except sqlite3.IntegrityError as e:
        raise Exception(f"Phone number '{patient_data['phone']}' may already exist.") from e
    finally:
        conn.close()

def update_patient(patient_id: str, patient_data: Dict[str, Any]) -> None:
    """Updates an existing patient's details."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patients SET name=?, sex=?, age=?, phone=?, email=?, address=?
            WHERE patientId=?
        """, (
            patient_data['name'], patient_data['sex'], patient_data['age'],
            patient_data['phone'], patient_data.get('email'), patient_data['address'],
            patient_id
        ))
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise Exception(f"Phone number '{patient_data['phone']}' may already be in use by another patient.") from e
    finally:
        conn.close()

def get_patient(patient_id: str) -> Optional[Dict[str, Any]]:
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE patientId=?", (patient_id,))
        return _dict_from_row(cursor.fetchone())
    finally:
        conn.close()

def get_patient_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE phone=?", (phone,))
        return _dict_from_row(cursor.fetchone())
    finally:
        conn.close()

def get_all_patients() -> List[Dict[str, Any]]:
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients ORDER BY name ASC")
        rows = cursor.fetchall()
        # Filter out potential None rows, though unlikely
        return [dict(row) for row in rows if row]
    finally:
        conn.close()

def add_invoice(invoice_id: str, invoice_data: Dict[str, Any]) -> None:
    """Saves a record of a generated invoice."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO invoices (invoiceId, patientId, invoiceDate, totalAmount, isPaid, invoiceData, discountPercentage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id,
            invoice_data['patient']['patientId'],
            datetime.datetime.now().isoformat(),
            invoice_data['final_total'],
            invoice_data['is_paid'],
            json.dumps(invoice_data),
            invoice_data['discount_percentage']
        ))
        conn.commit()
    finally:
        conn.close()

def get_invoices_for_patient(patient_id: str) -> List[Dict[str, Any]]:
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT invoiceId, invoiceDate, totalAmount, isPaid FROM invoices WHERE patientId=? ORDER BY invoiceDate DESC", (patient_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows if row]
    finally:
        conn.close()

def get_test_history_for_patient(patient_id: str) -> List[Dict[str, Any]]:
    """Aggregates all tests from all invoices for a patient."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT invoiceId, invoiceDate, invoiceData FROM invoices WHERE patientId=? ORDER BY invoiceDate DESC", (patient_id,))
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            try:
                invoice_details = json.loads(row['invoiceData'])
                for item in invoice_details.get('items', []):
                    history.append({
                        "invoiceId": row['invoiceId'],
                        "invoiceDate": row['invoiceDate'],
                        "testCode": item.get('testCode'),
                        "testName": item.get('testName')
                    })
            except (json.JSONDecodeError, TypeError):
                continue # Skip malformed records
        return history
    finally:
        conn.close()

def delete_invoice(invoice_id: str) -> None:
    """Deletes an invoice from the database."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM invoices WHERE invoiceId=?", (invoice_id,))
        conn.commit()
    finally:
        conn.close()


def delete_patient(patient_id: str) -> None:
    """Deletes a patient and all direct references to the patient in this DB.

    Note: This function deletes the patient row from the `patients` table.
    Higher-level cleanup of invoices in other DBs (report tracker, datasheet,
    and removed PDF files) is handled by the caller (typically an admin
    route in the application) so this function keeps a single responsibility.
    """
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE patientId = ?", (patient_id,))
        conn.commit()
    finally:
        conn.close()