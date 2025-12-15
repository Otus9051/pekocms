"""
Special/Custom Tests Database
Stores user-defined test data (Test Name, Description, Price)
Separate from the fetched catalogue data
"""
import sqlite3
import os

# Get path to databases folder
from app.utils import get_database_dir
DB_DIR = get_database_dir()
DB_NAME = os.path.join(DB_DIR, 'special_tests.db')

def init_db():
    """Initialize the special tests database"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS special_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        testName TEXT NOT NULL,
        testDescription TEXT,
        testFees REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def add_special_test(test_data: dict) -> int:
    """Add a new special test"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO special_tests (testName, testDescription, testFees)
                 VALUES (?, ?, ?)''',
              (test_data.get('testName', ''),
               test_data.get('testDescription', ''),
               float(test_data.get('testFees', 0))))
    conn.commit()
    test_id = c.lastrowid
    conn.close()
    return test_id

def get_all_special_tests() -> list:
    """Get all special tests"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT id, testName, testDescription, testFees FROM special_tests ORDER BY testName''')
    rows = c.fetchall()
    conn.close()
    
    tests = []
    for row in rows:
        tests.append({
            'id': row[0],
            'testCode': f'SPECIAL-{row[0]}',  # Generate a special code
            'testName': row[1],
            'testDescription': row[2],
            'testFees': row[3],
            'FastingRequired': 'No',  # Special tests don't have fasting requirement
            'isSpecial': True
        })
    return tests

def delete_special_test(test_id: int) -> bool:
    """Delete a special test"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM special_tests WHERE id = ?', (test_id,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def get_special_test(test_id: int) -> dict:
    """Get a specific special test by ID"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT id, testName, testDescription, testFees FROM special_tests WHERE id = ?''', (test_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'testCode': f'SPECIAL-{row[0]}',
            'testName': row[1],
            'testDescription': row[2],
            'testFees': row[3],
            'FastingRequired': 'No',
            'isSpecial': True
        }
    return {}
def search_special_tests(query: str) -> list:
    """Search special tests by name or description"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    search_term = f'%{query.lower()}%'
    c.execute('''SELECT id, testName, testDescription, testFees 
                 FROM special_tests 
                 WHERE LOWER(testName) LIKE ? OR LOWER(testDescription) LIKE ?
                 ORDER BY testName''', (search_term, search_term))
    rows = c.fetchall()
    conn.close()
    
    tests = []
    for row in rows:
        tests.append({
            'id': row[0],
            'testCode': f'SPECIAL-{row[0]}',
            'testName': row[1],
            'testDescription': row[2],
            'testFees': row[3],
            'FastingRequired': 'No',
            'isSpecial': True
        })
    return tests