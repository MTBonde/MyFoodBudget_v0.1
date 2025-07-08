"""
OpenFoodFacts reader implementation.

This reader fetches product and nutrition information from the OpenFoodFacts API.
"""

import re
import requests
from typing import Optional, Dict, Any
from ..exceptions import ReaderError, NetworkError
from ..validators import validate_barcode, normalize_barcode, is_danish_barcode
from .base_reader import CombinedReader


class OpenFoodFactsReader(CombinedReader):
    """
    Reader for OpenFoodFacts API.
    
    Provides both product information and nutrition data from OpenFoodFacts.
    """
    
    def __init__(self):
        super().__init__("OpenFoodFacts")
        self.base_url = "https://world.openfoodfacts.org/api/v0/product"
        self.timeout = 10
        self.user_agent = "MyFoodBudget/0.1 (https://github.com/user/myfoodbudget)"
    
    def lookup_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Look up product information by barcode from OpenFoodFacts.
        
        Args:
            barcode: The product barcode
            
        Returns:
            Product information dictionary or None if not found
        """
        try:
            # Validate and normalize barcode
            validate_barcode(barcode)
            clean_barcode = normalize_barcode(barcode)
            
            self.logger.info(f"Looking up barcode {clean_barcode} in OpenFoodFacts")
            
            # Make API request
            url = f"{self.base_url}/{clean_barcode}.json"
            headers = {'User-Agent': self.user_agent}
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 1 and data.get('product'):
                product_info = self._normalize_product_data(data['product'])
                product_info['source'] = 'openfoodfacts'
                product_info['is_danish'] = is_danish_barcode(clean_barcode)
                return product_info
            else:
                self.logger.info(f"Product not found for barcode: {clean_barcode}")
                return None
                
        except requests.exceptions.Timeout:
            raise NetworkError("OpenFoodFacts", "Request timeout")
        except requests.exceptions.RequestException as e:
            raise NetworkError("OpenFoodFacts", f"Request failed: {e}")
        except Exception as e:
            raise ReaderError("OpenFoodFacts", f"Unexpected error: {e}")
    
    def lookup_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Look up product information by name from OpenFoodFacts.
        
        Note: OpenFoodFacts doesn't have a direct name search API that's reliable
        for our use case, so this returns None.
        
        Args:
            name: The product name
            
        Returns:
            None (name search not implemented for OpenFoodFacts)
        """
        self.logger.info(f"Name-based lookup not supported for OpenFoodFacts: {name}")
        return None
    
    def get_nutrition(self, product_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract nutrition information from OpenFoodFacts product data.
        
        Args:
            product_info: Product information dictionary with raw_data
            
        Returns:
            Nutrition information dictionary or None if not available
        """
        try:
            raw_data = product_info.get('raw_data')
            if not raw_data:
                return None
            
            nutriments = raw_data.get('nutriments', {})
            
            if not nutriments:
                self.logger.info("No nutriments data found in OpenFoodFacts product")
                return None
            
            # Handle energy conversion - try kcal first, then kJ
            calories = nutriments.get('energy-kcal_100g')
            if not calories:
                # Convert from kJ to kcal if only kJ is available
                energy_kj = nutriments.get('energy_100g', 0)
                calories = energy_kj * 0.239006 if energy_kj else None
            
            nutrition = {
                'calories': calories,
                'protein': nutriments.get('proteins_100g'),
                'carbohydrates': nutriments.get('carbohydrates_100g'),
                'fat': nutriments.get('fat_100g'),
                'fiber': nutriments.get('fiber_100g')
            }
            
            # Filter out None values and check if we have any valid nutrition data
            valid_nutrition = {k: v for k, v in nutrition.items() if v is not None}
            
            if valid_nutrition:
                self.logger.info(f"Successfully extracted nutrition data from OpenFoodFacts: {list(valid_nutrition.keys())}")
                return nutrition
            else:
                self.logger.info("No valid nutrition data found in OpenFoodFacts product")
                return None
                
        except Exception as e:
            self.logger.error(f"Error extracting nutrition from OpenFoodFacts product: {e}")
            return None
    
    def supports_product(self, product_info: Dict[str, Any]) -> bool:
        """
        Check if this reader can provide nutrition for the given product.
        
        Args:
            product_info: Product information dictionary
            
        Returns:
            True if product has OpenFoodFacts raw data
        """
        return (product_info.get('source') == 'openfoodfacts' and 
                product_info.get('raw_data') is not None)
    
    def is_available(self) -> bool:
        """
        Check if OpenFoodFacts API is accessible.
        
        Returns:
            True if API is reachable
        """
        try:
            response = requests.head("https://world.openfoodfacts.org", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_priority(self) -> int:
        """
        Get the priority of this reader.
        
        Returns:
            Priority value (10 for OpenFoodFacts - high priority for barcoded products)
        """
        return 10
    
    def _normalize_product_data(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize OpenFoodFacts product data to our application format.
        
        Args:
            product_data: Raw product data from OpenFoodFacts API
            
        Returns:
            Normalized product information
        """
        # Extract product name (try multiple fields)
        name = (product_data.get('product_name') or 
                product_data.get('product_name_en') or 
                product_data.get('generic_name') or 
                'Unknown Product')
        
        # Extract brand information
        brand = (product_data.get('brands') or 
                 product_data.get('brand_owner') or 
                 None)
        
        # Extract quantity information
        quantity_text = product_data.get('quantity', '')
        quantity, quantity_unit = self._parse_quantity_from_text(quantity_text)
        
        # Extract barcode (code field)
        barcode = product_data.get('code')
        
        return {
            'name': name.strip(),
            'brand': brand.strip() if brand else None,
            'quantity': quantity,
            'quantity_unit': quantity_unit,
            'barcode': barcode,
            'price': 0.0,  # Price needs to be entered by user
            'raw_data': product_data  # Keep raw data for nutrition extraction
        }
    
    def _parse_quantity_from_text(self, quantity_text: str) -> tuple:
        """
        Parse quantity and unit from OpenFoodFacts quantity text.
        
        Args:
            quantity_text: Quantity text like "500g", "1L", "250ml"
            
        Returns:
            Tuple of (quantity, unit) where quantity is float and unit is string
        """
        if not quantity_text:
            return 1.0, 'unit'
        
        # Try to extract number and unit using regex
        match = re.search(r'(\d+(?:\.\d+)?)\s*([a-zA-Z\s]+)', quantity_text)
        
        if match:
            quantity = float(match.group(1))
            unit = match.group(2).lower().strip()
            
            # Normalize common units
            unit_mapping = {
                'ml': 'ml',
                'milliliter': 'ml',
                'milliliters': 'ml',
                'l': 'l',
                'liter': 'l',
                'liters': 'l',
                'g': 'g',
                'gram': 'g',
                'grams': 'g',
                'kg': 'kg',
                'kilogram': 'kg',
                'kilograms': 'kg',
                'oz': 'oz',
                'ounce': 'oz',
                'ounces': 'oz',
                'lb': 'lb',
                'pound': 'lb',
                'pounds': 'lb'
            }
            
            normalized_unit = unit_mapping.get(unit, unit)
            return quantity, normalized_unit
        
        # If no number found, default to 1 unit
        return 1.0, 'unit'