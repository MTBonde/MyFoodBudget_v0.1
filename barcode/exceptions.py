"""
Custom exceptions for barcode operations.
"""


class BarcodeError(Exception):
    """Base exception for barcode-related errors."""
    pass


class ProductNotFoundError(BarcodeError):
    """Raised when a product is not found in any data source."""
    pass


class ReaderError(BarcodeError):
    """Raised when a reader encounters an error."""
    def __init__(self, reader_name: str, message: str):
        self.reader_name = reader_name
        super().__init__(f"Error in {reader_name}: {message}")


class InvalidBarcodeError(BarcodeError):
    """Raised when a barcode format is invalid."""
    pass


class NetworkError(ReaderError):
    """Raised when a network-related error occurs."""
    pass


class APIRateLimitError(ReaderError):
    """Raised when API rate limit is exceeded."""
    pass