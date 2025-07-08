"""
Centralized logging configuration for MyFoodBudget application.

This module provides structured logging configuration with different levels
and formatters for development and production environments.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Dict, Any

import pytz
from flask import request, session, g
from werkzeug.local import LocalProxy


class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request context in log messages."""
    
    def format(self, record):
        # Add request context if available
        if request:
            record.method = request.method
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.user_agent = request.headers.get('User-Agent', 'Unknown')
            record.user_id = session.get('user_id', 'Anonymous')
            record.request_id = getattr(g, 'request_id', 'N/A')
        else:
            record.method = 'N/A'
            record.url = 'N/A'
            record.remote_addr = 'N/A'
            record.user_agent = 'N/A'
            record.user_id = 'N/A'
            record.request_id = 'N/A'
        
        # Add timestamp in a consistent format
        record.timestamp = datetime.now(pytz.UTC).isoformat()
        
        return super().format(record)


class ErrorContextFilter(logging.Filter):
    """Filter that adds error context to log records."""
    
    def filter(self, record):
        # Add error context for ERROR and CRITICAL levels
        if record.levelno >= logging.ERROR:
            # Add stack trace if available
            if hasattr(record, 'exc_info') and record.exc_info:
                record.stack_trace = self.format_exception(record.exc_info)
            else:
                record.stack_trace = 'N/A'
        
        return True
    
    def format_exception(self, exc_info):
        """Format exception information for logging."""
        import traceback
        return ''.join(traceback.format_exception(*exc_info))


def setup_logging(app_config: Dict[str, Any]) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        app_config: Flask application configuration dictionary
    """
    # Determine logging level based on environment
    debug_mode = app_config.get('DEBUG', False)
    log_level = logging.DEBUG if debug_mode else logging.INFO
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    if debug_mode:
        # Development formatter - more readable
        formatter = RequestFormatter(
            fmt='%(timestamp)s - %(name)s - %(levelname)s - [%(request_id)s] '
                '%(method)s %(url)s - User: %(user_id)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Production formatter - structured JSON-like format
        formatter = RequestFormatter(
            fmt='%(timestamp)s|%(levelname)s|%(name)s|%(request_id)s|%(method)s|%(url)s|'
                '%(user_id)s|%(remote_addr)s|%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(ErrorContextFilter())
    root_logger.addHandler(console_handler)
    
    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(logs_dir, 'myfoodbudget.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(ErrorContextFilter())
    root_logger.addHandler(file_handler)
    
    # Error file handler - only for errors and critical messages
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(logs_dir, 'errors.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(ErrorContextFilter())
    root_logger.addHandler(error_handler)
    
    # Configure specific loggers
    configure_application_loggers(log_level)
    
    # Log configuration completion
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {logging.getLevelName(log_level)}, Debug: {debug_mode}")


def configure_application_loggers(log_level: int) -> None:
    """Configure specific loggers for different parts of the application."""
    
    # Application loggers
    app_loggers = [
        'myfoodbudget.routes',
        'myfoodbudget.services',
        'myfoodbudget.repositories',
        'myfoodbudget.auth',
        'myfoodbudget.barcode',
        'myfoodbudget.errors'
    ]
    
    for logger_name in app_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.propagate = True  # Allow propagation to root logger
    
    # Set external libraries to WARNING level to reduce noise
    external_loggers = [
        'werkzeug',
        'urllib3',
        'requests',
        'flask',
        'sqlalchemy'
    ]
    
    for logger_name in external_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f'myfoodbudget.{name}')


def log_request_start():
    """Log the start of a request with basic information."""
    logger = get_logger('requests')
    logger.info(f"Request started - {request.method} {request.path}")


def log_request_end(response):
    """Log the end of a request with response information."""
    logger = get_logger('requests')
    duration = getattr(g, 'request_duration', 'N/A')
    logger.info(f"Request completed - Status: {response.status_code}, Duration: {duration}ms")
    return response


def log_error(error: Exception, context: Dict[str, Any] = None):
    """
    Log an error with full context information.
    
    Args:
        error: The exception that occurred
        context: Additional context information
    """
    logger = get_logger('errors')
    
    context = context or {}
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context
    }
    
    # Add custom exception details if available
    if hasattr(error, 'details'):
        error_info['error_details'] = error.details
    
    logger.error(f"Error occurred: {error_info}", exc_info=True)


def log_performance(operation: str, duration: float, details: Dict[str, Any] = None):
    """
    Log performance metrics for operations.
    
    Args:
        operation: Name of the operation
        duration: Duration in milliseconds
        details: Additional performance details
    """
    logger = get_logger('performance')
    
    details = details or {}
    logger.info(f"Performance: {operation} - Duration: {duration}ms - Details: {details}")


def log_security_event(event_type: str, details: Dict[str, Any] = None):
    """
    Log security-related events.
    
    Args:
        event_type: Type of security event
        details: Event details
    """
    logger = get_logger('security')
    
    details = details or {}
    logger.warning(f"Security event: {event_type} - Details: {details}")


def log_business_event(event_type: str, details: Dict[str, Any] = None):
    """
    Log business logic events.
    
    Args:
        event_type: Type of business event
        details: Event details
    """
    logger = get_logger('business')
    
    details = details or {}
    logger.info(f"Business event: {event_type} - Details: {details}")