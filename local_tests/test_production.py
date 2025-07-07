#!/usr/bin/env python3
"""
Test script to simulate production environment locally
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path

def test_production_setup():
    """Test the production configuration locally"""
    
    # Create a temporary directory to simulate /app/data
    test_dir = tempfile.mkdtemp(prefix='mfb_test_')
    data_dir = os.path.join(test_dir, 'data')
    
    print(f"Testing production setup in: {test_dir}")
    
    # Set environment variables to simulate production
    os.environ['FLASK_ENV'] = 'production'
    
    # Temporarily modify the production config to use our test directory
    original_cwd = os.getcwd()
    
    try:
        # Create a temporary config that uses our test directory
        from config import ProductionConfig
        
        # Override the database paths for testing
        ProductionConfig.DATABASE = os.path.join(data_dir, 'myfoodbudget.db')
        ProductionConfig.SQLALCHEMY_DATABASE_URI = f"sqlite:///{ProductionConfig.DATABASE}"
        
        print(f"Test database path: {ProductionConfig.DATABASE}")
        
        # Test database initialization
        print("\n1. Testing database initialization...")
        
        # We need to reload the db_init module to pick up the new config
        import importlib
        import db_init
        importlib.reload(db_init)
        
        db_init.initialize_database()
        
        # Check if database file was created
        db_path = ProductionConfig.DATABASE
        if os.path.exists(db_path):
            print(f"✓ Database file created successfully at: {db_path}")
            print(f"✓ Database file size: {os.path.getsize(db_path)} bytes")
        else:
            print(f"✗ Database file not found at: {db_path}")
            return False
        
        # Test app creation with production config
        print("\n2. Testing app creation with production config...")
        from app_factory import create_app
        app = create_app()
        
        if app.config['DEBUG'] == False:
            print("✓ App created in production mode (DEBUG=False)")
        else:
            print("✗ App not in production mode")
            return False
        
        # Test basic database operations
        print("\n3. Testing database operations...")
        with app.app_context():
            from services import register_user, authenticate_user
            
            # Test user registration
            success = register_user("testuser", "test@example.com", "testpass123")
            if success:
                print("✓ User registration successful")
            else:
                print("✗ User registration failed")
                return False
            
            # Test user authentication
            user = authenticate_user("testuser", "testpass123")
            if user:
                print(f"✓ User authentication successful - User ID: {user.id}")
            else:
                print("✗ User authentication failed")
                return False
        
        print("\n4. Testing database persistence...")
        # Check if we can connect to the database again
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        conn.close()
        
        if user_count >= 1:
            print(f"✓ Database persistent - Found {user_count} users")
        else:
            print("✗ Database not persistent")
            return False
        
        print("\n✅ All tests passed! Production setup is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        os.environ.pop('FLASK_ENV', None)
        print(f"\nCleaning up test directory: {test_dir}")
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    success = test_production_setup()
    sys.exit(0 if success else 1)