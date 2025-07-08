import pytest
from unittest.mock import patch, MagicMock
from services import (
    fetch_nutrition_from_nutrifinder,
    extract_nutrition_from_off_product,
    get_nutrition_data_dual_source
)


class TestNutritionService:
    """Test nutrition API integration functionality."""

    def test_fetch_nutrition_from_nutrifinder_success(self):
        """
        Test successful nutrition data fetch from NutriFinder API.
        
        Arrange: Mock successful API response
        Act: Call fetch_nutrition_from_nutrifinder
        Assert: Returns correct nutrition data
        """
        mock_response_data = {
            'kcal': 89.0,
            'protein': 4.3,
            'carb': 20.1,
            'fat': 0.3,
            'fiber': 2.6
        }
        
        with patch('services.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response
            
            result = fetch_nutrition_from_nutrifinder('tomato')
            
            expected = {
                'calories': 89.0,
                'protein': 4.3,
                'carbohydrates': 20.1,
                'fat': 0.3,
                'fiber': 2.6
            }
            
            assert result == expected
            mock_get.assert_called_once_with(
                'https://api.mtbonde.dev/api/nutrition?foodItemName=tomato',
                timeout=10
            )

    def test_fetch_nutrition_from_nutrifinder_not_found(self):
        """
        Test NutriFinder API when food item is not found.
        
        Arrange: Mock 404 response
        Act: Call fetch_nutrition_from_nutrifinder
        Assert: Returns None
        """
        with patch('services.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            result = fetch_nutrition_from_nutrifinder('unknownfood')
            
            assert result is None

    def test_fetch_nutrition_from_nutrifinder_invalid_input(self):
        """
        Test NutriFinder API with invalid ingredient name.
        
        Arrange: Invalid ingredient name
        Act: Call fetch_nutrition_from_nutrifinder
        Assert: Returns None without API call
        """
        result = fetch_nutrition_from_nutrifinder('invalid123')
        assert result is None
        
        result = fetch_nutrition_from_nutrifinder('')
        assert result is None

    def test_extract_nutrition_from_off_product_success(self):
        """
        Test successful nutrition extraction from OpenFoodFacts product data.
        
        Arrange: Mock OpenFoodFacts product data
        Act: Call extract_nutrition_from_off_product
        Assert: Returns correct nutrition data
        """
        mock_product_data = {
            'nutriments': {
                'energy-kcal_100g': 534.0,
                'proteins_100g': 25.0,
                'carbohydrates_100g': 30.0,
                'fat_100g': 29.0,
                'fiber_100g': 9.0
            }
        }
        
        result = extract_nutrition_from_off_product(mock_product_data)
        
        expected = {
            'calories': 534.0,
            'protein': 25.0,
            'carbohydrates': 30.0,
            'fat': 29.0,
            'fiber': 9.0
        }
        
        assert result == expected

    def test_extract_nutrition_from_off_product_energy_conversion(self):
        """
        Test nutrition extraction with energy conversion from kJ to kcal.
        
        Arrange: Mock product data with energy in kJ only
        Act: Call extract_nutrition_from_off_product
        Assert: Returns converted kcal value
        """
        mock_product_data = {
            'nutriments': {
                'energy_100g': 2234.0,  # kJ
                'proteins_100g': 25.0,
                'carbohydrates_100g': 30.0,
                'fat_100g': 29.0,
                'fiber_100g': 9.0
            }
        }
        
        result = extract_nutrition_from_off_product(mock_product_data)
        
        # 2234 kJ * 0.239006 = 534.0 kcal (approximately)
        expected_calories = 2234.0 * 0.239006
        assert result['calories'] == pytest.approx(expected_calories, rel=1e-3)
        assert result['protein'] == 25.0

    def test_extract_nutrition_from_off_product_no_nutriments(self):
        """
        Test nutrition extraction when no nutriments data is available.
        
        Arrange: Mock product data without nutriments
        Act: Call extract_nutrition_from_off_product
        Assert: Returns None
        """
        mock_product_data = {'product_name': 'Test Product'}
        
        result = extract_nutrition_from_off_product(mock_product_data)
        
        assert result is None

    def test_get_nutrition_data_dual_source_with_barcode_success(self):
        """
        Test dual-source nutrition lookup with successful OpenFoodFacts result.
        
        Arrange: Mock successful OpenFoodFacts fetch
        Act: Call get_nutrition_data_dual_source with barcode
        Assert: Returns OpenFoodFacts nutrition data
        """
        mock_product_data = {
            'nutriments': {
                'energy-kcal_100g': 534.0,
                'proteins_100g': 25.0,
                'carbohydrates_100g': 30.0,
                'fat_100g': 29.0,
                'fiber_100g': 9.0
            }
        }
        
        with patch('services.fetch_product_from_openfoodfacts') as mock_fetch:
            mock_fetch.return_value = mock_product_data
            
            result = get_nutrition_data_dual_source('test_product', '1234567890')
            
            expected = {
                'calories': 534.0,
                'protein': 25.0,
                'carbohydrates': 30.0,
                'fat': 29.0,
                'fiber': 9.0
            }
            
            assert result == expected
            mock_fetch.assert_called_once_with('1234567890')

    def test_get_nutrition_data_dual_source_fallback_to_nutrifinder(self):
        """
        Test dual-source nutrition lookup falling back to NutriFinder.
        
        Arrange: Mock failed OpenFoodFacts, successful NutriFinder
        Act: Call get_nutrition_data_dual_source
        Assert: Returns NutriFinder nutrition data
        """
        mock_nutrifinder_data = {
            'kcal': 89.0,
            'protein': 4.3,
            'carb': 20.1,
            'fat': 0.3,
            'fiber': 2.6
        }
        
        with patch('services.fetch_product_from_openfoodfacts') as mock_off:
            with patch('services.requests.get') as mock_get:
                # OpenFoodFacts returns None
                mock_off.return_value = None
                
                # NutriFinder returns data
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = mock_nutrifinder_data
                mock_get.return_value = mock_response
                
                result = get_nutrition_data_dual_source('tomato', '1234567890')
                
                expected = {
                    'calories': 89.0,
                    'protein': 4.3,
                    'carbohydrates': 20.1,
                    'fat': 0.3,
                    'fiber': 2.6
                }
                
                assert result == expected

    def test_get_nutrition_data_dual_source_no_barcode_uses_nutrifinder(self):
        """
        Test dual-source nutrition lookup without barcode uses NutriFinder directly.
        
        Arrange: Mock successful NutriFinder response
        Act: Call get_nutrition_data_dual_source without barcode
        Assert: Returns NutriFinder nutrition data, OpenFoodFacts not called
        """
        mock_nutrifinder_data = {
            'kcal': 89.0,
            'protein': 4.3,
            'carb': 20.1,
            'fat': 0.3,
            'fiber': 2.6
        }
        
        with patch('services.fetch_product_from_openfoodfacts') as mock_off:
            with patch('services.requests.get') as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = mock_nutrifinder_data
                mock_get.return_value = mock_response
                
                result = get_nutrition_data_dual_source('tomato')
                
                expected = {
                    'calories': 89.0,
                    'protein': 4.3,
                    'carbohydrates': 20.1,
                    'fat': 0.3,
                    'fiber': 2.6
                }
                
                assert result == expected
                # OpenFoodFacts should not be called without barcode
                mock_off.assert_not_called()

    def test_get_nutrition_data_dual_source_both_sources_fail(self):
        """
        Test dual-source nutrition lookup when both sources fail.
        
        Arrange: Mock failed responses from both APIs
        Act: Call get_nutrition_data_dual_source
        Assert: Returns None
        """
        with patch('services.fetch_product_from_openfoodfacts') as mock_off:
            with patch('services.requests.get') as mock_get:
                # OpenFoodFacts returns None
                mock_off.return_value = None
                
                # NutriFinder returns 404
                mock_response = MagicMock()
                mock_response.status_code = 404
                mock_get.return_value = mock_response
                
                result = get_nutrition_data_dual_source('unknownfood', '1234567890')
                
                assert result is None