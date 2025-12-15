#!/usr/bin/env python3
"""
Database Migration Tool - PekoCMS

This tool performs the following operations:
1. Creates backups of all databases
2. Migrates database schema: nidaanId -> patientId, nidaan_id -> patient_id
3. Recreates tables with renamed columns to ensure data integrity
4. Verifies migration success

Specific migrations:
- patient_cms.db:      patients(nidaanId->patientId), invoices(nidaanId->patientId)
- report_tracker.db:   reports(nidaanId->patientId)
- polyclinic.db:       polyclinic_bookings(nidaan_id->patient_id)
- datasheet.db:        invoice_records(nidaanId->patientId)

Usage:
    python migration_tool.py                 # Run full migration
    python migration_tool.py --backup-only   # Only create backups
    python migration_tool.py --rollback      # Restore from last backup
    python migration_tool.py --verify        # Verify without migrating
"""

import os
import sys
import json
import shutil
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.utils import get_database_dir


class DatabaseMigrator:
    """Handles database migration from nidaanId to patientId"""
    
    # Database file renames
    DB_FILE_RENAMES = {
        'nidaan_cms.db': 'patient_cms.db',
    }
    
    # Define specific migrations for each database
    MIGRATIONS = {
        'patient_cms.db': [
            ('patients', 'nidaanId', 'patientId'),
            ('invoices', 'nidaanId', 'patientId'),
        ],
        'report_tracker.db': [
            ('reports', 'nidaanId', 'patientId'),
        ],
        'polyclinic.db': [
            ('polyclinic_bookings', 'nidaan_id', 'patient_id'),
        ],
        'datasheet.db': [
            ('invoice_records', 'nidaanId', 'patientId'),
        ],
    }
    
    def __init__(self, db_dir: str = None):
        if db_dir is None:
            self.db_dir = Path(get_database_dir())
        else:
            self.db_dir = Path(db_dir)
        self.backup_dir = self.db_dir / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.backup_dir / "migration.log"
        self.migration_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log migration messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        self.migration_log.append(log_msg)
        print(log_msg)
    
    def save_log(self):
        """Save migration log to file"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.migration_log))
        self.log(f"Log saved to {self.log_file}")
    
    def backup_databases(self) -> bool:
        """Create backups of all database files"""
        try:
            self.log("Starting database backup...")
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup old database file names too
            db_files = []
            for old_name, new_name in self.DB_FILE_RENAMES.items():
                old_path = self.db_dir / old_name
                if old_path.exists():
                    db_files.append(old_path)
            
            # Backup current database names
            for db_name in self.MIGRATIONS.keys():
                db_path = self.db_dir / db_name
                if db_path.exists():
                    db_files.append(db_path)
            
            if not db_files:
                self.log("No database files found", "WARNING")
                return False
            
            for db_file in db_files:
                backup_file = self.backup_dir / db_file.name
                shutil.copy2(db_file, backup_file)
                self.log(f"Backed up: {db_file.name} -> {backup_file}")
            
            self.log(f"Successfully backed up {len(db_files)} database(s)")
            return True
        except Exception as e:
            self.log(f"Backup failed: {e}", "ERROR")
            return False
    
    def get_table_columns(self, db_path: Path, table_name: str) -> List[str]:
        """Get all column names for a table"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            conn.close()
            return columns
        except Exception as e:
            self.log(f"Error getting columns from {table_name}: {e}", "ERROR")
            return []
    
    def table_exists(self, db_path: Path, table_name: str) -> bool:
        """Check if a table exists in the database"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            self.log(f"Error checking table {table_name}: {e}", "ERROR")
            return False
    
    def get_table_schema(self, db_path: Path, table_name: str) -> str:
        """Get the CREATE TABLE statement for a table"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            self.log(f"Error getting schema for {table_name}: {e}", "ERROR")
            return None
    
    def rename_column_via_recreate(self, db_path: Path, table_name: str, old_col: str, new_col: str) -> bool:
        """Rename a column by recreating the table (safest method for SQLite)"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if old column exists
            columns = self.get_table_columns(db_path, table_name)
            if old_col not in columns:
                self.log(f"Column '{old_col}' not found in {table_name}", "WARNING")
                return False
            
            # Check if new column already exists
            if new_col in columns:
                self.log(f"Column '{new_col}' already exists in {table_name}", "WARNING")
                return False
            
            # Get original schema
            original_schema = self.get_table_schema(db_path, table_name)
            if not original_schema:
                self.log(f"Could not get schema for {table_name}", "ERROR")
                return False
            
            # Create new schema with renamed column
            new_schema = original_schema.replace(f" {old_col} ", f" {new_col} ").replace(f"({old_col}", f"({new_col}").replace(f" {old_col},", f" {new_col},")
            
            # Build column list for INSERT - map old names to new names
            col_list = ", ".join([f"{new_col if c == old_col else c}" for c in columns])
            old_col_list = ", ".join(columns)  # Original columns from temp table
            
            try:
                # Begin transaction
                cursor.execute("BEGIN TRANSACTION")
                
                # Create temporary table
                temp_table = f"temp_{table_name}"
                cursor.execute(f"ALTER TABLE {table_name} RENAME TO {temp_table}")
                
                # Create new table with renamed column
                cursor.execute(new_schema)
                
                # Copy data from temporary table (map old column to new column name)
                cursor.execute(f"INSERT INTO {table_name} SELECT {old_col_list} FROM {temp_table}")
                
                # Drop temporary table
                cursor.execute(f"DROP TABLE {temp_table}")
                
                # Commit transaction
                cursor.execute("COMMIT")
                conn.commit()
                
                self.log(f"Renamed column: {table_name}.{old_col} -> {new_col}")
                return True
            except Exception as e:
                cursor.execute("ROLLBACK")
                raise e
            finally:
                conn.close()
        except Exception as e:
            self.log(f"Error renaming column {old_col} in {table_name}: {e}", "ERROR")
            return False
    
    def rename_database_files(self) -> bool:
        """Rename database files from old names to new names"""
        try:
            self.log("Checking for database files to rename...")
            
            renamed_count = 0
            for old_name, new_name in self.DB_FILE_RENAMES.items():
                old_path = self.db_dir / old_name
                new_path = self.db_dir / new_name
                
                if not old_path.exists():
                    self.log(f"Database file '{old_name}' not found (skipping rename)", "INFO")
                    continue
                
                if new_path.exists():
                    self.log(f"New database file '{new_name}' already exists, keeping it", "WARNING")
                    continue
                
                try:
                    old_path.rename(new_path)
                    self.log(f"Renamed database file: {old_name} -> {new_name}")
                    renamed_count += 1
                except Exception as e:
                    self.log(f"Error renaming {old_name} to {new_name}: {e}", "ERROR")
                    return False
            
            if renamed_count > 0:
                self.log(f"Successfully renamed {renamed_count} database file(s)")
            return True
        except Exception as e:
            self.log(f"Database file rename failed: {e}", "ERROR")
            return False
    
    def migrate_database(self, db_name: str, db_path: Path) -> bool:
        """Migrate a single database file based on predefined migrations"""
        try:
            self.log(f"Migrating database: {db_name}")
            
            if db_name not in self.MIGRATIONS:
                self.log(f"No migration defined for {db_name}", "WARNING")
                return True
            
            migration_count = 0
            for table_name, old_col, new_col in self.MIGRATIONS[db_name]:
                # Check if table exists
                if not self.table_exists(db_path, table_name):
                    self.log(f"Table '{table_name}' not found in {db_name}", "WARNING")
                    continue
                
                # Check if old column exists
                columns = self.get_table_columns(db_path, table_name)
                if old_col not in columns:
                    self.log(f"Column '{old_col}' not found in {table_name}", "WARNING")
                    continue
                
                # Check if new column already exists
                if new_col in columns:
                    self.log(f"Column '{new_col}' already exists in {table_name}", "INFO")
                    migration_count += 1
                    continue
                
                # Perform migration
                if self.rename_column_via_recreate(db_path, table_name, old_col, new_col):
                    migration_count += 1
            
            self.log(f"Completed {migration_count} column migration(s) in {db_name}")
            return True
        except Exception as e:
            self.log(f"Database migration error in {db_name}: {e}", "ERROR")
            return False
    
    def migrate_all_databases(self) -> bool:
        """Migrate all databases in the directory"""
        try:
            # Step 1: Rename database files
            if not self.rename_database_files():
                self.log("Database file rename failed", "ERROR")
                return False
            
            print()
            
            # Step 2: Migrate column names
            db_files = []
            for db_name in self.MIGRATIONS.keys():
                db_path = self.db_dir / db_name
                if db_path.exists():
                    db_files.append((db_name, db_path))
            
            if not db_files:
                self.log("No database files found to migrate", "WARNING")
                return False
            
            self.log(f"Found {len(db_files)} database file(s) to migrate columns")
            
            success_count = 0
            for db_name, db_path in db_files:
                if self.migrate_database(db_name, db_path):
                    success_count += 1
            
            self.log(f"Successfully migrated {success_count}/{len(db_files)} database(s)")
            return success_count == len(db_files)
        except Exception as e:
            self.log(f"Migration failed: {e}", "ERROR")
            return False
    
    def verify_migration(self) -> bool:
        """Verify that migration was successful"""
        try:
            self.log("Verifying migration...")
            all_good = True
            
            for db_name, migrations in self.MIGRATIONS.items():
                db_path = self.db_dir / db_name
                if not db_path.exists():
                    self.log(f"Database {db_name} not found (skipping verification)", "WARNING")
                    continue
                
                for table_name, old_col, new_col in migrations:
                    if not self.table_exists(db_path, table_name):
                        self.log(f"Table {table_name} not found in {db_name} (skipping)", "WARNING")
                        continue
                    
                    columns = self.get_table_columns(db_path, table_name)
                    
                    # Check for old column names
                    if old_col in columns:
                        self.log(f"[FAIL] Issue: '{old_col}' still exists in {db_name}.{table_name}", "ERROR")
                        all_good = False
                    else:
                        self.log(f"[OK] Old column '{old_col}' removed from {db_name}.{table_name}")
                    
                    # Check for new column names
                    if new_col in columns:
                        self.log(f"[OK] New column '{new_col}' found in {db_name}.{table_name}")
                    else:
                        self.log(f"[FAIL] Issue: '{new_col}' not found in {db_name}.{table_name}", "ERROR")
                        all_good = False
            
            if all_good:
                self.log("[OK] Migration verification passed", "INFO")
            else:
                self.log("[FAIL] Migration verification found issues", "ERROR")
            
            return all_good
        except Exception as e:
            self.log(f"Verification error: {e}", "ERROR")
            return False
    
    def rollback_migration(self) -> bool:
        """Rollback to previous backup"""
        try:
            backups = sorted(list((self.db_dir / "backups").glob("*")), reverse=True)
            if not backups:
                self.log("No backups found to rollback", "ERROR")
                return False
            
            latest_backup = backups[0]
            self.log(f"Rolling back to backup: {latest_backup.name}")
            
            # Restore backup files
            restored_count = 0
            for backup_file in latest_backup.glob("*.db"):
                restore_file = self.db_dir / backup_file.name
                shutil.copy2(backup_file, restore_file)
                self.log(f"Restored: {backup_file.name}")
                restored_count += 1
            
            self.log(f"Rollback completed successfully ({restored_count} files restored)")
            return True
        except Exception as e:
            self.log(f"Rollback failed: {e}", "ERROR")
            return False


    def check_already_migrated(self) -> bool:
        """Check if migration has already been performed"""
        try:
            # Check patient_cms.db -> patients table
            db_path = self.db_dir / "patient_cms.db"
            if not db_path.exists():
                return False
                
            columns = self.get_table_columns(db_path, "patients")
            if "patientId" in columns and "nidaanId" not in columns:
                return True
                
            return False
        except Exception as e:
            self.log(f"Error checking migration status: {e}", "ERROR")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Database Migration Tool - Nidaan to Patient ID"
    )
    parser.add_argument(
        "--backup-only",
        action="store_true",
        help="Only create backups without migrating"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify migration without making changes"
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback to previous backup"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force migration even if it appears already done"
    )
    parser.add_argument(
        "--db-dir",
        default=None,
        help="Database directory path (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator(args.db_dir)
    
    print("=" * 70)
    print("PekoCMS - Database Migration Tool")
    print("=" * 70)
    print()
    
    try:
        # Check if already migrated
        if not args.backup_only and not args.verify and not args.rollback and not args.force:
            if migrator.check_already_migrated():
                print("[INFO] System appears to be already migrated (patientId found).")
                print("       No changes were made.")
                print("       Use --force to run migration anyway.")
                return 0

        # If verify only (without backup)
        if args.verify and not args.backup_only and not args.rollback:
            if migrator.verify_migration():
                print("\n[OK] Verification completed successfully")
                return 0
            else:
                print("\n[FAIL] Verification found issues")
                return 1
        
        # Step 1: Backup
        if not migrator.backup_databases():
            print("ERROR: Backup failed. Aborting migration.")
            return 1
        
        print()
        
        # If only backup is requested
        if args.backup_only:
            migrator.save_log()
            print("\n[OK] Backup completed successfully")
            print(f"[OK] Backups saved to: {migrator.backup_dir}")
            return 0
        
        # If rollback is requested
        if args.rollback:
            if migrator.rollback_migration():
                migrator.save_log()
                print("\n[OK] Rollback completed successfully")
                print(f"[OK] Log saved to: {migrator.log_file}")
                return 0
            else:
                print("\n[FAIL] Rollback failed")
                migrator.save_log()
                return 1
        
        # Step 2: Migrate
        if not migrator.migrate_all_databases():
            print("ERROR: Migration failed")
            migrator.save_log()
            print(f"[OK] Log saved to: {migrator.log_file}")
            return 1
        
        print()
        
        # Step 3: Verify
        if not migrator.verify_migration():
            print("WARNING: Verification found issues")
            migrator.save_log()
            print(f"[OK] Log saved to: {migrator.log_file}")
            return 1
        
        print()
        
        migrator.save_log()
        print("=" * 70)
        print("[OK] Migration completed successfully!")
        print(f"[OK] Backups saved to: {migrator.backup_dir}")
        print(f"[OK] Log saved to: {migrator.log_file}")
        print("=" * 70)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\nMigration interrupted by user")
        migrator.save_log()
        return 1
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        migrator.save_log()
        return 1


if __name__ == "__main__":
    sys.exit(main())

