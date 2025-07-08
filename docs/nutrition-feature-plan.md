# Nutrition Information Feature Implementation Plan

## Overview
This document outlines the plan for adding nutrition information tracking to the MyFoodBudget application. The feature will enable users to track nutritional values for ingredients using dual-source API integration (OpenFoodFacts + NutriFinder).

**APPROACH**: Start with a simple MVP to get core dual-source nutrition functionality working, then enhance incrementally.

## Current State Analysis (Updated: 2025-07-08)

### ✅ **COMPLETED - Barcode Branch Implementation**
- **Existing Architecture**: Flask app with SQLAlchemy ORM, Repository pattern, Service layer
- **OpenFoodFacts Integration**: ✅ **IMPLEMENTED** - Basic product lookup by barcode with caching
- **Database**: SQLite with manual schema management
- **Models**: Ingredient, Recipe, RecipeIngredient, User models established
- **Barcode Support**: ✅ **IMPLEMENTED** - Barcode and brand fields added to Ingredient model
- **Product Lookup**: ✅ **IMPLEMENTED** - Full OpenFoodFacts API integration for product data
- **Web Interface**: ✅ **IMPLEMENTED** - Barcode scanning UI with form pre-population

### ❌ **NOT IMPLEMENTED - Nutrition Features**
- **Nutrition Database Schema**: Missing nutrition fields in Ingredient model
- **Nutrition Data Extraction**: OpenFoodFacts integration does not extract nutrition data
- **Nutrition Calculations**: No nutrition calculation services implemented
- **Nutrition UI**: No nutrition display or input in web interface
- **Nutrition Testing**: No nutrition-related tests implemented

### **Foundation Ready for Nutrition Extension**
The barcode branch provides a solid foundation with:
- Working OpenFoodFacts API integration (`services.py`)
- Barcode scanning functionality (`routes.py`, `templates/add_ingredient.html`)
- Product data normalization (`normalize_openfoodfacts_product()`)
- Repository pattern ready for nutrition data (`repositories.py`)
- Database schema extensible for nutrition fields (`models.py`)

## 🎯 **MVP TARGET: Simple Dual-Source Nutrition**

### **MVP Scope** (Implement First)
1. ✅ Basic nutrition fields in Ingredient model
2. ✅ NutriFinder API integration for simple ingredients
3. ✅ Enhanced OpenFoodFacts to extract nutrition data
4. ✅ Simple nutrition display in ingredient forms
5. ✅ Basic dual-source selection logic

### **MVP Exclusions** (Future Phases)
- ❌ Recipe nutrition calculations
- ❌ Advanced data quality features
- ❌ Complex caching strategies
- ❌ Nutrition editing interfaces
- ❌ Advanced error handling

---

## Implementation Plan

### 1. **MVP Phase 1: Database Schema Changes**

#### 1.1 Ingredient Model Extension (MVP - Core Fields Only)
Add **essential** nutrition fields to the `Ingredient` model:
```python
# MVP: Add only core nutrition fields to Ingredient model
calories = db.Column(db.Float, nullable=True)           # kcal per 100g
protein = db.Column(db.Float, nullable=True)            # g per 100g
carbohydrates = db.Column(db.Float, nullable=True)      # g per 100g
fat = db.Column(db.Float, nullable=True)                # g per 100g
fiber = db.Column(db.Float, nullable=True)              # g per 100g
# MVP: Skip sugar/sodium for now - can add later
```

#### 1.2 Database Migration (MVP - Simple)
- Update `db_init.py` to include new nutrition columns
- All fields nullable (existing ingredients will have NULL nutrition)
- No complex migration script needed for MVP

#### 1.3 Recipe Nutrition Enhancement (SKIP FOR MVP)
**Future Phase**: Recipe nutrition calculations come after basic ingredient nutrition works

### 2. **MVP Phase 2: Dual-Source API Integration**

#### 2.1 MVP: Simple NutriFinder Integration (IMPLEMENT FIRST)
**STATUS**: ❌ **NOT IMPLEMENTED** - New integration required
**USE CASE**: Simple ingredients without barcodes (e.g., "tomato", "egg", "apple")

**MVP Implementation**:
```python
def fetch_nutrition_from_nutrifinder(ingredient_name):
    """MVP: Simple NutriFinder API call"""
    try:
        url = f"https://api.mtbonde.dev/api/nutrition?foodItemName={ingredient_name}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'calories': data.get('kcal'),
                'protein': data.get('protein'),
                'carbohydrates': data.get('carb'),
                'fat': data.get('fat'),
                'fiber': data.get('fiber')
            }
    except:
        return None
```

#### 2.2 MVP: Enhanced OpenFoodFacts (IMPLEMENT SECOND)
**STATUS**: ❌ **NOT IMPLEMENTED** - Extend existing `normalize_openfoodfacts_product()`
**USE CASE**: Branded products with barcodes (e.g., "Lurpak Butter")

