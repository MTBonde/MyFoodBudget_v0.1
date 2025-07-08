"""
Barcode module for MyFoodBudget application.

This module provides a clean, SOLID-principle-based architecture for barcode scanning
and product lookup functionality. It supports multiple data sources and follows
the strategy pattern for extensibility.
"""

from .scanner import BarcodeScanner
from .exceptions import BarcodeError, ProductNotFoundError, ReaderError

__all__ = ['BarcodeScanner', 'BarcodeError', 'ProductNotFoundError', 'ReaderError']