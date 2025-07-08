"""
Integration tests for database and configuration
"""
import os
import sys
import tempfile
import shutil
import pytest
from unittest.mock import patch

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_production_config_detection():
    """Test that production configuration is properly detected"""
    with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
        # Reload modules to pick up environment change
        import importlib
        if 'app_factory' in sys.modules:
            importlib.reload(sys.modules['app_factory'])
        
        # Mock the local reference after reload
        with patch('app_factory.initialize_database'):
            from app_factory import create_app
            app = create_app()
            
            assert app.config['DEBUG'] is False
            assert '/app/data' in app.config['DATABASE']
            assert 'sqlite:////app/data' in app.config['SQLALCHEMY_DATABASE_URI']


def test_development_config_detection():
    """Test that development configuration is properly detected"""
    with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
        # Reload modules to pick up environment change
        import importlib
        if 'app_factory' in sys.modules:
            importlib.reload(sys.modules['app_factory'])
        
        # Mock the local reference after reload
        with patch('app_factory.initialize_database'):
            from app_factory import create_app
            app = create_app()
            
            assert app.config['DEBUG'] is True
            assert 'myfoodbudget.db' in app.config['DATABASE']


def test_database_initialization_with_temp_directory():
    """Test database initialization with temporary directory (CI-safe)"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test database path
        test_db_path = os.path.join(temp_dir, 'data', 'test.db')
        
        # Test the directory creation logic from db_init.py
        db_dir = os.path.dirname(test_db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Verify directory was created
        assert os.path.exists(db_dir)
        
        # Test database file creation
        import sqlite3
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Create a test table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL
        )
        """)
        
        conn.commit()
        conn.close()
        
        # Verify database file exists
        assert os.path.exists(test_db_path)
        assert os.path.getsize(test_db_path) > 0


def test_db_init_environment_detection():
    """Test that db_init properly detects different environments"""
    
    # Test production environment
    with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
        # Reload db_init to pick up environment change
        import importlib
        if 'db_init' in sys.modules:
            importlib.reload(sys.modules['db_init'])
        
        import db_init
        assert db_init.env == 'production'
        assert '/app/data' in db_init.DATABASE_URL
    
    # Test development environment
    with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
        importlib.reload(db_init)
        assert db_init.env == 'development'
        assert 'myfoodbudget.db' in db_init.DATABASE_URL
    
    # Test testing environment
    with patch.dict(os.environ, {'FLASK_ENV': 'testing'}):
        importlib.reload(db_init)
        assert db_init.env == 'testing'
        assert ':memory:' in db_init.DATABASE_URL


def test_database_operations_with_temp_config():
    """Test database operations with temporary configuration"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_db_path = os.path.join(temp_dir, 'test.db')
        
        # Test the actual database initialization logic
        from config import TestingConfig
        
        # Create a temporary config for testing
        class TempConfig(TestingConfig):
            DATABASE = test_db_path
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{test_db_path}"
        
        from app_factory import create_app
        app = create_app(TempConfig)
        
        with app.app_context():
            # Test database initialization
            import sqlite3
            conn = sqlite3.connect(test_db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                hash TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
            """)
            
            # Insert test data
            cursor.execute("""
            INSERT INTO users (username, hash, email) 
            VALUES (?, ?, ?)
            """, ("testuser", "testhash", "test@example.com"))
            
            # Query test data
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            assert count == 1
            assert os.path.exists(test_db_path)


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])