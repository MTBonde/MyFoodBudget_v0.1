"""
Unit tests for user authentication.

Structure follows the AAA pattern: Arrange – Act – Assert
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services import register_user, authenticate_user
from exceptions import ValidationError, DuplicateResourceError, AuthenticationError, DatabaseError


def test_register_user_success(app_context):
    """
    ARRANGE: Valid registration.
    ACT: Call register_user.
    ASSERT: Should succeed.
    """
    # Arrange
    username = "testuser"
    email = "test@example.com"
    password = "password123"

    # Act
    result = register_user(username, email, password)

    # Assert
    assert result is not None
    assert result.username == username
    assert result.email == email


def test_register_user_duplicate_username(app_context):
    """
    ARRANGE: Register user.
    ACT: Register with same username.
    ASSERT: Should fail.
    """
    # Arrange
    username = "duplicateuser"
    email1 = "user1@example.com"
    email2 = "user2@example.com"
    password1 = "password1"
    password2 = "password2"
    register_user(username, email1, password1)

    # Act & Assert
    with pytest.raises(DuplicateResourceError):
        register_user(username, email2, password2)


def test_register_user_duplicate_email(app_context):
    """
    ARRANGE: Register user.
    ACT: Register with same email.
    ASSERT: Should fail.
    """
    # Arrange
    username1 = "user1"
    username2 = "user2"
    shared_email = "shared@example.com"
    password1 = "password1"
    password2 = "password2"
    register_user(username1, shared_email, password1)

    # Act & Assert
    with pytest.raises(DatabaseError):
        register_user(username2, shared_email, password2)


def test_authenticate_user_success(app_context):
    """
    ARRANGE: Register user.
    ACT: Authenticate with correct credentials.
    ASSERT: Should return user.
    """
    # Arrange
    username = "validuser"
    email = "valid@example.com"
    password = "mypassword"
    register_user(username, email, password)

    # Act
    user = authenticate_user(username, password)

    # Assert
    assert user is not None
    assert user.username == username


def test_authenticate_user_wrong_password(app_context):
    """
    ARRANGE: Register user.
    ACT: Authenticate with wrong password.
    ASSERT: Should return None.
    """
    # Arrange
    username = "userA"
    email = "a@example.com"
    correct_password = "correctpass"
    wrong_password = "wrongpass"
    register_user(username, email, correct_password)

    # Act & Assert
    with pytest.raises(AuthenticationError):
        authenticate_user(username, wrong_password)


def test_authenticate_user_nonexistent(app_context):
    """
    ARRANGE: Use nonexistent user.
    ACT: Try to authenticate.
    ASSERT: Should return None.
    """
    # Arrange
    username = "ghost"
    password = "any"

    # Act & Assert
    with pytest.raises(AuthenticationError):
        authenticate_user(username, password)


def test_authenticate_user_empty_username(app_context):
    """
    ARRANGE: Empty username.
    ACT: Try to authenticate with empty username.
    ASSERT: Should return None.
    """
    # Arrange
    username_empty = ""
    password = "something"

    # Act & Assert
    with pytest.raises(ValidationError):
        authenticate_user(username_empty, password)


def test_authenticate_user_empty_password(app_context):
    """
    ARRANGE: Empty password.
    ACT: Try to authenticate with empty password.
    ASSERT: Should return None.
    """
    # Arrange
    username = "someone"
    password_empty = ""

    # Act & Assert
    with pytest.raises(ValidationError):
        authenticate_user(username, password_empty)
