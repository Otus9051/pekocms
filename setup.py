#!/usr/bin/env python3
"""
Setup & Verification Script for PekoCMS

This script:
1. Moves static/ → assets/ directory
2. Verifies all imports are correct
3. Checks for hardcoded branding strings
4. Creates necessary directories
5. Validates configuration
"""

import os
import sys
import shutil
from pathlib import Path

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def check_hardcoded_branding():
    """Check for hardcoded branding strings that should use branding.py"""
    print_section("Checking for Hardcoded Branding Strings")
    
    hardcoded_terms = [
        "nidaan",
        "Nidaan",
        "NIDAAN",
        "\"Clinic",
        "Clinic\"",
    ]
    
    app_dir = Path("app")
    issues = []
    
    for py_file in app_dir.glob("*.py"):
        if py_file.name in ["branding.py", "__init__.py", "__main__.py"]:
            continue
        
        with open(py_file) as f:
            for line_num, line in enumerate(f, 1):
                # Skip comments and imports from branding
                if line.strip().startswith("#") or "from branding import" in line:
                    continue
                
                for term in hardcoded_terms:
                    if term.lower() in line.lower() and "branding" not in line.lower():
                        issues.append(f"{py_file.name}:{line_num} - {line.strip()[:60]}")
    
    if issues:
        print(f"⚠ Found {len(issues)} potential hardcoded branding references:")
        for issue in issues[:10]:  # Show first 10
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    else:
        print("✓ No hardcoded branding strings found")

def move_static_to_assets():
    """Move static directory to assets"""
    print_section("Moving static/ → assets/")
    
    static_dir = Path("static")
    assets_dir = Path("assets")
    
    if not static_dir.exists():
        print("⚠ static/ directory not found")
        return False
    
    if assets_dir.exists():
        print("✓ assets/ directory already exists")
        # Check if files are there
        files = list(assets_dir.glob("*"))
        if files:
            print(f"✓ Found {len(files)} file(s) in assets/")
            return True
        else:
            print("✓ assets/ is empty, proceeding with move...")
            shutil.rmtree(assets_dir)
    
    try:
        shutil.move(str(static_dir), str(assets_dir))
        print(f"✓ Successfully moved static/ → assets/")
        return True
    except Exception as e:
        print(f"✗ Failed to move directory: {e}")
        return False

def verify_assets():
    """Verify assets directory contains required files"""
    print_section("Verifying Assets")
    
    assets_dir = Path("assets")
    required_files = ["nidaan.svg", "nidaan_outline.png"]
    
    if not assets_dir.exists():
        print("✗ assets/ directory not found")
        return False
    
    files = list(assets_dir.glob("*"))
    print(f"✓ Found {len(files)} file(s) in assets/:")
    for f in files:
        print(f"  - {f.name}")
    
    for required in required_files:
        if (assets_dir / required).exists():
            print(f"✓ {required} found")
        else:
            print(f"⚠ {required} not found (may need to add manually)")
    
    return True

def verify_imports():
    """Verify key imports are working"""
    print_section("Verifying Imports")
    
    try:
        sys.path.insert(0, str(Path("app").absolute()))
        
        from branding import (
            APP_NAME, CLINIC_NAME, CLINIC_ADDRESS,
            LOGO_SVG, LOGO_PNG, ASSETS_DIRECTORY,
            PATIENT_ID_PREFIX, PATIENT_ID_COLUMN_NAME,
            QUEUE_TABLE_HEADERS, REPORT_TABLE_HEADERS
        )
        
        print("✓ All branding constants imported successfully")
        print(f"  - APP_NAME: {APP_NAME}")
        print(f"  - CLINIC_NAME: {CLINIC_NAME}")
        print(f"  - ASSETS_DIRECTORY: {ASSETS_DIRECTORY}")
        print(f"  - PATIENT_ID_PREFIX: {PATIENT_ID_PREFIX}")
        print(f"  - LOGO_SVG: {LOGO_SVG}")
        print(f"  - LOGO_PNG: {LOGO_PNG}")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def check_migration_tool():
    """Verify migration tool exists and is executable"""
    print_section("Checking Migration Tool")
    
    tool = Path("migration_tool.py")
    
    if tool.exists():
        print(f"✓ migration_tool.py found")
        print(f"  Location: {tool.absolute()}")
        print(f"  Size: {tool.stat().st_size} bytes")
        print(f"\n  Usage:")
        print(f"    python migration_tool.py              # Run migration")
        print(f"    python migration_tool.py --backup-only # Backup only")
        print(f"    python migration_tool.py --rollback    # Restore backup")
        return True
    else:
        print("✗ migration_tool.py not found")
        return False

def check_databases_dir():
    """Verify databases directory exists"""
    print_section("Checking Databases Directory")
    
    db_dir = Path("databases")
    
    if db_dir.exists():
        db_files = list(db_dir.glob("*.db"))
        print(f"✓ databases/ directory exists")
        print(f"✓ Found {len(db_files)} database file(s):")
        for db in db_files:
            size_mb = db.stat().st_size / (1024 * 1024)
            print(f"  - {db.name} ({size_mb:.2f} MB)")
        return True
    else:
        print("✗ databases/ directory not found")
        print("  Creating databases/ directory...")
        db_dir.mkdir(exist_ok=True)
        print("✓ databases/ created")
        return True

def create_missing_dirs():
    """Create necessary directories if they don't exist"""
    print_section("Creating Missing Directories")
    
    dirs = [
        "databases",
        "databases/backups",
        "assets",
        "invoice_storage",
    ]
    
    created = 0
    for dir_path in dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {dir_path}")
            created += 1
        else:
            print(f"✓ Exists: {dir_path}")
    
    return True

def main():
    """Run all checks and migrations"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  PekoCMS - Setup & Verification Script".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = {
        "Create directories": create_missing_dirs(),
        "Check databases": check_databases_dir(),
        "Move assets": move_static_to_assets(),
        "Verify assets": verify_assets(),
        "Check migration tool": check_migration_tool(),
        "Verify imports": verify_imports(),
        "Check hardcoded strings": check_hardcoded_branding(),
    }
    
    print_section("Summary")
    
    print("\nResults:")
    for check, result in results.items():
        status = "✓ PASS" if result else "⚠ WARNING"
        print(f"  {status}: {check}")
    
    if all(results.values()):
        print("\n" + "=" * 70)
        print("✓ All checks passed! System is ready to use.")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Run migration tool (if upgrading from nidaanId):")
        print("   python migration_tool.py")
        print("\n2. Start the application:")
        print("   python run.py")
        return 0
    else:
        print("\n" + "=" * 70)
        print("⚠ Some checks had warnings. Please review above.")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
