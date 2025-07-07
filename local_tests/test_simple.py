#!/usr/bin/env python3
"""
Simple test to verify production database setup works
"""
import os
import tempfile
import shutil

# Set environment to production
os.environ['FLASK_ENV'] = 'production'

# Create test directory structure
test_dir = tempfile.mkdtemp(prefix='mfb_prod_test_')
app_dir = os.path.join(test_dir, 'app')
data_dir = os.path.join(app_dir, 'data')

print(f"Testing in: {test_dir}")
print(f"Simulating /app/data at: {data_dir}")

try:
    # Change to test directory to simulate Docker environment
    original_cwd = os.getcwd()
    os.chdir(test_dir)
    
    # Create app directory
    os.makedirs(app_dir, exist_ok=True)
    
    # Copy our source files to test directory
    import sys
    sys.path.insert(0, original_cwd)
    
    # Test 1: Check if production config is loaded
    print("\n1. Testing production config detection...")
    from app_factory import create_app
    app = create_app()
    
    print(f"Debug mode: {app.config.get('DEBUG')}")
    print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print(f"Database path: {app.config.get('DATABASE', 'Not set')}")
    
    # Test 2: Check if database directory gets created
    print("\n2. Testing database directory creation...")
    
    # Test with actual production paths
    with app.app_context():
        from db_init import initialize_database
        
        # Check if data directory exists before
        print(f"Data directory exists before: {os.path.exists('/app/data')}")
        
        # This should create the directory and database
        initialize_database()
        
        # Check if database file was created
        db_path = app.config.get('DATABASE', '/app/data/myfoodbudget.db')
        print(f"Database path from config: {db_path}")
        print(f"Database exists: {os.path.exists(db_path)}")
        
        if os.path.exists(db_path):
            print(f"Database file size: {os.path.getsize(db_path)} bytes")
            
            # Test 3: Test database operations
            print("\n3. Testing database operations...")
            from services import register_user, authenticate_user
            
            # Register a user
            success = register_user("testuser", "test@example.com", "password123")
            print(f"User registration: {'SUCCESS' if success else 'FAILED'}")
            
            # Authenticate user
            user = authenticate_user("testuser", "password123")
            print(f"User authentication: {'SUCCESS' if user else 'FAILED'}")
            
            if user:
                print(f"User ID: {user.id}, Username: {user.username}")
                
                # Test 4: Test database persistence
                print("\n4. Testing database persistence...")
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                conn.close()
                print(f"Users in database: {count}")
                
                if count > 0:
                    print("✅ ALL TESTS PASSED!")
                else:
                    print("❌ Database persistence test failed")
            else:
                print("❌ Authentication test failed")
        else:
            print("❌ Database file not created")
            
finally:
    os.chdir(original_cwd)
    shutil.rmtree(test_dir, ignore_errors=True)
    print(f"\nTest completed. Cleaned up: {test_dir}")