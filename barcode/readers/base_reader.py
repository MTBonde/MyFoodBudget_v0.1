"""
Abstract base classes for barcode readers.

This module defines the interfaces that all barcode readers must implement,
following the Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging


class ProductReader(ABC):
    """
    Abstract base class for product information readers.
    
    Readers implementing this interface can look up product information
    by barcode or by name.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def lookup_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Look up product information by barcode.
        
        Args:
            barcode: The product barcode
            
        Returns:
            Product information dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def lookup_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Look up product information by name.
        
        Args:
            name: The product name
            
        Returns:
            Product information dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this reader is currently available (e.g., API is accessible).
        
        Returns:
            True if reader is available
        """
        pass
    
    def get_priority(self) -> int:
        """
        Get the priority of this reader (lower number = higher priority).
        
        Returns:
            Priority value (default: 100)
        """
        return 100


class NutritionReader(ABC):
    """
    Abstract base class for nutrition information readers.
    
    Readers implementing this interface can extract nutrition information
    from product data.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def get_nutrition(self, product_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract nutrition information from product data.
        
        Args:
            product_info: Product information dictionary
            
        Returns:
            Nutrition information dictionary or None if not available
        """
        pass
    
    @abstractmethod
    def supports_product(self, product_info: Dict[str, Any]) -> bool:
        """
        Check if this reader can provide nutrition for the given product.
        
        Args:
            product_info: Product information dictionary
            
        Returns:
            True if nutrition can be provided
        """
        pass


class CombinedReader(ProductReader, NutritionReader):
    """
    Abstract base class for readers that provide both product and nutrition information.
    
    This class combines both interfaces for readers that can handle complete
    product lookup and nutrition extraction.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def lookup_product_with_nutrition(self, barcode: str = None, name: str = None) -> Optional[Dict[str, Any]]:
        """
        Look up product information with nutrition data.
        
        Args:
            barcode: The product barcode (optional)
            name: The product name (optional)
            
        Returns:
            Combined product and nutrition information or None
        """
        product_info = None
        
        if barcode:
            product_info = self.lookup_by_barcode(barcode)
        
        if not product_info and name:
            product_info = self.lookup_by_name(name)
        
        if not product_info:
            return None
        
        # Add nutrition information if available
        nutrition = self.get_nutrition(product_info)
        if nutrition:
            product_info['nutrition'] = nutrition
        
        return product_info