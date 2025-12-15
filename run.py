#!/usr/bin/env python3
"""
PekoCMS - Entry Point

This script launches the application and ensures database migrations are applied.

Usage:
    python run.py
    or
    python -m app
"""
import sys
import os
import subprocess

# Ensure the project root is in the path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

def run_migrations():
    """Run database migrations before starting the application"""
    try:
        print("Checking database schema...")
        # Run migration tool with verify flag to check and migrate if needed
        result = subprocess.run(
            [sys.executable, os.path.join(PROJECT_ROOT, 'migration_tool.py')],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print("Warning: Migration check returned non-zero status")
            print(result.stdout)
            if result.stderr:
                print("Error:", result.stderr)
        else:
            print("Database schema verified")
    except Exception as e:
        print(f"Warning: Could not run migrations: {e}")
        print("The application will attempt to continue, but you may need to run the migration tool manually.")

if __name__ == '__main__':
    # Run migrations before starting the application
    run_migrations()
    
    from app.pyside_app import main
    main()
