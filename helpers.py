import csv
import datetime
import pytz
import requests
import urllib
import uuid
import pint

from flask import redirect, render_template, request, session
from functools import wraps
from exceptions import AuthenticationError, ValidationError
from logging_config import get_logger

ureg = pint.UnitRegistry()
logger = get_logger('helpers')

def apology(message, code=400):
    """
    Legacy apology function - DEPRECATED.
    
    Use proper exceptions instead:
    - raise ValidationError(message) for validation errors
    - raise AuthenticationError(message) for auth errors
    - etc.
    
    This function is maintained for backward compatibility only.
    """
    logger.warning(f"DEPRECATED: apology() function used with message: {message}")
    
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def validate_required_fields(form_data, required_fields):
    """
    Validate that all required fields are present and not empty.
    
    Args:
        form_data (dict): Form data to validate
        required_fields (list): List of required field names
        
    Raises:
        ValidationError: If any required field is missing or empty
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in form_data or not form_data[field] or form_data[field].strip() == "":
            missing_fields.append(field)
    
    if missing_fields:
        if len(missing_fields) == 1:
            raise ValidationError(f"The {missing_fields[0]} field is required", field=missing_fields[0])
        else:
            raise ValidationError(f"The following fields are required: {', '.join(missing_fields)}")


def validate_numeric_field(value, field_name, min_value=None, max_value=None):
    """
    Validate that a field is a valid number within specified bounds.
    
    Args:
        value: Value to validate
        field_name (str): Name of the field for error messages
        min_value (float, optional): Minimum allowed value
        max_value (float, optional): Maximum allowed value
        
    Returns:
        float: The validated numeric value
        
    Raises:
        ValidationError: If value is not a valid number or outside bounds
    """
    try:
        numeric_value = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid number", field=field_name, value=str(value))
    
    if min_value is not None and numeric_value < min_value:
        raise ValidationError(f"{field_name} must be at least {min_value}", field=field_name, value=str(value))
    
    if max_value is not None and numeric_value > max_value:
        raise ValidationError(f"{field_name} must be at most {max_value}", field=field_name, value=str(value))
    
    return numeric_value


def validate_string_length(value, field_name, min_length=None, max_length=None):
    """
    Validate that a string field meets length requirements.
    
    Args:
        value (str): Value to validate
        field_name (str): Name of the field for error messages
        min_length (int, optional): Minimum required length
        max_length (int, optional): Maximum allowed length
        
    Returns:
        str: The validated string value
        
    Raises:
        ValidationError: If string doesn't meet length requirements
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string", field=field_name)
    
    if min_length is not None and len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters long", field=field_name)
    
    if max_length is not None and len(value) > max_length:
        raise ValidationError(f"{field_name} must be at most {max_length} characters long", field=field_name)
    
    return value


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            logger.info(f"Unauthorized access attempt to {request.endpoint}")
            raise AuthenticationError("Please log in to access this page")
        return f(*args, **kwargs)

    return decorated_function


def convert_to_standard_unit(quantity, unit):
    try:
        measurement = quantity * ureg(unit)
        standard_measurement = measurement.to_base_units()
        return standard_measurement.magnitude, str(standard_measurement.units)
    except ValueError:
        return None

def format_quantity(quantity, unit):
    measurement = quantity * ureg(unit)
    return measurement.magnitude, str(measurement.units)
