"""
Flask error handlers for MyFoodBudget application.

This module provides centralized error handling for all custom exceptions
and standard HTTP errors with proper status codes and user-friendly responses.
"""

from flask import render_template, jsonify, request, session
from werkzeug.exceptions import HTTPException
import traceback

from exceptions import (
    ApplicationError,
    ValidationError,
    DatabaseError,
    AuthenticationError,
    AuthorizationError,
    ServiceError,
    ExternalServiceError,
    ConfigurationError,
    BusinessLogicError,
    ResourceNotFoundError,
    DuplicateResourceError
)
from logging_config import log_error, get_logger


def register_error_handlers(app):
    """
    Register all error handlers with the Flask application.
    
    Args:
        app: Flask application instance
    """
    logger = get_logger(__name__)
    logger.info("Registering error handlers")
    
    # Custom exception handlers
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(DatabaseError, handle_database_error)
    app.register_error_handler(AuthenticationError, handle_authentication_error)
    app.register_error_handler(AuthorizationError, handle_authorization_error)
    app.register_error_handler(ServiceError, handle_service_error)
    app.register_error_handler(ExternalServiceError, handle_external_service_error)
    app.register_error_handler(ConfigurationError, handle_configuration_error)
    app.register_error_handler(BusinessLogicError, handle_business_logic_error)
    app.register_error_handler(ResourceNotFoundError, handle_resource_not_found_error)
    app.register_error_handler(DuplicateResourceError, handle_duplicate_resource_error)
    app.register_error_handler(ApplicationError, handle_application_error)
    
    # Standard HTTP error handlers
    app.register_error_handler(400, handle_bad_request)
    app.register_error_handler(401, handle_unauthorized)
    app.register_error_handler(403, handle_forbidden)
    app.register_error_handler(404, handle_not_found)
    app.register_error_handler(405, handle_method_not_allowed)
    app.register_error_handler(500, handle_internal_server_error)
    
    # Generic exception handler for unhandled exceptions
    app.register_error_handler(Exception, handle_generic_exception)


def is_api_request():
    """Check if the request is an API request (expects JSON response)."""
    return (
        request.is_json or
        request.headers.get('Content-Type', '').startswith('application/json') or
        request.headers.get('Accept', '').startswith('application/json') or
        request.path.startswith('/api/')
    )


def get_error_context():
    """Get common error context for logging and display."""
    return {
        'user_id': session.get('user_id'),
        'url': request.url,
        'method': request.method,
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    }


def handle_validation_error(error):
    """Handle validation errors with user-friendly messages."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Validation Error',
            'message': error.message,
            'field': getattr(error, 'field', None),
            'value': getattr(error, 'value', None),
            'details': error.details
        }), 400
    
    return render_template('errors/validation_error.html', 
                         error=error, 
                         context=get_error_context()), 400


def handle_database_error(error):
    """Handle database errors with appropriate responses."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Database Error',
            'message': 'A database error occurred. Please try again later.',
            'operation': getattr(error, 'operation', None),
            'table': getattr(error, 'table', None)
        }), 500
    
    return render_template('errors/database_error.html', 
                         error=error, 
                         context=get_error_context()), 500


def handle_authentication_error(error):
    """Handle authentication errors with login redirect."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Authentication Error',
            'message': error.message,
            'redirect': '/login'
        }), 401
    
    return render_template('errors/authentication_error.html', 
                         error=error, 
                         context=get_error_context()), 401


def handle_authorization_error(error):
    """Handle authorization errors with access denied message."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Authorization Error',
            'message': error.message,
            'resource': getattr(error, 'resource', None),
            'action': getattr(error, 'action', None)
        }), 403
    
    return render_template('errors/authorization_error.html', 
                         error=error, 
                         context=get_error_context()), 403


