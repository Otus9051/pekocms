"""
Polyclinic Database Module
Manages doctors, availability, and patient bookings
"""
import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Get path to databases folder
from app.utils import get_database_dir
DB_DIR = get_database_dir()
DB_NAME = os.path.join(DB_DIR, 'polyclinic.db')

def _get_db_connection() -> sqlite3.Connection:
    """Establishes a connection to the polyclinic database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initializes the polyclinic database and creates tables if needed."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Create doctors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                speciality TEXT NOT NULL,
                degree TEXT NOT NULL,
                visiting_fees REAL NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create doctor_availability table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctor_availability (
                availability_id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER NOT NULL,
                day_of_week INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
            )
        """)
        
        # Create polyclinic_bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS polyclinic_bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                doctor_id INTEGER NOT NULL,
                booking_date DATE NOT NULL,
                booking_time TEXT NOT NULL,
                serial_number INTEGER NOT NULL,
                payment_status TEXT DEFAULT 'PENDING',
                attendance_status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
            )
        """)
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Polyclinic DB initialization error: {e}")
    finally:
        conn.close()

# ===== DOCTOR OPERATIONS =====

def add_doctor(name_or_dict, speciality=None, degree=None, visiting_fees=None, status='active') -> int:
    """Add a new doctor (accepts both dict and positional arguments)"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Support both dict and positional arguments
        if isinstance(name_or_dict, dict):
            name = name_or_dict.get('name')
            speciality = name_or_dict.get('speciality')
            degree = name_or_dict.get('degree')
            visiting_fees = float(name_or_dict.get('visiting_fees', 0))
            status = name_or_dict.get('status', 'active')
        else:
            name = name_or_dict
            visiting_fees = float(visiting_fees or 0)
        
        cursor.execute("""
            INSERT INTO doctors (name, speciality, degree, visiting_fees, status)
            VALUES (?, ?, ?, ?, ?)
        """, (name, speciality, degree, visiting_fees, status))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_all_doctors(active_only: bool = False) -> List[Dict[str, Any]]:
    """Get all doctors with their availability"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM doctors"
        if active_only:
            query += " WHERE status = 'active'"
        query += " ORDER BY name"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        doctors = []
        for row in rows:
            doc = dict(row)
            # Get availability for this doctor
            cursor.execute("""
                SELECT day_of_week, start_time, end_time FROM doctor_availability
                WHERE doctor_id = ? ORDER BY day_of_week, start_time
            """, (doc['doctor_id'],))
            availability = [dict(av) for av in cursor.fetchall()]
            doc['availability'] = availability
            doctors.append(doc)
        return doctors
    finally:
        conn.close()

def get_doctor(doctor_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific doctor with availability"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        doc = dict(row)
        cursor.execute("""
            SELECT day_of_week, start_time, end_time FROM doctor_availability
            WHERE doctor_id = ? ORDER BY day_of_week, start_time
        """, (doctor_id,))
        doc['availability'] = [dict(av) for av in cursor.fetchall()]
        return doc
    finally:
        conn.close()

def get_doctor_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get a doctor by name"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors WHERE name = ?", (name,))
        row = cursor.fetchone()
        if not row:
            return None
        
        doc = dict(row)
        cursor.execute("""
            SELECT day_of_week, start_time, end_time FROM doctor_availability
            WHERE doctor_id = ? ORDER BY day_of_week, start_time
        """, (doc['doctor_id'],))
        doc['availability'] = [dict(av) for av in cursor.fetchall()]
        return doc
    finally:
        conn.close()

def search_doctors(search_text: str) -> List[Dict[str, Any]]:
    """Search doctors by name or speciality"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        search_pattern = f"%{search_text.lower()}%"
        cursor.execute("""
            SELECT * FROM doctors 
            WHERE LOWER(name) LIKE ? OR LOWER(speciality) LIKE ?
            ORDER BY name
        """, (search_pattern, search_pattern))
        
        doctors = []
        for row in cursor.fetchall():
            doc = dict(row)
            cursor.execute("""
                SELECT day_of_week, start_time, end_time FROM doctor_availability
                WHERE doctor_id = ? ORDER BY day_of_week, start_time
            """, (doc['doctor_id'],))
            doc['availability'] = [dict(av) for av in cursor.fetchall()]
            doctors.append(doc)
        return doctors
    finally:
        conn.close()

