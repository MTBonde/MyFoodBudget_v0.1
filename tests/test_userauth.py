"""
Unit tests for user authentication services in MyFoodBudget.
These tests cover both successful and failing scenarios for user registration and login.

Follows AAA pattern: Arrange, Act, Assert
"""

import pytest
from services import register_user, authenticate_user


def test_register_user_success(app_context):
    """
    ARRANGE: Prepare valid user data.
    ACT: Register the user.
    ASSERT: Check that the operation was successful.
    """
    # Arrange
    username = "testuser"
    email = "test@example.com"
    password = "password123"

    # Act
    success = register_user(username, email, password)

    # Assert
    assert success is True


def test_register_user_duplicate_username(app_context):
    """
    ARRANGE: Register a user with a given username.
    ACT: Attempt to register a second user with the same username.
    ASSERT: The second registration should fail.
    """
    # Arrange
    register_user("duplicateuser", "one@example.com", "pass1")

    # Act
    second = register_user("duplicateuser", "two@example.com", "pass2")

    # Assert
    assert second is False


def test_register_user_duplicate_email(app_context):
    """
    ARRANGE: Register a user with a given email.
    ACT: Attempt to register a second user with the same email.
    ASSERT: The second registration should fail.
    """
    # Arrange
    register_user("userone", "dup@example.com", "pass1")

    # Act
    second = register_user("usertwo", "dup@example.com", "pass2")

    # Assert
    assert second is False


def test_authenticate_user_success(app_context):
    """
    ARRANGE: Register a user with known credentials.
    ACT: Authenticate using the same credentials.
    ASSERT: Authentication should return a valid user.
    """
    # Arrange
    username = "authuser"
    email = "auth@example.com"
    password = "securepass"
    register_user(username, email, password)

    # Act
    user = authenticate_user(username, password)

    # Assert
    assert user is not None
    assert user.username == username


def test_authenticate_user_wrong_password(app_context):
    """
    ARRANGE: Register a user with a valid password.
    ACT: Attempt authentication with the wrong password.
    ASSERT: Authentication should fail.
    """
    # Arrange
    register_user("userA", "a@example.com", "correctpass")

    # Act
    user = authenticate_user("userA", "wrongpass")

    # Assert
    assert user is None


def test_authenticate_user_nonexistent_user(app_context):
    """
    ARRANGE: Prepare a username that does not exist.
    ACT: Try authenticating with that username.
    ASSERT: Authentication should return None.
    """
    # Act
    user = authenticate_user("ghost", "any")

    # Assert
    assert user is None


def test_authenticate_user_empty_inputs(app_context):
    """
    ARRANGE: Prepare invalid input cases (empty fields).
    ACT: Try authenticating with missing credentials.
    ASSERT: Authentication should fail gracefully.
    """
    # Act & Assert
    assert authenticate_user("", "something") is None
    assert authenticate_user("someone", "") is None
