"""
Barcode validation utilities.
"""

import re
from typing import Optional
from .exceptions import InvalidBarcodeError


def validate_ean13(barcode: str) -> bool:
    """
    Validate EAN-13 barcode format and check digit.
    
    Args:
        barcode: The barcode string to validate
        
    Returns:
        True if valid EAN-13 barcode
        
    Raises:
        InvalidBarcodeError: If barcode format is invalid
    """
    if not barcode or not isinstance(barcode, str):
        return False
        
    # Remove any non-numeric characters
    clean_barcode = re.sub(r'[^0-9]', '', barcode)
    
    # EAN-13 must be exactly 13 digits
    if len(clean_barcode) != 13:
        return False
    
    # Calculate check digit according to EAN-13 standard
    # Multiply every second digit by 3, starting from the right (excluding check digit)
    total = 0
    for i in range(12):
        digit = int(clean_barcode[i])
        if i % 2 == 0:  # Positions 1, 3, 5, 7, 9, 11 (0-indexed)
            total += digit
        else:  # Positions 2, 4, 6, 8, 10, 12 (0-indexed)
            total += digit * 3
    
    check_digit = (10 - (total % 10)) % 10
    
    return check_digit == int(clean_barcode[12])


def validate_ean8(barcode: str) -> bool:
    """
    Validate EAN-8 barcode format and check digit.
    
    Args:
        barcode: The barcode string to validate
        
    Returns:
        True if valid EAN-8 barcode
    """
    if not barcode or not isinstance(barcode, str):
        return False
        
    # Remove any non-numeric characters
    clean_barcode = re.sub(r'[^0-9]', '', barcode)
    
    # EAN-8 must be exactly 8 digits
    if len(clean_barcode) != 8:
        return False
    
    # Calculate check digit
    odd_sum = sum(int(clean_barcode[i]) for i in range(0, 7, 2))
    even_sum = sum(int(clean_barcode[i]) for i in range(1, 7, 2))
    
    total = (odd_sum * 3) + even_sum
    check_digit = (10 - (total % 10)) % 10
    
    return check_digit == int(clean_barcode[7])


def get_country_code(barcode: str) -> Optional[str]:
    """
    Extract country code from EAN barcode.
    
    Args:
        barcode: The barcode string
        
    Returns:
        Country code (first 2-3 digits) or None if invalid
    """
    if not barcode or not isinstance(barcode, str):
        return None
        
    clean_barcode = re.sub(r'[^0-9]', '', barcode)
    
    if len(clean_barcode) >= 13:
        # For EAN-13, return first 3 digits for extended country codes
        return clean_barcode[:3]
    elif len(clean_barcode) >= 8:
        # For EAN-8, return first 2 digits
        return clean_barcode[:2]
    
    return None


def is_danish_barcode(barcode: str) -> bool:
    """
    Check if barcode is from a Danish product.
    Denmark uses GS1 country code 570-579.
    
    Args:
        barcode: The barcode string
        
    Returns:
        True if barcode appears to be Danish
    """
    country_code = get_country_code(barcode)
    if not country_code:
        return False
    
    # Denmark uses codes 570-579
    if len(country_code) >= 3:
        return country_code.startswith('57')
    elif len(country_code) >= 2:
        return country_code == '57'
    
    return False


def validate_barcode(barcode: str) -> bool:
    """
    Validate barcode format (EAN-8 or EAN-13).
    
    Args:
        barcode: The barcode string to validate
        
    Returns:
        True if valid barcode
        
    Raises:
        InvalidBarcodeError: If barcode format is invalid
    """
    if not barcode:
        raise InvalidBarcodeError("Barcode cannot be empty")
    
    clean_barcode = re.sub(r'[^0-9]', '', barcode)
    
    if len(clean_barcode) == 13:
        if not validate_ean13(clean_barcode):
            raise InvalidBarcodeError(f"Invalid EAN-13 barcode: {barcode}")
        return True
    elif len(clean_barcode) == 8:
        if not validate_ean8(clean_barcode):
            raise InvalidBarcodeError(f"Invalid EAN-8 barcode: {barcode}")
        return True
    else:
        raise InvalidBarcodeError(f"Barcode must be 8 or 13 digits, got {len(clean_barcode)}: {barcode}")


def normalize_barcode(barcode: str) -> str:
    """
    Normalize barcode by removing non-numeric characters.
    
    Args:
        barcode: The barcode string
        
    Returns:
        Normalized barcode string
    """
    if not barcode:
        return ""
    
    return re.sub(r'[^0-9]', '', barcode)