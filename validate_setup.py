#!/usr/bin/env python3
"""
Development Environment Setup Validation Script
This script validates that the development environment is properly configured.
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.12+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        print("✓ Python version OK:", f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print("✗ Python version insufficient:", f"{version.major}.{version.minor}.{version.micro}")
        print("  Required: Python 3.12+")
        return False

def check_virtual_environment():
    """Check if virtual environment is activated"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        env_path = sys.prefix
        if '.mfb-env' in env_path or '.venv' in env_path:
            print("✓ Virtual environment active:", env_path)
            return True
        else:
            print("✗ Wrong virtual environment:", env_path)
            return False
    else:
        print("✗ Virtual environment not activated")
        print("  Run: source .mfb-env/bin/activate")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'flask_session', 'flask_sqlalchemy', 
        'sqlalchemy', 'werkzeug', 'pint', 'pytz', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} missing")
    
    if missing_packages:
        print("  Install missing packages: pip install -r requirements.txt")
        return False
    
    return True

def check_database():
    """Check database connectivity"""
    try:
        # Try to connect to the database
        db_path = Path('myfoodbudget.db')
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if main tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['users', 'ingredients', 'recipes', 'recipe_ingredients']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print("✗ Database missing tables:", missing_tables)
                print("  Run: python manage.py init-db")
                return False
            else:
                print("✓ Database tables OK")
                
            conn.close()
            return True
        else:
            print("✗ Database file not found")
            print("  Run: python manage.py init-db")
            return False
            
    except Exception as e:
        print("✗ Database connection error:", str(e))
        return False

def check_directories():
    """Check if required directories exist"""
    required_dirs = ['templates', 'static', 'tests', 'logs', 'barcode']
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✓ {dir_name}/ directory exists")
        else:
            print(f"✗ {dir_name}/ directory missing")
            all_exist = False
    
    return all_exist

def check_configuration():
    """Check if configuration files exist"""
    required_files = ['CLAUDE.md', 'requirements.txt', 'requirements-dev.txt']
    
    all_exist = True
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"✓ {file_name} exists")
        else:
            print(f"✗ {file_name} missing")
            all_exist = False
    
    return all_exist

def main():
    """Main validation function"""
    print("=" * 50)
    print("MyFoodBudget Development Environment Validation")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", check_dependencies),
        ("Database", check_database),
        ("Directories", check_directories),
        ("Configuration", check_configuration),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        results.append(check_func())
    
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    if all(results):
        print("🎉 All checks passed! Development environment is ready.")
        sys.exit(0)
    else:
        failed_checks = [name for (name, _), result in zip(checks, results) if not result]
        print(f"❌ {len(failed_checks)} checks failed:")
        for check in failed_checks:
            print(f"  - {check}")
        print("\nPlease fix the issues above before continuing development.")
        sys.exit(1)

if __name__ == "__main__":
    main()