def handle_service_error(error):
    """Handle service layer errors with context."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Service Error',
            'message': error.message,
            'service': getattr(error, 'service', None),
            'operation': getattr(error, 'operation', None)
        }), 500
    
    return render_template('errors/service_error.html', 
                         error=error, 
                         context=get_error_context()), 500


def handle_external_service_error(error):
    """Handle external service errors with retry suggestions."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'External Service Error',
            'message': f'Error connecting to {error.service_name}. Please try again later.',
            'service': error.service_name,
            'status_code': error.status_code
        }), 502
    
    return render_template('errors/external_service_error.html', 
                         error=error, 
                         context=get_error_context()), 502


def handle_configuration_error(error):
    """Handle configuration errors (typically for admins)."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Configuration Error',
            'message': 'A configuration error occurred. Please contact support.',
            'config_key': getattr(error, 'config_key', None)
        }), 500
    
    return render_template('errors/configuration_error.html', 
                         error=error, 
                         context=get_error_context()), 500


def handle_business_logic_error(error):
    """Handle business logic constraint violations."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Business Logic Error',
            'message': error.message,
            'constraint': getattr(error, 'constraint', None),
            'details': error.details
        }), 400
    
    return render_template('errors/business_logic_error.html', 
                         error=error, 
                         context=get_error_context()), 400


def handle_resource_not_found_error(error):
    """Handle resource not found errors."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Resource Not Found',
            'message': error.message,
            'resource_type': getattr(error, 'resource_type', None),
            'resource_id': getattr(error, 'resource_id', None)
        }), 404
    
    return render_template('errors/resource_not_found_error.html', 
                         error=error, 
                         context=get_error_context()), 404


def handle_duplicate_resource_error(error):
    """Handle duplicate resource errors."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Duplicate Resource',
            'message': error.message,
            'resource_type': getattr(error, 'resource_type', None),
            'identifier': getattr(error, 'identifier', None)
        }), 409
    
    return render_template('errors/duplicate_resource_error.html', 
                         error=error, 
                         context=get_error_context()), 409


def handle_application_error(error):
    """Handle generic application errors."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Application Error',
            'message': error.message,
            'details': error.details
        }), 500
    
    return render_template('errors/application_error.html', 
                         error=error, 
                         context=get_error_context()), 500


# Standard HTTP error handlers
def handle_bad_request(error):
    """Handle 400 Bad Request errors."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request was invalid. Please check your input.'
        }), 400
    
    return render_template('errors/400.html', 
                         error=error, 
                         context=get_error_context()), 400


def handle_unauthorized(error):
    """Handle 401 Unauthorized errors."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required.',
            'redirect': '/login'
        }), 401
    
    return render_template('errors/401.html', 
                         error=error, 
                         context=get_error_context()), 401


def handle_forbidden(error):
    """Handle 403 Forbidden errors."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access to this resource is forbidden.'
        }), 403
    
    return render_template('errors/403.html', 
                         error=error, 
                         context=get_error_context()), 403


def handle_not_found(error):
    """Handle 404 Not Found errors."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found.'
        }), 404
    
    return render_template('errors/404.html', 
                         error=error, 
                         context=get_error_context()), 404


def handle_method_not_allowed(error):
    """Handle 405 Method Not Allowed errors."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Method Not Allowed',
            'message': f'The {request.method} method is not allowed for this resource.'
        }), 405
    
    return render_template('errors/405.html', 
                         error=error, 
                         context=get_error_context()), 405


def handle_internal_server_error(error):
    """Handle 500 Internal Server Error."""
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An internal server error occurred. Please try again later.'
        }), 500
    
    return render_template('errors/500.html', 
                         error=error, 
                         context=get_error_context()), 500


def handle_generic_exception(error):
    """Handle any unhandled exceptions."""
    logger = get_logger(__name__)
    logger.critical(f"Unhandled exception: {type(error).__name__}: {str(error)}", exc_info=True)
    
    log_error(error, get_error_context())
    
    if is_api_request():
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500
    
    return render_template('errors/500.html', 
                         error=error, 
                         context=get_error_context()), 500