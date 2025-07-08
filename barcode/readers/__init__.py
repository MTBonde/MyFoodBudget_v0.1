"""
Barcode readers package.

Contains implementations of different barcode/product data sources.
"""

from .base_reader import ProductReader, NutritionReader
from .openfoodfacts_reader import OpenFoodFactsReader
from .nutrifinder_reader import NutriFinderReader

__all__ = [
    'ProductReader', 
    'NutritionReader',
    'OpenFoodFactsReader', 
    'NutriFinderReader'
]