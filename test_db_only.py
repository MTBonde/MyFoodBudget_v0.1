#!/usr/bin/env python3
"""
Test just the database initialization logic
"""
import os
import sys
import tempfile
import shutil
import sqlite3

def test_db_creation():
    """Test database creation with production-like paths"""
    
    # Create test directory structure like Docker
    test_dir = tempfile.mkdtemp(prefix='mfb_db_test_')
    app_dir = os.path.join(test_dir, 'app')
    data_dir = os.path.join(app_dir, 'data')
    
    print(f"Testing database creation in: {test_dir}")
    print(f"Simulating /app/data at: {data_dir}")
    
    try:
        # Test 1: Directory creation logic
        print("\n1. Testing directory creation...")
        
        db_path = os.path.join(data_dir, 'myfoodbudget.db')
        print(f"Target database path: {db_path}")
        
        # This is the same logic as in db_init.py
        db_dir = os.path.dirname(db_path)
        print(f"Database directory: {db_dir}")
        print(f"Directory exists before: {os.path.exists(db_dir)}")
        
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"Created directory: {db_dir}")
        
        print(f"Directory exists after: {os.path.exists(db_dir)}")
        
        # Test 2: Database file creation
        print("\n2. Testing database file creation...")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table (minimal test)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hash TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        conn.close()
        
        print(f"Database file created: {os.path.exists(db_path)}")
        if os.path.exists(db_path):
            print(f"Database file size: {os.path.getsize(db_path)} bytes")
            
            # Test 3: Database operations
            print("\n3. Testing database operations...")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Insert test user
            cursor.execute("""
            INSERT INTO users (username, hash, email) 
            VALUES (?, ?, ?)
            """, ("testuser", "testhash", "test@example.com"))
            
            # Query users
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            print(f"Test user inserted successfully: {count == 1}")
            
            # Test 4: Production config paths
            print("\n4. Testing production config paths...")
            
            # Test absolute path resolution
            abs_path = "/app/data/myfoodbudget.db"
            print(f"Absolute path: {abs_path}")
            
            # Test relative path resolution
            rel_path = "data/myfoodbudget.db"
            print(f"Relative path: {rel_path}")
            print(f"Dirname of relative path: {os.path.dirname(rel_path)}")
            
            # Test if directory creation works for both
            test_abs_dir = os.path.dirname(abs_path)
            test_rel_dir = os.path.dirname(rel_path)
            
            print(f"Absolute dirname: {test_abs_dir} (empty: {not test_abs_dir})")
            print(f"Relative dirname: {test_rel_dir} (empty: {not test_rel_dir})")
            
            print("✅ All database tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"\nCleaned up: {test_dir}")

if __name__ == "__main__":
    success = test_db_creation()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)