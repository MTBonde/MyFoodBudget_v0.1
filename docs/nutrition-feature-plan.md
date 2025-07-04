# Nutrition Information Feature Implementation Plan

## Overview
This document outlines the comprehensive plan for adding nutrition information tracking to the MyFoodBudget application. The feature will enable users to track nutritional values (calories, protein, carbohydrates, fat, fiber, sugar, sodium) for ingredients and automatically calculate nutrition information for complete recipes.

## Current State Analysis
- **Existing Architecture**: Flask app with SQLAlchemy ORM, Repository pattern, Service layer
- **OpenFoodFacts Integration**: Already implemented for basic product lookup by barcode
- **Database**: SQLite with manual schema management
- **Models**: Ingredient, Recipe, RecipeIngredient, User models established

## Implementation Plan

### 1. Database Schema Changes

#### 1.1 Ingredient Model Extension
Add nutrition fields to the `Ingredient` model (standardized per 100g):
```python
# New fields to add to Ingredient model
calories = db.Column(db.Float, nullable=True)           # kcal per 100g
protein = db.Column(db.Float, nullable=True)            # g per 100g
carbohydrates = db.Column(db.Float, nullable=True)      # g per 100g
fat = db.Column(db.Float, nullable=True)                # g per 100g
fiber = db.Column(db.Float, nullable=True)              # g per 100g
sugar = db.Column(db.Float, nullable=True)              # g per 100g
sodium = db.Column(db.Float, nullable=True)             # mg per 100g
```

#### 1.2 Database Migration
- Update `db_init.py` to include new columns in ingredients table
- Create migration script for existing data
- Handle NULL values appropriately for existing ingredients

#### 1.3 Recipe Nutrition Enhancement
Consider adding computed nutrition fields to Recipe model:
```python
# Optional: Add to Recipe model for caching
total_calories = db.Column(db.Float, nullable=True)
total_protein = db.Column(db.Float, nullable=True)
total_carbohydrates = db.Column(db.Float, nullable=True)
total_fat = db.Column(db.Float, nullable=True)
total_fiber = db.Column(db.Float, nullable=True)
total_sugar = db.Column(db.Float, nullable=True)
total_sodium = db.Column(db.Float, nullable=True)
```

### 2. OpenFoodFacts API Integration Enhancement

#### 2.1 Nutrition Data Extraction
Extend `normalize_openfoodfacts_product()` function to extract:
- Energy values (convert from kJ to kcal: multiply by 0.23900573614)
- Protein, carbohydrates, fat, fiber, sugar per 100g
- Sodium content (handle salt to sodium conversion)

#### 2.2 API Response Handling
```python
def extract_nutrition_from_off_product(product_data):
    """
    Extract nutrition information from OpenFoodFacts product data.
    All values standardized to per 100g basis.
    """
    nutriments = product_data.get('nutriments', {})
    
    # Energy conversion from kJ to kcal
    energy_kj = nutriments.get('energy_100g', 0)
    calories = energy_kj * 0.23900573614 if energy_kj else None
    
    nutrition = {
        'calories': calories,
        'protein': nutriments.get('proteins_100g'),
        'carbohydrates': nutriments.get('carbohydrates_100g'),
        'fat': nutriments.get('fat_100g'),
        'fiber': nutriments.get('fiber_100g'),
        'sugar': nutriments.get('sugars_100g'),
        'sodium': nutriments.get('sodium_100g')  # Already in mg
    }
    
    return nutrition
```

#### 2.3 Error Handling and Fallbacks
- Handle missing nutrition data gracefully
- Provide default values or user input prompts
- Log nutrition data availability for debugging

### 3. Services Layer Enhancement

#### 3.1 Nutrition Calculation Services
Create new service functions:
```python
def calculate_recipe_nutrition(recipe_id):
    """
    Calculate total nutrition for a recipe based on ingredients and quantities.
    Returns nutrition per recipe and per serving.
    """
    
def calculate_ingredient_nutrition_for_quantity(ingredient, quantity, unit):
    """
    Calculate nutrition for specific quantity of ingredient.
    Handle unit conversions properly.
    """
    
def update_ingredient_nutrition(ingredient_id, nutrition_data):
    """
    Update nutrition information for an ingredient.
    """
```

#### 3.2 Unit Conversion Integration
- Extend existing unit conversion utilities
- Handle nutrition calculations across different units
- Maintain consistency with existing Pint library usage

### 4. Repository Layer Updates

#### 4.1 Ingredient Repository Extensions
Update repository functions:
```python
def add_ingredient(name, quantity, quantity_unit, price, barcode=None, brand=None, nutrition=None):
    """Extended to include nutrition data"""
    
def update_ingredient_nutrition(ingredient_id, nutrition_data):
    """Add function to update nutrition information"""
    
def get_ingredients_with_nutrition():
    """Get all ingredients including nutrition data"""
```

#### 4.2 Recipe Repository Extensions
```python
def get_recipe_with_nutrition(recipe_id):
    """Get recipe with calculated nutrition information"""
    
def get_all_recipes_with_nutrition():
    """Get all recipes with nutrition calculations"""
```

