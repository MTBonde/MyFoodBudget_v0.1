"""
Tests for the barcode module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from barcode.validators import validate_ean13, validate_ean8, is_danish_barcode, normalize_barcode
from barcode.exceptions import InvalidBarcodeError
from barcode.scanner import BarcodeScanner
from barcode.readers import OpenFoodFactsReader, NutriFinderReader


class TestBarcodeValidators(unittest.TestCase):
    """Test barcode validation functions."""
    
    def test_validate_ean13_valid(self):
        """Test validation of valid EAN-13 barcodes."""
        # Valid EAN-13 barcode (test barcode: 1234567890128)
        self.assertTrue(validate_ean13("1234567890128"))
        
    def test_validate_ean13_invalid_checksum(self):
        """Test validation of EAN-13 with invalid checksum."""
        # Invalid checksum
        self.assertFalse(validate_ean13("1234567890123"))
        
    def test_validate_ean13_wrong_length(self):
        """Test validation of wrong length barcodes."""
        self.assertFalse(validate_ean13("123456"))
        self.assertFalse(validate_ean13("12345678901234"))
        
    def test_is_danish_barcode(self):
        """Test Danish barcode detection."""
        # Danish barcode (starts with 57)
        self.assertTrue(is_danish_barcode("5700000000003"))
        # Non-Danish barcode
        self.assertFalse(is_danish_barcode("1234567890128"))
        
    def test_normalize_barcode(self):
        """Test barcode normalization."""
        self.assertEqual(normalize_barcode("570-000-000003"), "5700000000003")
        self.assertEqual(normalize_barcode("570 000 000003"), "5700000000003")


class TestBarcodeScanner(unittest.TestCase):
    """Test the main BarcodeScanner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_openfoodfacts_reader = Mock(spec=OpenFoodFactsReader)
        self.mock_nutrifinder_reader = Mock(spec=NutriFinderReader)
        
        # Configure mock readers
        self.mock_openfoodfacts_reader.name = "OpenFoodFacts"
        self.mock_openfoodfacts_reader.get_priority.return_value = 10
        self.mock_openfoodfacts_reader.is_available.return_value = True
        
        self.mock_nutrifinder_reader.name = "NutriFinder"
        self.mock_nutrifinder_reader.get_priority.return_value = 20
        self.mock_nutrifinder_reader.is_available.return_value = True
        
        self.scanner = BarcodeScanner([self.mock_openfoodfacts_reader, self.mock_nutrifinder_reader])
    
    def test_lookup_product_by_barcode_success(self):
        """Test successful product lookup by barcode."""
        # Arrange
        test_barcode = "1234567890128"  # Valid test barcode
        expected_product = {
            'name': 'Test Product',
            'brand': 'Test Brand',
            'barcode': test_barcode
        }
        
        self.mock_openfoodfacts_reader.lookup_by_barcode.return_value = expected_product
        
        # Act
        result = self.scanner.lookup_product(barcode=test_barcode)
        
        # Assert
        self.assertEqual(result, expected_product)
        self.mock_openfoodfacts_reader.lookup_by_barcode.assert_called_once_with(test_barcode)
    
    def test_lookup_product_by_name_fallback(self):
        """Test product lookup by name when barcode fails."""
        # Arrange
        test_name = "apple"
        expected_product = {
            'name': 'Apple',
            'source': 'nutrifinder'
        }
        
        self.mock_openfoodfacts_reader.lookup_by_name.return_value = None
        self.mock_nutrifinder_reader.lookup_by_name.return_value = expected_product
        
        # Act
        result = self.scanner.lookup_product(name=test_name)
        
        # Assert
        self.assertEqual(result, expected_product)
        self.mock_nutrifinder_reader.lookup_by_name.assert_called_once_with(test_name)
    
    def test_get_nutrition_data_success(self):
        """Test successful nutrition data retrieval."""
        # Arrange
        test_name = "apple"
        product_info = {
            'name': 'Apple',
            'source': 'nutrifinder',
            'raw_data': {'kcal': 52, 'protein': 0.3}
        }
        expected_nutrition = {
            'calories': 52,
            'protein': 0.3,
            'carbohydrates': 14,
            'fat': 0.2,
            'fiber': 2.4
        }
        
        self.mock_nutrifinder_reader.lookup_by_name.return_value = product_info
        self.mock_nutrifinder_reader.supports_product.return_value = True
        self.mock_nutrifinder_reader.get_nutrition.return_value = expected_nutrition
        
        # Act
        result = self.scanner.get_nutrition_data(name=test_name)
        
        # Assert
        self.assertEqual(result, expected_nutrition)
    
    def test_get_available_readers(self):
        """Test getting list of available readers."""
        # Act
        available = self.scanner.get_available_readers()
        
        # Assert
        self.assertEqual(available, ["OpenFoodFacts", "NutriFinder"])
    
    def test_add_reader(self):
        """Test adding a new reader."""
        # Arrange
        new_reader = Mock()
        new_reader.name = "TestReader"
        new_reader.get_priority.return_value = 15
        
        # Act
        self.scanner.add_reader(new_reader)
        
        # Assert
        self.assertIn(new_reader, self.scanner.readers)
    
    def test_remove_reader(self):
        """Test removing a reader."""
        # Act
        result = self.scanner.remove_reader("OpenFoodFacts")
        
        # Assert
        self.assertTrue(result)
        reader_names = [r.name for r in self.scanner.readers]
        self.assertNotIn("OpenFoodFacts", reader_names)


