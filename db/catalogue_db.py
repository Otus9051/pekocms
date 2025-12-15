import sqlite3
import json
import os
from typing import List, Dict, Any, Optional

# Get path to databases folder
from app.utils import get_database_dir
DB_DIR = get_database_dir()
DB_NAME = os.path.join(DB_DIR, 'catalogue.db')

def _get_db_connection() -> sqlite3.Connection:
    """Establishes a connection to the catalogue database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initializes the catalogue database and creates tables if needed."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Create catalogue table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS catalogue (
                testCode TEXT PRIMARY KEY,
                testName TEXT NOT NULL,
                testFees REAL NOT NULL,
                CategoryName TEXT,
                SampleType TEXT,
                SampleVolume TEXT,
                FastingRequired TEXT,
                PatientConsentForm TEXT,
                ReportedOn TEXT,
                isActive TEXT,
                MethodName TEXT,
                ProcessingDepartment TEXT,
                ClinicalUse TEXT,
                raw_data TEXT
            )
        """)
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Catalogue DB initialization error: {e}")
    finally:
        conn.close()

def add_or_update_test(test_data: Dict[str, Any]) -> None:
    """Adds or updates a single test entry in the catalogue."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO catalogue 
            (testCode, testName, testFees, CategoryName, SampleType, SampleVolume, 
             FastingRequired, PatientConsentForm, ReportedOn, isActive, MethodName, 
             ProcessingDepartment, ClinicalUse, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_data.get('testCode'),
            test_data.get('testName'),
            test_data.get('testFees', 0),
            test_data.get('CategoryName'),
            test_data.get('SampleType'),
            test_data.get('SampleVolume'),
            test_data.get('FastingRequired'),
            test_data.get('PatientConsentForm'),
            test_data.get('ReportedOn'),
            test_data.get('isActive'),
            test_data.get('MethodName'),
            test_data.get('ProcessingDepartment'),
            test_data.get('ClinicalUse'),
            json.dumps(test_data)
        ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error adding test to catalogue DB: {e}")
    finally:
        conn.close()

def bulk_add_or_update_tests(tests: List[Dict[str, Any]]) -> None:
    """Bulk insert or update tests. Clears old entries and adds new ones."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        # Clear old catalogue
        cursor.execute("DELETE FROM catalogue")
        # Insert new tests
        for test_data in tests:
            cursor.execute("""
                INSERT INTO catalogue 
                (testCode, testName, testFees, CategoryName, SampleType, SampleVolume, 
                 FastingRequired, PatientConsentForm, ReportedOn, isActive, MethodName, 
                 ProcessingDepartment, ClinicalUse, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_data.get('testCode'),
                test_data.get('testName'),
                test_data.get('testFees', 0),
                test_data.get('CategoryName'),
                test_data.get('SampleType'),
                test_data.get('SampleVolume'),
                test_data.get('FastingRequired'),
                test_data.get('PatientConsentForm'),
                test_data.get('ReportedOn'),
                test_data.get('isActive'),
                test_data.get('MethodName'),
                test_data.get('ProcessingDepartment'),
                test_data.get('ClinicalUse'),
                json.dumps(test_data)
            ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error bulk adding tests to catalogue DB: {e}")
    finally:
        conn.close()

def get_all_tests() -> List[Dict[str, Any]]:
    """Retrieves all tests from the catalogue database."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT raw_data FROM catalogue ORDER BY testName ASC")
        rows = cursor.fetchall()
        tests = []
        for row in rows:
            try:
                if row['raw_data']:
                    test = json.loads(row['raw_data'])
                    tests.append(test)
            except json.JSONDecodeError:
                pass
        return tests
    except sqlite3.Error as e:
        print(f"Error fetching from catalogue DB: {e}")
        return []
    finally:
        conn.close()

def get_test_count() -> int:
    """Returns the number of tests in the catalogue."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM catalogue")
        row = cursor.fetchone()
        return row['cnt'] if row else 0
    except sqlite3.Error as e:
        print(f"Error getting test count: {e}")
        return 0
    finally:
        conn.close()

def search_tests(query: str) -> List[Dict[str, Any]]:
    """Search tests by code or name (case-insensitive)."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        q = f"%{query.lower()}%"
        cursor.execute("""
            SELECT raw_data FROM catalogue 
            WHERE LOWER(testCode) LIKE ? OR LOWER(testName) LIKE ?
            ORDER BY testName ASC
        """, (q, q))
        rows = cursor.fetchall()
        tests = []
        for row in rows:
            try:
                test = json.loads(row['raw_data'])
                tests.append(test)
            except json.JSONDecodeError:
                pass
        return tests
    except sqlite3.Error as e:
        print(f"Error searching catalogue DB: {e}")
        return []
    finally:
        conn.close()

def get_test(test_code: str) -> Optional[Dict[str, Any]]:
    """Get a single test by test code."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT raw_data FROM catalogue 
            WHERE testCode = ?
        """, (test_code,))
        row = cursor.fetchone()
        if row:
            try:
                return json.loads(row['raw_data'])
            except json.JSONDecodeError:
                pass
        return None
    except sqlite3.Error as e:
        print(f"Error getting test from catalogue DB: {e}")
        return None
    finally:
        conn.close()
