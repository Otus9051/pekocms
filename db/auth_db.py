
import sqlite3
import datetime
import os
from typing import Optional, Dict, Any, List
from werkzeug.security import generate_password_hash, check_password_hash

# Get path to databases folder
from app.utils import get_database_dir
DB_DIR = get_database_dir()
DB_NAME = os.path.join(DB_DIR, 'auth.db')


def _get_db_connection() -> sqlite3.Connection:
    """Establishes a connection to the authentication database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def _table_has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info('{table}')")
    cols = [r['name'] for r in cur.fetchall()]
    return column in cols


def init_db() -> None:
    """Initializes the authentication database and ensures required columns exist.

    This function is migration-safe: if an existing `users` table is present but
    lacks the `full_name` column, it will be added with a sensible default.
    """
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()

        # Ensure users table exists (minimal schema). We'll migrate columns if needed.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
        """)

        # Ensure login_logs table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

        # If users table exists but missing full_name, add it and populate from username
        if not _table_has_column(conn, 'users', 'full_name'):
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT DEFAULT ''")
                # Fill full_name for existing rows with username as a reasonable default
                cursor.execute("UPDATE users SET full_name = username WHERE full_name = '' OR full_name IS NULL")
            except sqlite3.OperationalError:
                # Some older SQLite builds may not support ALTER TABLE ADD COLUMN; ignore
                pass

        conn.commit()
    except sqlite3.Error as e:
        print(f"Auth DB initialization error: {e}")
    finally:
        conn.close()


def create_user(username: str, password: str, full_name: str, role: str = 'user') -> None:
    """Creates a new user with a hashed password, full name and optional role."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
            (username, generate_password_hash(password), full_name, role)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError(f"User '{username}' already exists.")
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Retrieves a user record by their username."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves a user record by their ID."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_users() -> List[Dict[str, Any]]:
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        # Return full_name so UI can display it
        cursor.execute("SELECT id, username, full_name, role FROM users ORDER BY username ASC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def set_user_role(user_id: int, role: str) -> None:
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        conn.commit()
    finally:
        conn.close()


def log_event(user_id: Optional[int], event: str) -> None:
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO login_logs (user_id, event, timestamp) VALUES (?, ?, ?)",
            (user_id, event, datetime.datetime.now().isoformat())
        )
        conn.commit()
    finally:
        conn.close()


def get_login_logs(limit: int = 200) -> List[Dict[str, Any]]:
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM login_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def check_password(hashed_password: str, password_to_check: str) -> bool:
    """Verifies a password against its stored hash."""
    return check_password_hash(hashed_password, password_to_check)


def check_if_any_user_exists() -> bool:
    """Checks if there is at least one user in the database. Used for setup."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users LIMIT 1")
        return cursor.fetchone() is not None
    finally:
        conn.close()

def update_user(user_id: str, password: Optional[str] = None, full_name: Optional[str] = None, role: Optional[str] = None) -> None:
    """Updates user information. Password update is optional."""
    conn = _get_db_connection()
    try:
        cursor = conn.cursor()
        # First check if user exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            raise ValueError(f"User ID {user_id} not found")
        
        # Build update query dynamically based on provided fields
        updates = []
        params = []
        
        if full_name is not None:
            updates.append("full_name = ?")
            params.append(full_name)
        
        if role is not None:
            if role not in ['admin', 'user']:
                raise ValueError("Invalid role. Must be 'admin' or 'user'")
            updates.append("role = ?")
            params.append(role)
        
        if password is not None and password.strip():
            updates.append("password = ?")
            params.append(generate_password_hash(password))
        
        if not updates:
            raise ValueError("No fields to update")
        
        # Add user_id to params and execute update
        params.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", tuple(params))
        conn.commit()
    finally:
        conn.close()
