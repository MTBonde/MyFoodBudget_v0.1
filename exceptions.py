"""
Custom exceptions for MyFoodBudget application.

This module provides a comprehensive exception hierarchy for consistent error handling
across the application, following the same pattern as the barcode module.
"""

from typing import Optional, Dict, Any


class ApplicationError(Exception):
    """Base exception for all application-specific errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ApplicationError):
    """Raised when user input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.field = field
        self.value = value
        super().__init__(message, details)


class DatabaseError(ApplicationError):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, table: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.operation = operation
        self.table = table
        super().__init__(message, details)


class AuthenticationError(ApplicationError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", username: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.username = username
        super().__init__(message, details)


class AuthorizationError(ApplicationError):
    """Raised when authorization fails (user lacks permission)."""
    
    def __init__(self, message: str = "Access denied", resource: Optional[str] = None, action: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.resource = resource
        self.action = action
        super().__init__(message, details)


class ServiceError(ApplicationError):
    """Raised when service layer operations fail."""
    
    def __init__(self, message: str, service: Optional[str] = None, operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.service = service
        self.operation = operation
        super().__init__(message, details)


class ExternalServiceError(ServiceError):
    """Raised when external API calls fail."""
    
    def __init__(self, message: str, service_name: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        self.service_name = service_name
        self.status_code = status_code
        super().__init__(message, service_name, "external_api_call", details)


class ConfigurationError(ApplicationError):
    """Raised when configuration issues are detected."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.config_key = config_key
        super().__init__(message, details)


class BusinessLogicError(ApplicationError):
    """Raised when business logic constraints are violated."""
    
    def __init__(self, message: str, constraint: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.constraint = constraint
        super().__init__(message, details)


class ResourceNotFoundError(ApplicationError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(message, details)


class DuplicateResourceError(ApplicationError):
    """Raised when attempting to create a resource that already exists."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, identifier: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.resource_type = resource_type
        self.identifier = identifier
        super().__init__(message, details)