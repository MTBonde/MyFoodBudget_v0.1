"""
conftest.py: Pytest configuration file

This file defines shared fixtures that are automatically available to all test files
in the same directory and subdirectories.

The filename must be exactly `conftest.py` for pytest to discover it automatically.
Fixtures defined here do not need to be imported manually in test files.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import db

@pytest.fixture(scope="function")
def app_context():
    """
    <summary>
    Provides a clean in-memory database for each test case.

    This fixture sets up an isolated SQLite in-memory database context before each test.
    It ensures test isolation by resetting the database state after each test run.
    All models are re-created using SQLAlchemy's metadata.
    </summary>
    """
    from app_factory import create_app
    from config import TestingConfig

    # Create app with testing configuration
    app = create_app(TestingConfig)

    # Provide application context and initialize the database schema
    with app.app_context():
        # Run the test
        db.create_all()
        yield  
        db.session.remove()
        # Cleanup after test
        db.drop_all()  
