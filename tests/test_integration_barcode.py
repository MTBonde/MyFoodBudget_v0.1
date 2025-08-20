"""
Integration tests for the complete barcode scanning workflow.
Tests the full pipeline from barcode scanning to database storage.
"""
import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock

from app_factory import create_app
from config import TestingConfig
from extensions import db
from models import Ingredient
from services import lookup_product_by_barcode, create_ingredient, get_nutrition_data_dual_source
from exceptions import DuplicateResourceError


class TestBarcodeIntegration(unittest.TestCase):
    """Integration tests for barcode scanning workflow."""
    
    def setUp(self):
        """Set up test fixtures with clean database."""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Create all tables
        db.create_all()
        
        # Create test user
        self.test_user = self._create_test_user()
    
    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def _create_test_user(self, username="testuser", email="test@example.com"):
        """Helper method to create a test user."""
        from models import User
        from werkzeug.security import generate_password_hash
        test_user = User(username=username, email=email, hash=generate_password_hash("password"))
        db.session.add(test_user)
        db.session.commit()
        return test_user
    
    def test_full_barcode_workflow_with_real_data(self):
        """
        Test complete workflow: barcode lookup -> nutrition fetch -> database storage.
        Uses Krægården smør barcode for real data integration.
        """
        # Arrange
        test_barcode = "5740900403376"  # Krægården smør
        
        # Act 1: Lookup product by barcode
        product_info = lookup_product_by_barcode(test_barcode)
        
        # Assert 1: Product found
        self.assertIsNotNone(product_info, "Product lookup should succeed")
        self.assertEqual(product_info['barcode'], test_barcode)
        self.assertIn('name', product_info)
        self.assertEqual(product_info['source'], 'api')
        
        # Act 2: Get nutrition data
        nutrition_data = get_nutrition_data_dual_source(product_info['name'], test_barcode)
        
        # Assert 2: Nutrition data retrieved
        self.assertIsNotNone(nutrition_data, "Nutrition data should be available")
        self.assertIn('calories', nutrition_data)
        self.assertIn('protein', nutrition_data)
        self.assertIn('fat', nutrition_data)
        
        # Act 3: Create ingredient in database
        ingredient = create_ingredient(
            name=product_info['name'],
            quantity=product_info['quantity'],
            quantity_unit=product_info['quantity_unit'],
            price=25.0,  # User-provided price
            barcode=test_barcode,
            brand=product_info['brand'],
            user_id=self.test_user.id
        )
        
        # Assert 3: Ingredient created successfully
        self.assertIsNotNone(ingredient, "Ingredient should be created")
        self.assertEqual(ingredient.barcode, test_barcode)
        self.assertEqual(ingredient.name, product_info['name'])
        self.assertIsNotNone(ingredient.calories, "Nutrition data should be stored")
        
        # Act 4: Verify database persistence
        stored_ingredient = Ingredient.query.filter_by(barcode=test_barcode).first()
        
        # Assert 4: Data persisted correctly
        self.assertIsNotNone(stored_ingredient, "Ingredient should be in database")
        self.assertEqual(stored_ingredient.barcode, test_barcode)
        self.assertEqual(stored_ingredient.calories, nutrition_data['calories'])
        self.assertEqual(stored_ingredient.protein, nutrition_data['protein'])
        
    def test_duplicate_barcode_handling(self):
        """Test that duplicate barcodes are handled correctly."""
        # Arrange
        test_barcode = "5740900403376"
        
        # Act 1: Create first ingredient
        ingredient1 = create_ingredient(
            name="First Butter",
            quantity=200.0,
            quantity_unit="g",
            price=20.0,
            barcode=test_barcode,
            brand="Brand1",
            user_id=self.test_user.id
        )
        
        # Assert 1: First ingredient created
        self.assertIsNotNone(ingredient1)
        
        # Act 2: Try to create duplicate
        with self.assertRaises(DuplicateResourceError):
            create_ingredient(
                name="Second Butter",
                quantity=500.0,
                quantity_unit="g", 
                price=30.0,
                barcode=test_barcode,  # Same barcode
                brand="Brand2",
                user_id=self.test_user.id
            )
        
        # Assert 3: Only one ingredient in database
        ingredients = Ingredient.query.filter_by(barcode=test_barcode).all()
        self.assertEqual(len(ingredients), 1)
        
    def test_barcode_workflow_with_invalid_barcode(self):
        """Test workflow behavior with invalid barcode."""
        # Arrange
        invalid_barcode = "1234567890"  # Invalid length
        
        # Act & Assert: Should handle gracefully
        product_info = lookup_product_by_barcode(invalid_barcode)
        self.assertIsNone(product_info, "Invalid barcode should return None")
        
    def test_barcode_workflow_without_nutrition_data(self):
        """Test workflow when nutrition data is not available."""
        # Arrange - Mock scanner to return product but no nutrition
        test_barcode = "8712566311316"  # Valid barcode format
        
        with patch('services.BarcodeScanner') as mock_scanner_class:
            mock_scanner = mock_scanner_class.return_value
            
            # Mock product lookup success but nutrition failure
            mock_scanner.lookup_product.return_value = {
                'name': 'Test Product',
                'brand': 'Test Brand',
                'quantity': 100.0,
                'quantity_unit': 'g',
                'barcode': test_barcode
            }
            mock_scanner.get_nutrition_data.return_value = None
            
            # Act
            ingredient = create_ingredient(
                name="Test Product",
                quantity=100.0,
                quantity_unit="g",
                price=15.0,
                barcode=test_barcode,
                brand="Test Brand",
                user_id=self.test_user.id
            )
            
            # Assert: Ingredient created without nutrition data
            self.assertIsNotNone(ingredient, "Ingredient should be created even without nutrition")
            self.assertIsNone(ingredient.calories, "Calories should be None")
            self.assertIsNone(ingredient.protein, "Protein should be None")
            
    def test_database_schema_compatibility(self):
        """Test that database schema matches model expectations."""
        # Arrange & Act: Create ingredient with all nutrition fields
        ingredient = Ingredient(
            name="Schema Test Product",
            quantity=100.0,
            quantity_unit="g",
            price=10.0,
            barcode="1234567890128",
            brand="Test Brand",
            user_id=self.test_user.id,
            calories=250.0,
            protein=15.0,
            carbohydrates=30.0,
            fat=8.0,
            fiber=5.0
        )
        
        db.session.add(ingredient)
        db.session.commit()
        
        # Assert: All fields stored and retrieved correctly
        stored = Ingredient.query.filter_by(name="Schema Test Product").first()
        self.assertIsNotNone(stored)
        self.assertEqual(stored.calories, 250.0)
        self.assertEqual(stored.protein, 15.0)
        self.assertEqual(stored.carbohydrates, 30.0)
        self.assertEqual(stored.fat, 8.0)
        self.assertEqual(stored.fiber, 5.0)