def get_specialities() -> List[str]:
    """Get all unique specialities"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT speciality FROM doctors ORDER BY speciality")
        rows = cursor.fetchall()
        return [row['speciality'] for row in rows]
    finally:
        conn.close()

def update_doctor(doctor_id: int, doctor_data: Dict[str, Any]) -> bool:
    """Update doctor information"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE doctors 
            SET name = ?, speciality = ?, degree = ?, visiting_fees = ?, status = ?
            WHERE doctor_id = ?
        """, (
            doctor_data.get('name'),
            doctor_data.get('speciality'),
            doctor_data.get('degree'),
            float(doctor_data.get('visiting_fees', 0)),
            doctor_data.get('status', 'active'),
            doctor_id
        ))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_doctor(doctor_id: int) -> bool:
    """Delete a doctor and all associated data"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        # Delete availability
        cursor.execute("DELETE FROM doctor_availability WHERE doctor_id = ?", (doctor_id,))
        # Delete bookings
        cursor.execute("DELETE FROM polyclinic_bookings WHERE doctor_id = ?", (doctor_id,))
        # Delete doctor
        cursor.execute("DELETE FROM doctors WHERE doctor_id = ?", (doctor_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

# ===== DOCTOR AVAILABILITY OPERATIONS =====

def add_availability(doctor_id: int, day_of_week: int, start_time: str, end_time: str) -> int:
    """Add availability slot for a doctor"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time)
            VALUES (?, ?, ?, ?)
        """, (doctor_id, day_of_week, start_time, end_time))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_doctor_availability(doctor_id: int) -> List[Dict[str, Any]]:
    """Get availability for a doctor"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM doctor_availability
            WHERE doctor_id = ? ORDER BY day_of_week, start_time
        """, (doctor_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def delete_availability(availability_id: int) -> bool:
    """Delete an availability slot"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM doctor_availability WHERE availability_id = ?", (availability_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def clear_doctor_availability(doctor_id: int) -> None:
    """Clear all availability for a doctor"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM doctor_availability WHERE doctor_id = ?", (doctor_id,))
        conn.commit()
    finally:
        conn.close()

# ===== BOOKING OPERATIONS =====

def add_booking(patient_id_or_dict=None, doctor_id=None, booking_date=None, booking_time=None, serial_number=None, payment_status='PENDING', attendance_status='PENDING') -> int:
    """Add a new booking (accepts both dict and positional arguments)"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Support both dict and positional arguments
        if isinstance(patient_id_or_dict, dict):
            patient_id = patient_id_or_dict.get('patient_id')
            doctor_id = patient_id_or_dict.get('doctor_id')
            booking_date = patient_id_or_dict.get('booking_date')
            booking_time = patient_id_or_dict.get('booking_time')
            serial_number = patient_id_or_dict.get('serial_number')
            payment_status = patient_id_or_dict.get('payment_status', 'PENDING')
            attendance_status = patient_id_or_dict.get('attendance_status', 'PENDING')
        else:
            patient_id = patient_id_or_dict
            # If serial_number not provided, calculate it
            if serial_number is None:
                cursor.execute("""
                    SELECT MAX(serial_number) as max_serial FROM polyclinic_bookings
                    WHERE doctor_id = ? AND booking_date = ? AND booking_time = ?
                """, (doctor_id, booking_date, booking_time))
                result = cursor.fetchone()
                serial_number = (result['max_serial'] or 0) + 1
        
        cursor.execute("""
            INSERT INTO polyclinic_bookings 
            (patient_id, doctor_id, booking_date, booking_time, serial_number, payment_status, attendance_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            doctor_id,
            booking_date,
            booking_time,
            serial_number,
            payment_status,
            attendance_status
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_bookings_for_doctor_date(doctor_id: int, booking_date: str) -> List[Dict[str, Any]]:
    """Get all bookings for a doctor on a specific date"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM polyclinic_bookings
            WHERE doctor_id = ? AND booking_date = ?
            ORDER BY booking_time, serial_number
        """, (doctor_id, booking_date))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_bookings_for_doctor_date_time(doctor_id: int, booking_date: str, booking_time: str) -> List[Dict[str, Any]]:
    """Get all bookings for a doctor on a specific date and time"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM polyclinic_bookings
            WHERE doctor_id = ? AND booking_date = ? AND booking_time = ?
            ORDER BY serial_number
        """, (doctor_id, booking_date, booking_time))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_booking(booking_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific booking"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM polyclinic_bookings WHERE booking_id = ?", (booking_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_patient_bookings(patient_id: str) -> List[Dict[str, Any]]:
    """Get all bookings for a patient"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM polyclinic_bookings
            WHERE patient_id = ?
            ORDER BY booking_date DESC, booking_time DESC
        """, (patient_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_bookings_between_dates(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Get all bookings between two dates"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM polyclinic_bookings
            WHERE booking_date BETWEEN ? AND ?
            ORDER BY booking_date DESC, booking_time DESC
        """, (start_date, end_date))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def update_booking_payment_status(booking_id: int, payment_status) -> bool:
    """Update payment status of a booking (accepts both bool and string)"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        # Convert bool to string if needed
        if isinstance(payment_status, bool):
            payment_status = 'PAID' if payment_status else 'PENDING'
        cursor.execute("""
            UPDATE polyclinic_bookings SET payment_status = ? WHERE booking_id = ?
        """, (payment_status, booking_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def update_booking_attendance_status(booking_id: int, attendance_status) -> bool:
    """Update attendance status of a booking (accepts both bool and string)"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        # Convert bool to string if needed
        if isinstance(attendance_status, bool):
            attendance_status = 'ATTENDED' if attendance_status else 'PENDING'
        cursor.execute("""
            UPDATE polyclinic_bookings SET attendance_status = ? WHERE booking_id = ?
        """, (attendance_status, booking_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_booking(booking_id: int) -> bool:
    """Delete a booking"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM polyclinic_bookings WHERE booking_id = ?", (booking_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_day_summary(doctor_id: int, booking_date: str) -> Dict[str, Any]:
    """Get summary for a specific doctor-date"""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get doctor info
        cursor.execute("SELECT visiting_fees FROM doctors WHERE doctor_id = ?", (doctor_id,))
        doc_row = cursor.fetchone()
        visiting_fees = doc_row['visiting_fees'] if doc_row else 0
        
        # Get all bookings for the day
        cursor.execute("""
            SELECT * FROM polyclinic_bookings
            WHERE doctor_id = ? AND booking_date = ?
        """, (doctor_id, booking_date))
        bookings = [dict(row) for row in cursor.fetchall()]
        
        total_patients = len(bookings)
        attended = sum(1 for b in bookings if b['attendance_status'] == 'ATTENDED')
        paid = sum(1 for b in bookings if b['payment_status'] == 'PAID')
        total_fees = total_patients * visiting_fees
        collected_fees = paid * visiting_fees
        pending_fees = total_fees - collected_fees
        
        return {
            'total_patients': total_patients,
            'attended': attended,
            'paid': paid,
            'total_fees': total_fees,
            'collected_fees': collected_fees,
            'pending_fees': pending_fees,
            'visiting_fees_per_patient': visiting_fees,
            'bookings': bookings
        }
    finally:
        conn.close()
