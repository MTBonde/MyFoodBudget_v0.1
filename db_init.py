#!/usr/bin/env python3
"""
Database initialization script with environment detection.
Maintains backward compatibility for tests while avoiding circular imports.
"""
import os
from config import DevelopmentConfig, ProductionConfig, TestingConfig

# Environment detection for test compatibility
env = os.getenv("FLASK_ENV", "development")

if env == "development":
    config = DevelopmentConfig()
elif env == "testing":
    config = TestingConfig()
else:
    config = ProductionConfig()

DATABASE_URL = config.DATABASE

def initialize_database_standalone():
    """
    Initialize database using SQLAlchemy models via app factory.
    This function avoids circular imports by importing only when called.
    """
    from app_factory import create_app
    
    app = create_app()
    try:
        with app.app_context():
            from app_factory import initialize_database
            initialize_database()
    finally:
        # Ensure app and all its resources are properly cleaned up
        try:
            from extensions import db
            if hasattr(db, 'engine'):
                db.engine.dispose()
        except:
            pass

if __name__ == "__main__":
    initialize_database_standalone()
