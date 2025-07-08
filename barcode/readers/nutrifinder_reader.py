"""
NutriFinder reader implementation.

This reader fetches nutrition information from the NutriFinder API for simple ingredients.
"""

import re
import requests
from typing import Optional, Dict, Any
from ..exceptions import ReaderError, NetworkError
from .base_reader import CombinedReader


class NutriFinderReader(CombinedReader):
    """
    Reader for NutriFinder API.
    
    Specializes in nutrition data for simple ingredients (no barcode lookup).
    Uses DTU Nutrition database via NutriFinder API.
    """
    
    def __init__(self):
        super().__init__("NutriFinder")
        self.base_url = "https://api.mtbonde.dev/api/nutrition"
        self.timeout = 10
        self.name_pattern = re.compile(r'^[a-åA-Å]{1,32}$')
    
    def lookup_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Look up product information by barcode from NutriFinder.
        
        Note: NutriFinder doesn't support barcode lookup, returns None.
        
        Args:
            barcode: The product barcode
            
        Returns:
            None (barcode lookup not supported by NutriFinder)
        """
        self.logger.info(f"Barcode lookup not supported for NutriFinder: {barcode}")
        return None
    
    def lookup_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Look up product information by name from NutriFinder.
        
        Args:
            name: The product name
            
        Returns:
            Product information dictionary or None if not found
        """
        try:
            # Validate input (1-32 characters, English/Danish letters only)
            if not self.name_pattern.match(name):
                self.logger.warning(f"Invalid food item name for NutriFinder: {name}")
                return None
            
            self.logger.info(f"Looking up ingredient '{name}' in NutriFinder")
            
            # Make API request
            url = f"{self.base_url}?foodItemName={name}"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Create product info with nutrition data
                product_info = {
                    'name': data.get('foodItemName', name),
                    'brand': None,
                    'quantity': 100.0,  # NutriFinder returns per 100g
                    'quantity_unit': 'g',
                    'barcode': None,
                    'price': 0.0,
                    'source': 'nutrifinder',
                    'is_danish': True,  # DTU data is Danish
                    'raw_data': data
                }
                
                return product_info
                
            elif response.status_code == 404:
                self.logger.info(f"Food item not found in NutriFinder: {name}")
                return None
            else:
                self.logger.warning(f"NutriFinder API returned status {response.status_code} for {name}")
                return None
                
        except requests.exceptions.Timeout:
            raise NetworkError("NutriFinder", "Request timeout")
        except requests.exceptions.RequestException as e:
            raise NetworkError("NutriFinder", f"Request failed: {e}")
        except Exception as e:
            raise ReaderError("NutriFinder", f"Unexpected error: {e}")
    
    def get_nutrition(self, product_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract nutrition information from NutriFinder product data.
        
        Args:
            product_info: Product information dictionary with raw_data
            
        Returns:
            Nutrition information dictionary or None if not available
        """
        try:
            raw_data = product_info.get('raw_data')
            if not raw_data:
                return None
            
            # Map NutriFinder response to our format
            nutrition = {
                'calories': raw_data.get('kcal'),
                'protein': raw_data.get('protein'),
                'carbohydrates': raw_data.get('carb'),
                'fat': raw_data.get('fat'),
                'fiber': raw_data.get('fiber')
            }
            
            # Filter out None values and check if we have any valid nutrition data
            valid_nutrition = {k: v for k, v in nutrition.items() if v is not None}
            
            if valid_nutrition:
                self.logger.info(f"Successfully extracted nutrition data from NutriFinder: {list(valid_nutrition.keys())}")
                return nutrition
            else:
                self.logger.info("No valid nutrition data found in NutriFinder response")
                return None
                
        except Exception as e:
            self.logger.error(f"Error extracting nutrition from NutriFinder: {e}")
            return None
    
    def supports_product(self, product_info: Dict[str, Any]) -> bool:
        """
        Check if this reader can provide nutrition for the given product.
        
        Args:
            product_info: Product information dictionary
            
        Returns:
            True if product has NutriFinder raw data
        """
        return (product_info.get('source') == 'nutrifinder' and 
                product_info.get('raw_data') is not None)
    
    def is_available(self) -> bool:
        """
        Check if NutriFinder API is accessible.
        
        Returns:
            True if API is reachable
        """
        try:
            response = requests.head("https://api.mtbonde.dev", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_priority(self) -> int:
        """
        Get the priority of this reader.
        
        Returns:
            Priority value (20 for NutriFinder - lower priority than OpenFoodFacts)
        """
        return 20
    
    def fetch_nutrition_only(self, food_item_name: str) -> Optional[Dict[str, Any]]:
        """
        Direct nutrition lookup for compatibility with existing code.
        
        Args:
            food_item_name: Name of the food item to look up
            
        Returns:
            Nutrition data if found, None otherwise
        """
        product_info = self.lookup_by_name(food_item_name)
        if product_info:
            return self.get_nutrition(product_info)
        return None