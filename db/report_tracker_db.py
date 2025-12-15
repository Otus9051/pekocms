
import sqlite3
import datetime
import os
from typing import Dict, Any, List

# Get path to databases folder
from app.utils import get_database_dir
DB_DIR = get_database_dir()
DB_NAME = os.path.join(DB_DIR, 'report_tracker.db')

def _get_db_connection() -> sqlite3.Connection:
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initializes the report tracker database and table."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                invoiceId TEXT PRIMARY KEY,
                patientId TEXT NOT NULL,
                patientName TEXT NOT NULL,
                pdf_filename TEXT NOT NULL,
                status TEXT NOT NULL, -- 'Undelivered' or 'Delivered'
                vid TEXT,
                created_at TEXT NOT NULL,
                created_by INTEGER
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Report Tracker DB initialization error: {e}")
    finally:
        conn.close()

def add_report(invoice_id: str, patient_id: str, patient_name: str, pdf_filename: str, created_by: int = None) -> None:
    """Adds a new report record to the tracker, defaulting to 'Undelivered'."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reports (invoiceId, patientId, patientName, pdf_filename, status, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id,
            patient_id,
            patient_name,
            pdf_filename,
            'Undelivered',
            datetime.datetime.now().isoformat(),
            created_by
        ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding report to tracker DB: {e}")
    finally:
        conn.close()

def get_all_reports() -> List[Dict[str, Any]]:
    """Retrieves all report records, newest first."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"Error fetching from report tracker DB: {e}")
        return []
    finally:
        conn.close()

def mark_report_delivered(invoice_id: str, vid: str) -> None:
    """Updates a report's status to 'Delivered' and logs the VID."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reports
            SET status = ?, vid = ?
            WHERE invoiceId = ?
        """, ('Delivered', vid, invoice_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating report status in tracker DB: {e}")
    finally:
        conn.close()

def delete_report(invoice_id: str) -> str:
    """Deletes a report and returns its PDF filename."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        # Get the filename before deleting
        cursor.execute("SELECT pdf_filename FROM reports WHERE invoiceId = ?", (invoice_id,))
        row = cursor.fetchone()
        filename = row['pdf_filename'] if row else None
        
        # Delete the report
        cursor.execute("DELETE FROM reports WHERE invoiceId = ?", (invoice_id,))
        conn.commit()
        return filename
    finally:
        conn.close()
