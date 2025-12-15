import sqlite3
import datetime
import json
import os
from typing import Dict, Any, List

# Get path to databases folder
from app.utils import get_database_dir
DB_DIR = get_database_dir()
DB_NAME = os.path.join(DB_DIR, 'datasheet.db')

def _get_db_connection() -> sqlite3.Connection:
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initializes the datasheet database and performs schema migrations if necessary."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    try:
        # --- Step 1: Create table if it doesn't exist ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoice_records (
                invoiceId TEXT PRIMARY KEY,
                invoiceDate TEXT NOT NULL,
                patientId TEXT NOT NULL,
                patientName TEXT NOT NULL,
                totalAmount REAL NOT NULL,
                isPaid BOOLEAN NOT NULL
            )
        """)
        
        # --- Step 2: Schema Migration - Add missing columns if they don't exist ---
        cursor.execute("PRAGMA table_info(invoice_records)")
        existing_columns = [col['name'] for col in cursor.fetchall()]
        
        columns_to_add = {
            "patientDetails": "TEXT",
            "items": "TEXT",
            "subtotal": "REAL",
            "discountPercentage": "REAL",
            "homeCollectionFee": "REAL",
            "created_by": "INTEGER",
            "roundOff": "REAL"
        }
        
        for col_name, col_type in columns_to_add.items():
            if col_name not in existing_columns:
                print(f"Datasheet DB Migration: Adding column '{col_name}'...")
                cursor.execute(f"ALTER TABLE invoice_records ADD COLUMN {col_name} {col_type}")

        conn.commit()
    except sqlite3.Error as e:
        print(f"Datasheet DB initialization/migration error: {e}")
    finally:
        conn.close()

def add_invoice_record(invoice_id: str, invoice_data: Dict[str, Any]) -> None:
    """Saves a flattened record of a generated invoice to the datasheet."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        patient_details = invoice_data.get('patient', {})
        
        cursor.execute("""
            INSERT INTO invoice_records (
                invoiceId, invoiceDate, patientId, patientName, patientDetails, 
                items, subtotal, discountPercentage, homeCollectionFee, 
                roundOff, totalAmount, isPaid, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id,
            datetime.datetime.now().isoformat(),
            patient_details.get('patientId'),
            patient_details.get('name'),
            json.dumps(patient_details),
            json.dumps(invoice_data.get('items', [])),
            invoice_data.get('subtotal'),
            invoice_data.get('discount_percentage'),
            invoice_data.get('home_collection_fee'),
            invoice_data.get('round_off'),
            invoice_data.get('final_total'),
            invoice_data.get('is_paid', False),
            invoice_data.get('created_by')
        ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding record to datasheet DB: {e}")
    finally:
        conn.close()

def get_all_invoice_records(full: bool = False) -> List[Dict[str, Any]]:
    """Retrieves all invoice records from the datasheet, newest first."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoice_records ORDER BY invoiceDate DESC")
        rows = cursor.fetchall()

        if full:
            # For exports, return the full, raw data
            return [dict(row) for row in rows]
        else:
            # For the UI table, return a simplified list
            return [
                {
                    "invoiceId": row["invoiceId"],
                    "invoiceDate": row["invoiceDate"],
                    "patientId": row["patientId"],
                    "patientName": row["patientName"],
                    "totalAmount": row["totalAmount"],
                    "isPaid": bool(row["isPaid"])
                } for row in rows
            ]
    except sqlite3.Error as e:
        print(f"Error fetching from datasheet DB: {e}")
        return []
    finally:
        conn.close()

def delete_invoice_record(invoice_id: str) -> None:
    """Deletes an invoice record from the datasheet."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM invoice_records WHERE invoiceId = ?", (invoice_id,))
        conn.commit()
    finally:
        conn.close()