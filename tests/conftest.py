"""
conftest.py: Pytest configuration file

This file defines shared fixtures that are automatically available to all test files
in the same directory and subdirectories.

The filename must be exactly `conftest.py` for pytest to discover it automatically.
Fixtures defined here do not need to be imported manually in test files.
"""

import pytest
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
    from app import app

    # Configure app for test mode with an in-memory SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True

    # Provide application context and initialize the database schema
    with app.app_context():
        # Run the test
        db.create_all()
        yield  
        db.session.remove()
        # Cleanup after test
        db.drop_all()  
