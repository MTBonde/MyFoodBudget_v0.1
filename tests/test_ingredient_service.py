"""
Unit tests for ingredient services using pytest, mocks, and AAA pattern.
"""

import pytest
from unittest.mock import patch, MagicMock
from services import create_ingredient, get_all_ingredients, delete_ingredient_service


@patch("services.add_ingredient")
def test_create_ingredient_success(mock_add_ingredient):
    """
    ARRANGE: Valid data.
    ACT: Call create_ingredient.
    ASSERT: Should return created object.
    """
    # Arrange
    test_name = "Flour"
    test_quantity = 1000.0
    test_unit = "g"
    test_price = 10
    mock_ingredient = MagicMock()
    mock_add_ingredient.return_value = mock_ingredient

    # Act
    result = create_ingredient(test_name, test_quantity, test_unit, test_price)

    # Assert
    mock_add_ingredient.assert_called_once_with(test_name, test_quantity, test_unit, test_price)
    assert result == mock_ingredient


@patch("services.add_ingredient")
def test_create_ingredient_failure(mock_add_ingredient):
    """
    ARRANGE: Simulate failure.
    ACT: Call create_ingredient.
    ASSERT: Should return None.
    """
    # Arrange
    test_name = "Salt"
    test_quantity = 5.0
    test_unit = "g"
    test_price = 0.50
    mock_add_ingredient.return_value = None

    # Act
    result = create_ingredient(test_name, test_quantity, test_unit, test_price)

    # Assert
    assert result is None



@patch("services.get_all_ingredients_from_db")
def test_get_all_ingredients_success(mock_get_ingredients):
    """
    ARRANGE: Mock list.
    ACT: Call get_all_ingredients.
    ASSERT: Should return list.
    """
    # Arrange
    ingredient1 = MagicMock(name="Sugar")
    ingredient2 = MagicMock(name="Milk")
    mock_get_ingredients.return_value = [ingredient1, ingredient2]

    # Act
    result = get_all_ingredients()

    # Assert
    mock_get_ingredients.assert_called_once()
    assert result == [ingredient1, ingredient2]


@patch("services.delete_ingredient_from_db")
def test_delete_ingredient_success(mock_delete_ingredient):
    """
    ARRANGE: Valid ID.
    ACT: Call delete_ingredient_service.
    ASSERT: Should return True.
    """
    # Arrange
    ingredient_id = 1
    mock_delete_ingredient.return_value = True

    # Act
    result = delete_ingredient_service(ingredient_id)

    # Assert
    mock_delete_ingredient.assert_called_once_with(ingredient_id)
    assert result is True



@patch("services.delete_ingredient_from_db")
def test_delete_ingredient_failure(mock_delete_ingredient):
    """
    ARRANGE: Invalid ID.
    ACT: Call delete_ingredient_service.
    ASSERT: Should return False.
    """
    # Arrange
    invalid_id = 999
    mock_delete_ingredient.return_value = False

    # Act
    result = delete_ingredient_service(invalid_id)

    # Assert
    mock_delete_ingredient.assert_called_once_with(invalid_id)
    assert result is False



@patch("services.delete_ingredient_from_db")
def test_delete_ingredient_exception(mock_delete_ingredient):
    """
    ARRANGE: Simulate exception.
    ACT: Call delete_ingredient_service.
    ASSERT: Should return False.
    """
    # Arrange
    ingredient_id = 1
    mock_delete_ingredient.side_effect = Exception("DB error")

    # Act
    result = delete_ingredient_service(ingredient_id)

    # Assert
    mock_delete_ingredient.assert_called_once_with(ingredient_id)
    assert result is False