**MVP Enhancement**:
```python
def extract_nutrition_from_off_product(product_data):
    """MVP: Extract basic nutrition from OpenFoodFacts"""
    nutriments = product_data.get('nutriments', {})
    return {
        'calories': nutriments.get('energy-kcal_100g') or nutriments.get('energy_100g', 0) * 0.239,
        'protein': nutriments.get('proteins_100g'),
        'carbohydrates': nutriments.get('carbohydrates_100g'), 
        'fat': nutriments.get('fat_100g'),
        'fiber': nutriments.get('fiber_100g')
    }
```

#### 2.3 MVP: Simple Dual-Source Logic
**PRIORITY LOGIC** (Simple):
1. **Has Barcode**: Try OpenFoodFacts first
2. **No Barcode OR OpenFoodFacts failed**: Try NutriFinder
3. **Both Failed**: Store ingredient without nutrition (user can add manually later)

```python
def get_nutrition_data_simple(ingredient_name, barcode=None):
    """MVP: Simple dual-source nutrition lookup"""
    nutrition = None
    
    # Try OpenFoodFacts if barcode exists
    if barcode:
        product_data = fetch_product_from_openfoodfacts(barcode)
        if product_data:
            nutrition = extract_nutrition_from_off_product(product_data)
    
    # Fallback to NutriFinder
    if not nutrition:
        nutrition = fetch_nutrition_from_nutrifinder(ingredient_name)
    
    return nutrition  # Can be None - that's OK for MVP
```

#### 2.4 API Response Handling Implementation

**OpenFoodFacts Nutrition Extraction**:
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

**NutriFinder API Integration**:
```python
def fetch_nutrition_from_nutrifinder(food_item_name):
    """
    Fetch nutrition information from NutriFinder API for simple ingredients.
    Returns nutrition data per 100g basis.
    """
    import requests
    import re
    
    # Validate input (1-32 characters, English letters only)
    if not re.match(r'^[a-åA-Å]{1,32}$', food_item_name):
        return None
    
    try:
        url = f"https://api.mtbonde.dev/api/nutrition?foodItemName={food_item_name}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Map NutriFinder response to our format
            nutrition = {
                'calories': data.get('kcal'),
                'protein': data.get('protein'),
                'carbohydrates': data.get('carb'),
                'fat': data.get('fat'),
                'fiber': data.get('fiber'),
                'sugar': None,  # Not provided by NutriFinder
                'sodium': None  # Not provided by NutriFinder
            }
            
            return nutrition
        elif response.status_code == 404:
            return None  # Food item not found
        else:
            return None  # Other errors
            
    except requests.RequestException:
        return None  # Network/timeout errors

def get_nutrition_data_dual_source(ingredient_name, barcode=None):
    """
    Get nutrition data using dual-source strategy.
    Priority: OpenFoodFacts (if barcode) -> NutriFinder -> Manual entry
    """
    nutrition = None
    
    # Try OpenFoodFacts first if barcode exists
    if barcode:
        product_data = fetch_product_from_openfoodfacts(barcode)
        if product_data:
            nutrition = extract_nutrition_from_off_product(product_data)
    
    # Fallback to NutriFinder for simple ingredients
    if not nutrition:
        nutrition = fetch_nutrition_from_nutrifinder(ingredient_name)
    
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
- **NutriFinder API integration and response handling**
- **Dual-source nutrition data strategy**
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

#### ✅ **Phase 0: Foundation (COMPLETED)**
1. ✅ Basic OpenFoodFacts API integration (`services.py`)
2. ✅ Barcode scanning functionality (`routes.py`, `templates/add_ingredient.html`)
3. ✅ Product data normalization (`normalize_openfoodfacts_product()`)
4. ✅ Repository pattern ready for extension (`repositories.py`)
5. ✅ Database schema extensible (`models.py`)

#### 🎯 **MVP Phase 1: Database Schema (SIMPLE)**
1. ❌ Add 5 core nutrition fields to Ingredient model
2. ❌ Update `db_init.py` with new columns
3. ❌ Update `add_ingredient()` in repositories to accept nutrition data

#### 🎯 **MVP Phase 2: API Integration (DUAL-SOURCE)**
1. ❌ Add `fetch_nutrition_from_nutrifinder()` function
2. ❌ Add `extract_nutrition_from_off_product()` function  
3. ❌ Add `get_nutrition_data_simple()` dual-source function
4. ❌ Update ingredient creation to use nutrition APIs

#### 🎯 **MVP Phase 3: Basic UI (DISPLAY ONLY)**
1. ❌ Show nutrition data in ingredient forms
2. ❌ Display nutrition in ingredient listings
3. ❌ Add simple nutrition display template

#### 🎯 **MVP Phase 4: Testing (BASIC)**
1. ❌ Test NutriFinder API integration
2. ❌ Test OpenFoodFacts nutrition extraction
3. ❌ Test dual-source logic

---

#### 🚀 **FUTURE PHASES** (Post-MVP)
- **Phase 5**: Recipe nutrition calculations
- **Phase 6**: Advanced data quality features  
- **Phase 7**: Nutrition editing interfaces
- **Phase 8**: Performance optimizations

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