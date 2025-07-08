"""
Main barcode scanner orchestrator.

This module provides the main BarcodeScanner class that coordinates multiple
barcode readers using the strategy pattern.
"""

import logging
from typing import Optional, Dict, Any, List
from .exceptions import ProductNotFoundError, ReaderError
from .validators import validate_barcode, is_danish_barcode
from .readers import OpenFoodFactsReader, NutriFinderReader


class BarcodeScanner:
    """
    Main scanner class that orchestrates multiple barcode readers.
    
    Uses strategy pattern to try multiple data sources in priority order,
    with fallback mechanisms and error handling.
    """
    
    def __init__(self, readers: Optional[List] = None):
        """
        Initialize the barcode scanner with readers.
        
        Args:
            readers: List of reader instances (optional, uses defaults if None)
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize default readers if none provided
        if readers is None:
            self.readers = [
                OpenFoodFactsReader(),
                NutriFinderReader()
            ]
        else:
            self.readers = readers
        
        # Sort readers by priority (lower number = higher priority)
        self.readers.sort(key=lambda r: r.get_priority())
        
        self.logger.info(f"Initialized BarcodeScanner with {len(self.readers)} readers")
    
    def lookup_product(self, barcode: str = None, name: str = None) -> Optional[Dict[str, Any]]:
        """
        Look up product information using available readers.
        
        Args:
            barcode: Product barcode (optional)
            name: Product name (optional)
            
        Returns:
            Product information dictionary or None if not found
            
        Raises:
            ProductNotFoundError: If no reader can find the product
        """
        if not barcode and not name:
            raise ValueError("Either barcode or name must be provided")
        
        # If barcode is provided, prioritize readers that support barcode lookup
        if barcode:
            try:
                validate_barcode(barcode)
                is_danish = is_danish_barcode(barcode)
                self.logger.info(f"Looking up barcode {barcode} (Danish: {is_danish})")
                
                return self._lookup_by_barcode(barcode)
            except Exception as e:
                self.logger.warning(f"Barcode lookup failed: {e}")
                # Fall through to name-based lookup if barcode fails
        
        # Try name-based lookup as fallback or primary method
        if name:
            self.logger.info(f"Looking up by name: {name}")
            return self._lookup_by_name(name)
        
        return None
    
    def get_nutrition_data(self, barcode: str = None, name: str = None) -> Optional[Dict[str, Any]]:
        """
        Get nutrition data for a product.
        
        Args:
            barcode: Product barcode (optional)
            name: Product name (optional)
            
        Returns:
            Nutrition information dictionary or None if not found
        """
        # First try to get product information
        product_info = self.lookup_product(barcode=barcode, name=name)
        
        if not product_info:
            return None
        
        # Extract nutrition from product info
        for reader in self.readers:
            if hasattr(reader, 'get_nutrition') and reader.supports_product(product_info):
                try:
                    nutrition = reader.get_nutrition(product_info)
                    if nutrition:
                        self.logger.info(f"Successfully got nutrition from {reader.name}")
                        return nutrition
                except Exception as e:
                    self.logger.warning(f"Error getting nutrition from {reader.name}: {e}")
                    continue
        
        self.logger.info("No nutrition data found from any reader")
        return None
    
    def lookup_product_with_nutrition(self, barcode: str = None, name: str = None) -> Optional[Dict[str, Any]]:
        """
        Look up product information with nutrition data included.
        
        Args:
            barcode: Product barcode (optional)
            name: Product name (optional)
            
        Returns:
            Combined product and nutrition information or None
        """
        product_info = self.lookup_product(barcode=barcode, name=name)
        
        if not product_info:
            return None
        
        # Add nutrition information if available
        nutrition = self.get_nutrition_data(barcode=barcode, name=name)
        if nutrition:
            product_info['nutrition'] = nutrition
        
        return product_info
    
    def _lookup_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Look up product by barcode using available readers.
        
        Args:
            barcode: The product barcode
            
        Returns:
            Product information or None
        """
        for reader in self.readers:
            if not hasattr(reader, 'lookup_by_barcode'):
                continue
                
            try:
                if not reader.is_available():
                    self.logger.warning(f"Reader {reader.name} is not available")
                    continue
                
                self.logger.debug(f"Trying barcode lookup with {reader.name}")
                result = reader.lookup_by_barcode(barcode)
                
                if result:
                    self.logger.info(f"Found product with {reader.name}")
                    return result
                    
            except ReaderError as e:
                self.logger.warning(f"Reader error in {reader.name}: {e}")
                continue
            except Exception as e:
                self.logger.error(f"Unexpected error in {reader.name}: {e}")
                continue
        
        self.logger.info(f"No product found for barcode {barcode}")
        return None
    
    def _lookup_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Look up product by name using available readers.
        
        Args:
            name: The product name
            
        Returns:
            Product information or None
        """
        for reader in self.readers:
            if not hasattr(reader, 'lookup_by_name'):
                continue
                
            try:
                if not reader.is_available():
                    self.logger.warning(f"Reader {reader.name} is not available")
                    continue
                
                self.logger.debug(f"Trying name lookup with {reader.name}")
                result = reader.lookup_by_name(name)
                
                if result:
                    self.logger.info(f"Found product with {reader.name}")
                    return result
                    
            except ReaderError as e:
                self.logger.warning(f"Reader error in {reader.name}: {e}")
                continue
            except Exception as e:
                self.logger.error(f"Unexpected error in {reader.name}: {e}")
                continue
        
        self.logger.info(f"No product found for name '{name}'")
        return None
    
    def get_available_readers(self) -> List[str]:
        """
        Get list of currently available readers.
        
        Returns:
            List of reader names that are currently available
        """
        available = []
        for reader in self.readers:
            try:
                if reader.is_available():
                    available.append(reader.name)
            except:
                continue
        return available
    
    def add_reader(self, reader) -> None:
        """
        Add a new reader to the scanner.
        
        Args:
            reader: Reader instance to add
        """
        self.readers.append(reader)
        self.readers.sort(key=lambda r: r.get_priority())
        self.logger.info(f"Added reader {reader.name}")
    
    def remove_reader(self, reader_name: str) -> bool:
        """
        Remove a reader from the scanner.
        
        Args:
            reader_name: Name of the reader to remove
            
        Returns:
            True if reader was removed, False if not found
        """
        for i, reader in enumerate(self.readers):
            if reader.name == reader_name:
                del self.readers[i]
                self.logger.info(f"Removed reader {reader_name}")
                return True
        return False