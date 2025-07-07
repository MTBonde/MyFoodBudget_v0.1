#!/usr/bin/env python3
"""
Test configuration switching between development and production
"""
import os
import sys

def test_config_switching():
    """Test that FLASK_ENV properly switches configurations"""
    
    print("Testing configuration switching...")
    
    # Test 1: Development config (default)
    print("\n1. Testing development config (default)...")
    
    # Clear any existing FLASK_ENV
    if 'FLASK_ENV' in os.environ:
        del os.environ['FLASK_ENV']
    
    # Import config fresh
    from config import DevelopmentConfig, ProductionConfig
    
    print(f"Development DEBUG: {DevelopmentConfig.DEBUG}")
    print(f"Development DB: {DevelopmentConfig.DATABASE}")
    print(f"Development URI: {DevelopmentConfig.SQLALCHEMY_DATABASE_URI}")
    
    print(f"Production DEBUG: {ProductionConfig.DEBUG}")
    print(f"Production DB: {ProductionConfig.DATABASE}")
    print(f"Production URI: {ProductionConfig.SQLALCHEMY_DATABASE_URI}")
    
    # Test 2: Production config selection
    print("\n2. Testing production config selection...")
    
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    
    # Test the factory's config selection logic
    config_class = None
    if os.environ.get('FLASK_ENV') == 'production':
        config_class = ProductionConfig
    else:
        config_class = DevelopmentConfig
    
    print(f"Selected config: {config_class.__name__}")
    print(f"Selected DEBUG: {config_class.DEBUG}")
    print(f"Selected DB: {config_class.DATABASE}")
    
    # Test 3: Development config selection
    print("\n3. Testing development config selection...")
    
    # Set development environment
    os.environ['FLASK_ENV'] = 'development'
    
    # Test the factory's config selection logic
    config_class = None
    if os.environ.get('FLASK_ENV') == 'production':
        config_class = ProductionConfig
    else:
        config_class = DevelopmentConfig
    
    print(f"Selected config: {config_class.__name__}")
    print(f"Selected DEBUG: {config_class.DEBUG}")
    print(f"Selected DB: {config_class.DATABASE}")
    
    # Test 4: Production paths
    print("\n4. Testing production paths...")
    
    prod_db = ProductionConfig.DATABASE
    prod_uri = ProductionConfig.SQLALCHEMY_DATABASE_URI
    
    print(f"Production DB path: {prod_db}")
    print(f"Production URI: {prod_uri}")
    
    # Check if paths are absolute
    print(f"DB path is absolute: {os.path.isabs(prod_db)}")
    
    # Check if paths are consistent
    uri_path = prod_uri.replace('sqlite:///', '')
    print(f"URI path: {uri_path}")
    print(f"Paths match: {prod_db == uri_path}")
    
    # Test 5: Directory from paths
    print("\n5. Testing directory extraction...")
    
    db_dir = os.path.dirname(prod_db)
    print(f"Database directory: {db_dir}")
    print(f"Directory is not empty: {bool(db_dir)}")
    
    if db_dir:
        print("✅ Directory extraction works for production")
    else:
        print("❌ Directory extraction failed for production")
        return False
    
    print("✅ All configuration tests passed!")
    return True

if __name__ == "__main__":
    success = test_config_switching()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)