class TestWebEndpointIntegration(unittest.TestCase):
    """Integration tests for web endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Create all tables
        db.create_all()
        
        # Create test user and login
        from services import register_user
        register_user("testuser", "test@example.com", "password123")
        
        # Login
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
    
    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_scan_product_endpoint_success(self):
        """Test /scan_product endpoint with valid barcode."""
        # Arrange
        test_data = {
            'barcode': '5740900403376'  # Krægården smør
        }
        
        # Act
        response = self.client.post('/scan_product', 
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'found')
        self.assertIn('product', data)
        self.assertIn('redirect', data)
        
    def test_scan_product_endpoint_invalid_barcode(self):
        """Test /scan_product endpoint with invalid barcode."""
        # Arrange
        test_data = {
            'barcode': '123456789'  # Invalid barcode
        }
        
        # Act
        response = self.client.post('/scan_product',
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'not_found')
        
    def test_add_ingredient_with_barcode_parameter(self):
        """Test /add_ingredient endpoint with barcode parameter."""
        # Act
        response = self.client.get('/add_ingredient?barcode=5740900403376')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        # Check that product data is pre-filled in the form
        self.assertIn(b'Butter', response.data)  # Product name should be pre-filled
        
    def test_add_ingredient_form_submission_with_nutrition(self):
        """Test complete form submission with barcode and nutrition data."""
        # Arrange
        form_data = {
            'name': 'Integration Test Butter',
            'brand': 'Test Brand',
            'barcode': '1234567890128',  # Valid format
            'quantity': '200',
            'quantity_unit': 'g',
            'price': '25.50'
        }
        
        # Act
        response = self.client.post('/add_ingredient', data=form_data)
        
        # Assert
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify ingredient was created in database
        ingredient = Ingredient.query.filter_by(barcode='1234567890128').first()
        self.assertIsNotNone(ingredient)
        self.assertEqual(ingredient.name, 'Integration Test Butter')
        self.assertEqual(ingredient.price, 25.50)


if __name__ == '__main__':
    unittest.main()