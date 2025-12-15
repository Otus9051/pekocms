"""Worker threads for background operations in PekoCMS"""
import sys
import os
from PySide6 import QtCore

# Add parent directory to path for db imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import catalogue_db
from db import data_fetcher
from db import special_tests_db


class CatalogueLoaderThread(QtCore.QThread):
    """Worker thread for loading catalogue data - loads from cache first"""
    finished = QtCore.Signal()
    status_updated = QtCore.Signal(str)
    catalogue_loaded = QtCore.Signal(list)
    
    def run(self):
        """Run in separate thread - load from cache first, then fetch if needed"""
        try:
            # Load from SQLite cache first (instant)
            cached_data = catalogue_db.get_all_tests()
            if cached_data:
                self.status_updated.emit(f"Loaded {len(cached_data)} tests from cache")
                # Don't block waiting for web data - use cache immediately
            else:
                # Cache is empty - try to fetch fresh data from the server
                self.status_updated.emit("Loading data from server (this may take 1-2 minutes)...")
                fresh_data = data_fetcher.get_catalogue_data()
                if fresh_data:
                    # Store in local database
                    for test in fresh_data:
                        catalogue_db.add_or_update_test(test)
                    cached_data = fresh_data
                    self.status_updated.emit(f"Loaded {len(fresh_data)} tests from server")
                else:
                    self.status_updated.emit("No test data available")
        except Exception as e:
            # Use cached data on error
            try:
                cached_data = catalogue_db.get_all_tests()
                if cached_data:
                    self.status_updated.emit(f"Using cached data ({len(cached_data)} tests)")
                else:
                    self.status_updated.emit("No test data available")
            except:
                self.status_updated.emit("No test data available")
        finally:
            self.finished.emit()


class InvoiceCatalogueLoaderThread(QtCore.QThread):
    """Worker thread for loading invoice catalogue"""
    catalogue_loaded = QtCore.Signal(list, str)
    error_occurred = QtCore.Signal(str)
    
    def run(self):
        """Run in separate thread"""
        try:
            cat = catalogue_db.get_all_tests()
            if not cat:
                cat = data_fetcher.get_catalogue_data()
                status = data_fetcher.get_fetch_status()
                status_msg = status[:50]
            else:
                status_msg = f"Loaded {len(cat)} tests from cache"
            self.catalogue_loaded.emit(cat, status_msg)
        except Exception as e:
            self.error_occurred.emit(f"Error loading: {str(e)}")


class SpecialTestsLoaderThread(QtCore.QThread):
    """Worker thread for loading special tests"""
    tests_loaded = QtCore.Signal(list)
    error_occurred = QtCore.Signal(str)
    
    def run(self):
        """Run in separate thread"""
        try:
            special_tests = special_tests_db.get_all_special_tests()
            self.tests_loaded.emit(special_tests)
        except Exception as e:
            self.error_occurred.emit(f"Error loading special tests: {str(e)}")


class FullCatalogueLoaderThread(QtCore.QThread):
    """Worker thread for loading full catalogue data"""
    data_ready = QtCore.Signal(list)
    error_occurred = QtCore.Signal(str)
    
    def run(self):
        """Run in separate thread"""
        try:
            data = data_fetcher.get_catalogue_data()
            self.data_ready.emit(data)
        except Exception as e:
            self.error_occurred.emit(f"Error loading catalogue: {str(e)}")
