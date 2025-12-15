import os
import sys
import time
import datetime
import threading
import subprocess
from . import catalogue_db
from app.utils import get_database_dir

# --- CONFIGURATION ---
REFRESH_INTERVAL_SECONDS = 3600 
SYNC_WORKER_FILENAME = "sync_worker.exe"

# --- GLOBAL DATA STORE (Kept for UI compatibility, though mainly unused now) ---
_CATALOGUE_DATA = [] 
_FETCH_STATUS = "Not Initialized"

def get_fetch_status() -> str:
    return _FETCH_STATUS

def get_catalogue_data() -> list:
    return _CATALOGUE_DATA

# --- DATA FETCHING LAUNCHER ---
def fetch_catalogue_data() -> None:
    global _FETCH_STATUS
    
    if "Fetching..." in _FETCH_STATUS:
        print(f"[{datetime.datetime.now()}] Skipping fetch, one is already running.")
        return

    _FETCH_STATUS = f"Fetching... (Started: {datetime.datetime.now().strftime('%H:%M:%S')})"
    print(f"[{datetime.datetime.now()}] {_FETCH_STATUS}")
    
    try:
        # Determine path to sync_worker.exe
        # 1. Check in current directory (typical for dev)
        # 2. Check in sys._MEIPASS (if bundled, though we plan to keep it separate)
        # 3. Check in dist/PekoCMS (for manual dev testing)
        
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        worker_path = os.path.join(base_path, SYNC_WORKER_FILENAME)
        
        # If running from source, logic might differ, assume proprietary/ folder built
        if not getattr(sys, 'frozen', False):
            # Development mode specific path if needed
             pass

        if not os.path.exists(worker_path):
             _FETCH_STATUS = f"Sync worker not found ({SYNC_WORKER_FILENAME}). Using offline mode."
             print(f"[{datetime.datetime.now()}] {_FETCH_STATUS}")
             return

        # Prepare DB PATH
        db_path = os.path.join(get_database_dir(), catalogue_db.DB_NAME)

        # Launch Worker
        # CREATE_NO_WINDOW = 0x08000000 ensures no console pops up on Windows
        subprocess.run([worker_path, db_path], check=True, creationflags=0x08000000)
        
        _FETCH_STATUS = f"SUCCESS: Sync complete. (Last Refresh: {datetime.datetime.now().strftime('%H:%M:%S')})"
        
    except subprocess.CalledProcessError as e:
        _FETCH_STATUS = f"FAILURE: Worker Error (Code {e.returncode})"
    except Exception as e:
        _FETCH_STATUS = f"FAILURE: Launcher Error: {e}"
    finally:
        print(f"[{datetime.datetime.now()}] {_FETCH_STATUS}")

def start_fetch_scheduler() -> None:
    def scheduler_loop():
        # Initial wait to let app startup finish
        time.sleep(5) 
        fetch_catalogue_data()
        while True:
            # print(f"[{datetime.datetime.now()}] Next data refresh in {REFRESH_INTERVAL_SECONDS} seconds.")
            time.sleep(REFRESH_INTERVAL_SECONDS)
            fetch_catalogue_data()

    scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
    scheduler_thread.start()