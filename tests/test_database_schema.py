"""
Database schema validation tests.
Ensures that the database schema matches the model definitions.
"""
import unittest
import sqlite3
import tempfile
import os
from app_factory import create_app
from config import TestingConfig
from extensions import db
from models import Ingredient, Recipe, RecipeIngredient, User


class TestDatabaseSchema(unittest.TestCase):
    """Test database schema consistency."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create all tables
        db.create_all()
    
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
    
    def test_ingredient_table_schema(self):
        """Test that Ingredient table has all required columns."""
        # Create a test user first
        test_user = self._create_test_user()
        
        # Create a test ingredient to ensure table exists
        test_ingredient = Ingredient(
            name="Schema Test",
            quantity=100.0,
            quantity_unit="g",
            price=10.0,
            user_id=test_user.id
        )
        db.session.add(test_ingredient)
        db.session.commit()
        
        # Get table info from SQLite
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = {}
        
        for column in inspector.get_columns('ingredients'):
            columns[column['name']] = str(column['type']).upper()
        
        # Expected columns from Ingredient model (checking existence, not exact types)
        expected_columns = [
            'id', 'name', 'quantity', 'quantity_unit', 'price', 
            'barcode', 'brand', 'user_id', 'calories', 'protein', 
            'carbohydrates', 'fat', 'fiber'
        ]
        
        # Assert all expected columns exist
        for column_name in expected_columns:
            self.assertIn(column_name, columns, 
                         f"Column '{column_name}' missing from ingredients table")
        
        print(f"✅ Found all {len(expected_columns)} expected columns in ingredients table")
    
    def test_nutrition_columns_nullable(self):
        """Test that nutrition columns can be NULL."""
        # Create test user first
        test_user = self._create_test_user()
        
        # Create ingredient without nutrition data
        ingredient = Ingredient(
            name="Test Product",
            quantity=100.0,
            quantity_unit="g",
            price=10.0,
            user_id=test_user.id
        )
        
        db.session.add(ingredient)
        db.session.commit()
        
        # Verify stored correctly with NULL nutrition values
        stored = Ingredient.query.filter_by(name="Test Product").first()
        self.assertIsNotNone(stored)
        self.assertIsNone(stored.calories)
        self.assertIsNone(stored.protein)
        self.assertIsNone(stored.carbohydrates)
        self.assertIsNone(stored.fat)
        self.assertIsNone(stored.fiber)
    
    def test_barcode_unique_constraint(self):
        """Test that barcode field has unique constraint."""
        # Create test user first
        test_user = self._create_test_user()
        
        # Create first ingredient
        ingredient1 = Ingredient(
            name="Product 1",
            quantity=100.0,
            quantity_unit="g",
            price=10.0,
            barcode="1234567890123",
            user_id=test_user.id
        )
        db.session.add(ingredient1)
        db.session.commit()
        
        # Try to create second ingredient with same barcode
        ingredient2 = Ingredient(
            name="Product 2",
            quantity=200.0,
            quantity_unit="g",
            price=20.0,
            barcode="1234567890123",  # Same barcode
            user_id=test_user.id
        )
        db.session.add(ingredient2)
        
        # Should raise IntegrityError
        with self.assertRaises(Exception):  # IntegrityError
            db.session.commit()
    
    def test_all_models_create_successfully(self):
        """Test that all models can be created and relationships work."""
        # Create user
        user = User(username="testuser", email="test@example.com", hash="hashed")
        db.session.add(user)
        db.session.commit()
        
        # Create ingredients
        ingredient1 = Ingredient(
            name="Flour", quantity=1000.0, quantity_unit="g", price=5.0,
            user_id=user.id,
            calories=364.0, protein=10.3, carbohydrates=76.3, fat=1.0, fiber=2.7
        )
        ingredient2 = Ingredient(
            name="Sugar", quantity=500.0, quantity_unit="g", price=3.0,
            user_id=user.id,
            calories=387.0, protein=0.0, carbohydrates=100.0, fat=0.0, fiber=0.0
        )
        db.session.add_all([ingredient1, ingredient2])
        db.session.commit()
        
        # Create recipe
        recipe = Recipe(name="Test Recipe", instructions="Mix ingredients", total_price=8.0, user_id=user.id)
        db.session.add(recipe)
        db.session.commit()
        
        # Create recipe ingredients
        recipe_ing1 = RecipeIngredient(
            recipe_id=recipe.id, ingredient_id=ingredient1.id,
            quantity=200.0, quantity_unit="g"
        )
        recipe_ing2 = RecipeIngredient(
            recipe_id=recipe.id, ingredient_id=ingredient2.id,
            quantity=100.0, quantity_unit="g"
        )
        db.session.add_all([recipe_ing1, recipe_ing2])
        db.session.commit()
        
        # Verify everything was created
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(Ingredient.query.count(), 2)
        self.assertEqual(Recipe.query.count(), 1)
        self.assertEqual(RecipeIngredient.query.count(), 2)
        
        # Test relationships
        stored_recipe = Recipe.query.first()
        self.assertEqual(len(stored_recipe.recipe_ingredients), 2)
    
    def test_database_migration_compatibility(self):
        """Test that existing data survives schema updates."""
        # This test simulates adding nutrition columns to existing data
        
        # Create test user first
        test_user = self._create_test_user()
        
        # 1. Create ingredient using ORM first (simulates existing data)
        old_ingredient = Ingredient(
            name="Old Product",
            quantity=100.0,
            quantity_unit="g",
            price=15.0,
            barcode="9876543210987",
            brand="Old Brand",
            user_id=test_user.id
        )
        db.session.add(old_ingredient)
        db.session.commit()
        
        # 2. Simulate manual update to test migration compatibility
        # Use SQLAlchemy's connection for in-memory database
        from sqlalchemy import text
        
        # Update using raw SQL to simulate schema migration
        db.session.execute(text('''
            UPDATE ingredients SET calories = :calories, protein = :protein
            WHERE barcode = :barcode
        '''), {'calories': 200.0, 'protein': 5.0, 'barcode': "9876543210987"})
        db.session.commit()
        
        # 3. Verify ingredient can be loaded with ORM after manual update
        ingredient = Ingredient.query.filter_by(name="Old Product").first()
        self.assertIsNotNone(ingredient)
        self.assertEqual(ingredient.name, "Old Product")
        self.assertEqual(ingredient.calories, 200.0)  # Should have updated value
        
        # 4. Verify we can update with more nutrition data via ORM
        ingredient.carbohydrates = 30.0
        ingredient.fat = 8.0
        db.session.commit()
        
        # 5. Verify update persisted
        updated = Ingredient.query.filter_by(name="Old Product").first()
        self.assertEqual(updated.calories, 200.0)
        self.assertEqual(updated.protein, 5.0)
        self.assertEqual(updated.carbohydrates, 30.0)
        self.assertEqual(updated.fat, 8.0)


class TestDatabaseOperations(unittest.TestCase):
    """Test database operations under various conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
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
    
    def test_concurrent_ingredient_creation(self):
        """Test that concurrent ingredient creation is handled properly."""
        # This would be more complex in a real concurrent scenario
        # For now, test sequential creation with potential conflicts
        
        # Create test user first
        test_user = self._create_test_user()
        
        ingredients = []
        for i in range(10):
            ingredient = Ingredient(
                name=f"Product {i}",
                quantity=100.0,
                quantity_unit="g",
                price=10.0 + i,
                barcode=f"123456789012{i}",
                user_id=test_user.id
            )
            ingredients.append(ingredient)
        
        # Add all at once
        db.session.add_all(ingredients)
        db.session.commit()
        
        # Verify all created
        self.assertEqual(Ingredient.query.count(), 10)
        
        # Verify barcodes are unique
        barcodes = [ing.barcode for ing in Ingredient.query.all()]
        self.assertEqual(len(barcodes), len(set(barcodes)))
    
    def test_large_data_handling(self):
        """Test handling of large nutrition values and long strings."""
        # Create test user first
        test_user = self._create_test_user()
        
        # Test with extreme values
        ingredient = Ingredient(
            name="X" * 255,  # Long name
            quantity=999999.99,  # Large quantity
            quantity_unit="kg",
            price=999999.99,  # Large price
            barcode="1234567890123",
            brand="Y" * 99,  # Long brand name
            user_id=test_user.id,
            calories=9999.99,  # High calories
            protein=999.99,   # High protein
            carbohydrates=999.99,
            fat=999.99,
            fiber=999.99
        )
        
        db.session.add(ingredient)
        db.session.commit()
        
        # Verify stored correctly
        stored = Ingredient.query.first()
        self.assertEqual(len(stored.name), 255)
        self.assertEqual(stored.quantity, 999999.99)
        self.assertEqual(stored.calories, 9999.99)


if __name__ == '__main__':
    unittest.main()