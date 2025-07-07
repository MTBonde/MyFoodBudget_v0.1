#!/usr/bin/env python3
"""
Test the improved db_init configuration handling
"""
import os
import sys
import tempfile
import shutil

def test_improved_config():
    """Test that db_init properly selects config based on FLASK_ENV"""
    
    print("Testing improved db_init configuration handling...")
    
    # Test 1: Development environment (default)
    print("\n1. Testing development environment (default)...")
    
    # Clear FLASK_ENV
    if 'FLASK_ENV' in os.environ:
        del os.environ['FLASK_ENV']
    
    # Reload db_init to pick up environment change
    import importlib
    if 'db_init' in sys.modules:
        importlib.reload(sys.modules['db_init'])
    
    import db_init
    
    print(f"DATABASE_URL: {db_init.DATABASE_URL}")
    print(f"Environment: {db_init.env}")
    print(f"Config class: {db_init.config.__class__.__name__}")
    
    # Should use development config
    assert "MyFoodBudget" in db_init.DATABASE_URL, "Should use development path"
    assert db_init.env == "development", "Should detect development environment"
    
    # Test 2: Production environment
    print("\n2. Testing production environment...")
    
    os.environ['FLASK_ENV'] = 'production'
    importlib.reload(db_init)
    
    print(f"DATABASE_URL: {db_init.DATABASE_URL}")
    print(f"Environment: {db_init.env}")
    print(f"Config class: {db_init.config.__class__.__name__}")
    
    # Should use production config
    assert "/app/data" in db_init.DATABASE_URL, "Should use production path"
    assert db_init.env == "production", "Should detect production environment"
    
    # Test 3: Testing environment
    print("\n3. Testing testing environment...")
    
    os.environ['FLASK_ENV'] = 'testing'
    importlib.reload(db_init)
    
    print(f"DATABASE_URL: {db_init.DATABASE_URL}")
    print(f"Environment: {db_init.env}")
    print(f"Config class: {db_init.config.__class__.__name__}")
    
    # Should use testing config
    assert ":memory:" in db_init.DATABASE_URL, "Should use in-memory database"
    assert db_init.env == "testing", "Should detect testing environment"
    
    # Test 4: Unknown environment (should default to production)
    print("\n4. Testing unknown environment (should default to production)...")
    
    os.environ['FLASK_ENV'] = 'unknown'
    importlib.reload(db_init)
    
    print(f"DATABASE_URL: {db_init.DATABASE_URL}")
    print(f"Environment: {db_init.env}")
    print(f"Config class: {db_init.config.__class__.__name__}")
    
    # Should use production config as fallback
    assert "/app/data" in db_init.DATABASE_URL, "Should default to production path"
    assert db_init.env == "unknown", "Should detect unknown environment"
    
    # Test 5: Database initialization with production config
    print("\n5. Testing database initialization with production config...")
    
    # Set back to production
    os.environ['FLASK_ENV'] = 'production'
    importlib.reload(db_init)
    
    # Create temporary directory for test
    test_dir = tempfile.mkdtemp(prefix='db_init_test_')
    
    try:
        # Temporarily override the database path for testing
        original_db_url = db_init.DATABASE_URL
        test_db_path = os.path.join(test_dir, 'data', 'myfoodbudget.db')
        db_init.DATABASE_URL = test_db_path
        
        print(f"Testing with path: {test_db_path}")
        
        # This should create the directory and database
        db_init.initialize_database()
        
        # Check results
        print(f"Database file exists: {os.path.exists(test_db_path)}")
        print(f"Database directory exists: {os.path.exists(os.path.dirname(test_db_path))}")
        
        if os.path.exists(test_db_path):
            print(f"Database file size: {os.path.getsize(test_db_path)} bytes")
        
        # Restore original
        db_init.DATABASE_URL = original_db_url
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)
    
    print("✅ All improved configuration tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_improved_config()
        print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up environment
        if 'FLASK_ENV' in os.environ:
            del os.environ['FLASK_ENV']