### 5. Web Interface Updates

#### 5.1 Ingredient Forms
- Add nutrition fields to ingredient creation form
- Make nutrition fields optional with clear labels
- Auto-populate from OpenFoodFacts when available
- Provide manual entry options

#### 5.2 Recipe Display
- Show nutrition information in recipe view
- Display per-serving nutrition calculations
- Add nutrition summary cards
- Include nutrition in recipe comparison features

#### 5.3 Ingredient Management
- Add nutrition columns to ingredient listings
- Enable nutrition editing for existing ingredients
- Show nutrition completeness indicators

### 6. Testing Strategy

#### 6.1 Unit Tests
Create comprehensive tests for:
- Nutrition calculation algorithms
- OpenFoodFacts nutrition data extraction
- Unit conversion for nutrition values
- Database operations with nutrition data

#### 6.2 Integration Tests
- Test complete workflow from barcode scan to nutrition calculation
- Test recipe nutrition calculation with multiple ingredients
- Test nutrition data persistence and retrieval

#### 6.3 Test Data
- Create test fixtures with known nutrition values
- Mock OpenFoodFacts responses with nutrition data
- Test edge cases (missing data, zero values, unit mismatches)

### 7. Implementation Phases

#### Phase 1: Database and Models (Foundation)
1. Update Ingredient model with nutrition fields
2. Modify database schema (db_init.py)
3. Create migration script for existing data
4. Update repositories to handle nutrition data

#### Phase 2: OpenFoodFacts Integration
1. Extend normalize_openfoodfacts_product function
2. Add nutrition data extraction logic
3. Implement error handling and fallbacks
4. Test API integration thoroughly

#### Phase 3: Nutrition Services
1. Create nutrition calculation services
2. Implement recipe nutrition calculation
3. Add unit conversion support
4. Create nutrition update services

#### Phase 4: Web Interface
1. Update ingredient forms with nutrition fields
2. Add nutrition display to recipes
3. Enhance ingredient management with nutrition
4. Add nutrition-focused UI components

#### Phase 5: Testing and Validation
1. Write comprehensive unit tests
2. Create integration tests
3. Validate nutrition calculations
4. Test user workflows end-to-end

### 8. Data Validation and Quality

#### 8.1 Nutrition Data Validation
- Implement reasonable range checks for nutrition values
- Validate nutrition data consistency
- Handle edge cases (zero values, missing data)

#### 8.2 User Input Validation
- Provide clear validation messages
- Guide users on proper nutrition data entry
- Offer suggestions based on similar ingredients

### 9. Performance Considerations

#### 9.1 Database Performance
- Index nutrition fields if frequently queried
- Consider nutrition data caching strategies
- Optimize recipe nutrition calculation queries

#### 9.2 API Performance
- Cache OpenFoodFacts nutrition responses
- Implement batch nutrition updates
- Handle API rate limiting gracefully

### 10. Future Enhancements

#### 10.1 Advanced Nutrition Features
- Nutrition goals and tracking
- Dietary restriction filtering
- Nutrition-based recipe recommendations
- Integration with fitness apps

#### 10.2 Data Sources
- Support for additional nutrition databases
- User-contributed nutrition data
- Nutrition data verification systems

## Technical Requirements

### Dependencies
- No new major dependencies required
- Leverage existing Flask, SQLAlchemy, and Pint libraries
- Continue using OpenFoodFacts API

### Database Changes
- Backward compatible schema changes
- Graceful handling of missing nutrition data
- Efficient storage of nutrition information

### API Integration
- Robust error handling for OpenFoodFacts API
- Fallback mechanisms for missing data
- Proper rate limiting and caching

## Success Criteria

1. **Functional Requirements Met**
   - Users can view nutrition information for ingredients
   - Recipe nutrition is automatically calculated
   - OpenFoodFacts integration provides nutrition data
   - Manual nutrition entry is available

2. **Technical Requirements Met**
   - Database schema updated without breaking existing functionality
   - All existing tests continue to pass
   - New functionality is thoroughly tested
   - Performance remains acceptable

3. **User Experience**
   - Intuitive nutrition information display
   - Clear indication of data sources
   - Graceful handling of missing data
   - Helpful user guidance for nutrition entry

## Risk Mitigation

### Technical Risks
- **Database Migration**: Test thoroughly with backup data
- **API Changes**: Implement robust error handling
- **Performance Impact**: Monitor and optimize queries

### User Experience Risks
- **Data Overwhelm**: Make nutrition information optional and progressive
- **Accuracy Concerns**: Clearly indicate data sources and limitations
- **Complexity**: Maintain simple, clean interface design

## Documentation Updates

### Code Documentation
- Update all function docstrings
- Add nutrition calculation examples
- Document data sources and assumptions

### User Documentation
- Update CLAUDE.md with nutrition feature information
- Add nutrition data source explanations
- Document manual nutrition entry procedures

---

*This plan provides a comprehensive roadmap for implementing nutrition information tracking in MyFoodBudget while maintaining the existing architecture and ensuring robust, scalable functionality.*