class TestOpenFoodFactsReader(unittest.TestCase):
    """Test OpenFoodFacts reader implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = OpenFoodFactsReader()
    
    @patch('barcode.readers.openfoodfacts_reader.requests.get')
    def test_lookup_by_barcode_success(self, mock_get):
        """Test successful barcode lookup."""
        # Arrange
        test_barcode = "1234567890128"  # Valid test barcode
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 1,
            'product': {
                'product_name': 'Test Product',
                'brands': 'Test Brand',
                'quantity': '500g',
                'code': test_barcode
            }
        }
        mock_get.return_value = mock_response
        
        # Act
        result = self.reader.lookup_by_barcode(test_barcode)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Test Product')
        self.assertEqual(result['brand'], 'Test Brand')
        self.assertEqual(result['barcode'], test_barcode)
    
    def test_lookup_by_name_not_supported(self):
        """Test that name lookup returns None (not supported)."""
        result = self.reader.lookup_by_name("test product")
        self.assertIsNone(result)
    
    def test_get_priority(self):
        """Test reader priority."""
        self.assertEqual(self.reader.get_priority(), 10)


class TestNutriFinderReader(unittest.TestCase):
    """Test NutriFinder reader implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = NutriFinderReader()
    
    @patch('barcode.readers.nutrifinder_reader.requests.get')
    def test_lookup_by_name_success(self, mock_get):
        """Test successful name lookup."""
        # Arrange
        test_name = "apple"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'foodItemName': 'Apple',
            'kcal': 52,
            'protein': 0.3,
            'carb': 14,
            'fat': 0.2,
            'fiber': 2.4
        }
        mock_get.return_value = mock_response
        
        # Act
        result = self.reader.lookup_by_name(test_name)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Apple')
        self.assertEqual(result['source'], 'nutrifinder')
        self.assertTrue(result['is_danish'])
    
    def test_lookup_by_barcode_not_supported(self):
        """Test that barcode lookup returns None (not supported)."""
        result = self.reader.lookup_by_barcode("1234567890123")
        self.assertIsNone(result)
    
    def test_get_priority(self):
        """Test reader priority."""
        self.assertEqual(self.reader.get_priority(), 20)
    
    def test_invalid_name_format(self):
        """Test that invalid name format returns None."""
        result = self.reader.lookup_by_name("invalid-name-123")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()