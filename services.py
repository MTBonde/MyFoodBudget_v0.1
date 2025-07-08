from werkzeug.security import check_password_hash
import requests
import logging
from barcode import BarcodeScanner
from exceptions import (
    AuthenticationError,
    ValidationError,
    DatabaseError,
    ServiceError,
    DuplicateResourceError,
    ResourceNotFoundError,
    ExternalServiceError
)
from logging_config import get_logger
from repositories import (
    create_user,
    find_by_username,
    add_ingredient,
    add_recipe,
    add_recipe_ingredient,
    get_all_ingredients_from_db,
    get_all_recipes_from_db,
    get_all_recipes_with_ingredients_from_db, 
    get_recipe_with_ingredients_from_db,
    delete_recipe_from_db, 
    delete_ingredient_from_db,
    find_ingredient_by_barcode,
    barcode_exists
)

# Get logger for this module
logger = get_logger('services')

def authenticate_user(username, password):
    """
    Authenticate a user with username and password.
    
    Args:
        username (str): Username to authenticate
        password (str): Password to verify
        
    Returns:
        User: User object if authentication successful
        
    Raises:
        ValidationError: If username or password is empty
        AuthenticationError: If credentials are invalid
        DatabaseError: If database operation fails
    """
    if not username or not password:
        raise ValidationError("Username and password are required")
    
    try:
        user = find_by_username(username)
        if user and check_password_hash(user.hash, password):
            logger.info(f"User {username} authenticated successfully")
            return user
        else:
            logger.warning(f"Authentication failed for user {username}")
            raise AuthenticationError("Invalid username or password", username=username)
            
    except AuthenticationError:
        # Re-raise authentication errors
        raise
    except Exception as e:
        logger.error(f"Database error during authentication for user {username}: {e}")
        raise DatabaseError("Authentication failed due to database error", operation="authenticate_user")

def register_user(username, email, password):
    """
    Register a new user account.
    
    Args:
        username (str): Username for the new account
        email (str): Email address for the new account
        password (str): Password for the new account
        
    Returns:
        User: Created user object
        
    Raises:
        ValidationError: If required fields are missing or invalid
        DuplicateResourceError: If username already exists
        DatabaseError: If database operation fails
    """
    # Input validation
    if not username or not email or not password:
        raise ValidationError("Username, email, and password are required")
        
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters long", field="username")
        
    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters long", field="password")
    
    try:
        # Check if username already exists
        if find_by_username(username) is not None:
            raise DuplicateResourceError(
                f"Username '{username}' already exists",
                resource_type="user",
                identifier=username
            )
        
        # Create the user
        user = create_user(username, email, password)
        if user is None:
            raise DatabaseError("Failed to create user account", operation="create_user")
            
        logger.info(f"User {username} registered successfully")
        return user
        
    except (ValidationError, DuplicateResourceError):
        # Re-raise validation and duplicate errors
        raise
    except Exception as e:
        logger.error(f"Database error during user registration for {username}: {e}")
        raise DatabaseError("Registration failed due to database error", operation="register_user")

def create_ingredient(name, quantity, quantity_unit, price, barcode=None, brand=None):
    """
    Create a new ingredient with nutrition data.
    
    Args:
        name (str): Name of the ingredient
        quantity (float): Quantity of the ingredient
        quantity_unit (str): Unit of the quantity
        price (float): Price of the ingredient
        barcode (str, optional): Barcode of the ingredient
        brand (str, optional): Brand of the ingredient
        
    Returns:
        Ingredient: Created ingredient object
        
    Raises:
        ValidationError: If required fields are missing or invalid
        DuplicateResourceError: If barcode already exists
        DatabaseError: If database operation fails
        ExternalServiceError: If nutrition data lookup fails
    """
    # Input validation
    if not name or not quantity_unit:
        raise ValidationError("Name and quantity unit are required")
        
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than 0", field="quantity", value=str(quantity))
        
    if price < 0:
        raise ValidationError("Price cannot be negative", field="price", value=str(price))
    
    # Check if barcode already exists
    if barcode and check_barcode_exists(barcode):
        raise DuplicateResourceError(
            f"Ingredient with barcode '{barcode}' already exists",
            resource_type="ingredient",
            identifier=barcode
        )
    
    try:
        # Fetch nutrition data using new barcode scanner
        scanner = BarcodeScanner()
        nutrition = scanner.get_nutrition_data(barcode=barcode, name=name)
        
        # Create ingredient with nutrition data
        ingredient = add_ingredient(name, quantity, quantity_unit, price, barcode, brand, nutrition)
        
        if ingredient is None:
            raise DatabaseError("Failed to create ingredient", operation="add_ingredient")
            
        logger.info(f"Ingredient '{name}' created successfully")
        return ingredient
        
    except (ValidationError, DuplicateResourceError):
        # Re-raise validation and duplicate errors
        raise
    except Exception as e:
        logger.error(f"Error creating ingredient '{name}': {e}")
        raise ServiceError(f"Failed to create ingredient '{name}'", service="ingredient_service", operation="create_ingredient")

def create_recipe(name, instructions, ingredients):
    """
    Create a new recipe with ingredients.
    
    Args:
        name (str): Name of the recipe
        instructions (str): Recipe instructions
        ingredients (list): List of ingredient dictionaries
        
    Returns:
        Recipe: Created recipe object
        
    Raises:
        ValidationError: If required fields are missing or invalid
        DatabaseError: If database operation fails
        ServiceError: If recipe creation fails
    """
    # Input validation
    if not name or not instructions:
        raise ValidationError("Recipe name and instructions are required")
        
    if not ingredients or len(ingredients) == 0:
        raise ValidationError("Recipe must contain at least one ingredient")
    
    # Validate ingredients
    for i, ing in enumerate(ingredients):
        if not all(key in ing for key in ['id', 'quantity_used', 'quantity_purchased', 'price']):
            raise ValidationError(f"Ingredient {i+1} is missing required fields")
            
        if ing['quantity_used'] <= 0:
            raise ValidationError(f"Ingredient {i+1} quantity used must be greater than 0")
            
        if ing['quantity_purchased'] <= 0:
            raise ValidationError(f"Ingredient {i+1} quantity purchased must be greater than 0")
    
    try:
        # Compute total recipe cost using the cost formula:
        # For each ingredient: cost = (quantity_used / quantity_purchased) * price
        total_price = sum(
            (ing['quantity_used'] / ing['quantity_purchased']) * ing['price']
            for ing in ingredients if ing['quantity_purchased'] > 0
        )
        
        # Create the recipe
        recipe = add_recipe(name, instructions, total_price)
        if recipe is None:
            raise DatabaseError("Failed to create recipe", operation="add_recipe")
        
        # Add ingredients to the recipe
        for ing in ingredients:
            if not add_recipe_ingredient(recipe.id, ing['id'], ing['quantity_used'], ing['quantity_unit']):
                # Clean up by deleting the recipe if ingredient addition fails
                try:
                    delete_recipe_from_db(recipe.id)
                except:
                    pass
                raise DatabaseError("Failed to add ingredient to recipe", operation="add_recipe_ingredient")
        
        logger.info(f"Recipe '{name}' created successfully with {len(ingredients)} ingredients")
        return recipe
        
    except (ValidationError, DatabaseError):
        # Re-raise validation and database errors
        raise
    except Exception as e:
        logger.error(f"Error creating recipe '{name}': {e}")
        raise ServiceError(f"Failed to create recipe '{name}'", service="recipe_service", operation="create_recipe")

def get_all_ingredients():
    """
    Retrieve all ingredients from the database.
    
    Returns:
        list: List of ingredient objects
        
    Raises:
        DatabaseError: If database operation fails
    """
    try:
        ingredients = get_all_ingredients_from_db()
        logger.debug(f"Retrieved {len(ingredients)} ingredients from database")
        return ingredients
    except Exception as e:
        logger.error(f"Error retrieving ingredients: {e}")
        raise DatabaseError("Failed to retrieve ingredients", operation="get_all_ingredients")

def get_all_recipes():
    """
    Retrieve all recipes from the database.
    
    Returns:
        list: List of recipe objects
        
    Raises:
        DatabaseError: If database operation fails
    """
    try:
        recipes = get_all_recipes_from_db()
        logger.debug(f"Retrieved {len(recipes)} recipes from database")
        return recipes
    except Exception as e:
        logger.error(f"Error retrieving recipes: {e}")
        raise DatabaseError("Failed to retrieve recipes", operation="get_all_recipes")

def get_all_recipes_with_ingredients():
    """
    Retrieve all recipes with their ingredients from the database.
    
    Returns:
        list: List of recipe objects with ingredients
        
    Raises:
        DatabaseError: If database operation fails
    """
    try:
        recipes = get_all_recipes_with_ingredients_from_db()
        logger.debug(f"Retrieved {len(recipes)} recipes with ingredients from database")
        return recipes
    except Exception as e:
        logger.error(f"Error retrieving recipes with ingredients: {e}")
        raise DatabaseError("Failed to retrieve recipes with ingredients", operation="get_all_recipes_with_ingredients")

def delete_recipe_service(recipe_id):
    """
    Delete a recipe from the database.
    
    Args:
        recipe_id (int): ID of the recipe to delete
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        ValidationError: If recipe_id is invalid
        ResourceNotFoundError: If recipe doesn't exist
        DatabaseError: If database operation fails
    """
    if not recipe_id or recipe_id <= 0:
        raise ValidationError("Recipe ID must be a positive integer", field="recipe_id")
    
    try:
        # Check if recipe exists first
        recipe = get_recipe_with_ingredients_from_db(recipe_id)
        if not recipe:
            raise ResourceNotFoundError(
                f"Recipe with ID {recipe_id} not found",
                resource_type="recipe",
                resource_id=str(recipe_id)
            )
        
        # Delete the recipe
        success = delete_recipe_from_db(recipe_id)
        if not success:
            raise DatabaseError("Failed to delete recipe", operation="delete_recipe")
            
        logger.info(f"Recipe with ID {recipe_id} deleted successfully")
        return True
        
    except (ValidationError, ResourceNotFoundError, DatabaseError):
        # Re-raise specific errors
        raise
    except Exception as e:
        logger.error(f"Error deleting recipe {recipe_id}: {e}")
        raise DatabaseError("Failed to delete recipe", operation="delete_recipe_service")

def delete_ingredient_service(ingredient_id):
    """
    Delete an ingredient from the database.
    
    Args:
        ingredient_id (int): ID of the ingredient to delete
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        ValidationError: If ingredient_id is invalid
        ResourceNotFoundError: If ingredient doesn't exist
        DatabaseError: If database operation fails
    """
    if not ingredient_id or ingredient_id <= 0:
        raise ValidationError("Ingredient ID must be a positive integer", field="ingredient_id")
    
    try:
        # Delete the ingredient
        success = delete_ingredient_from_db(ingredient_id)
        if not success:
            raise ResourceNotFoundError(
                f"Ingredient with ID {ingredient_id} not found",
                resource_type="ingredient",
                resource_id=str(ingredient_id)
            )
            
        logger.info(f"Ingredient with ID {ingredient_id} deleted successfully")
        return True
        
    except (ValidationError, ResourceNotFoundError):
        # Re-raise specific errors
        raise
    except Exception as e:
        logger.error(f"Error deleting ingredient {ingredient_id}: {e}")
        raise DatabaseError("Failed to delete ingredient", operation="delete_ingredient_service")


def fetch_product_from_openfoodfacts(barcode):
    """
    Legacy function - replaced by barcode module.
    Fetches product information from OpenFoodFacts API by barcode.
    
    Args:
        barcode (str): The barcode to look up.
    Returns:
        dict: Product information if found, None otherwise.
    """
    from barcode.readers import OpenFoodFactsReader
    reader = OpenFoodFactsReader()
    try:
        return reader.lookup_by_barcode(barcode)
    except Exception as e:
        logging.error(f"Error in legacy fetch_product_from_openfoodfacts: {e}")
        return None


def normalize_openfoodfacts_product(product_data):
    """
    Legacy function - replaced by barcode module.
    Normalizes OpenFoodFacts product data to our application format.
    Args:
        product_data (dict): Raw product data from OpenFoodFacts API.
    Returns:
        dict: Normalized product information.
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
    quantity, quantity_unit = parse_quantity_from_text(quantity_text)
    
    # Extract barcode (code field)
    barcode = product_data.get('code')
    
    return {
        'name': name.strip(),
        'brand': brand.strip() if brand else None,
        'quantity': quantity,
        'quantity_unit': quantity_unit,
        'barcode': barcode,
        'price': 0.0,  # Price needs to be entered by user
        'raw_data': product_data  # Keep raw data for debugging
    }


def parse_quantity_from_text(quantity_text):
    """
    Parses quantity and unit from OpenFoodFacts quantity text.
    Args:
        quantity_text (str): Quantity text like "500g", "1L", "250ml"
    Returns:
        tuple: (quantity, unit) where quantity is float and unit is string
    """
    import re
    
    if not quantity_text:
        return 1.0, 'unit'
    
    # Try to extract number and unit using regex
    match = re.search(r'(\d+(?:\.\d+)?)\s*([a-zA-Z\s]+)', quantity_text)
    
    if match:
        quantity = float(match.group(1))
        unit = match.group(2).lower()
        
        # Normalize common units
        unit_mapping = {
            'g': 'g',
            'kg': 'kg',
            'l': 'l',
            'ml': 'ml',
            'cl': 'cl',
            'oz': 'oz',
            'lb': 'lb',
            'fl oz': 'fl oz'
        }
        
        unit = unit_mapping.get(unit, unit)
        return quantity, unit
    
    # If no pattern matches, return default
    return 1.0, 'unit'


# Simple in-memory cache for API results
_barcode_cache = {}

def lookup_product_by_barcode(barcode):
    """
    Looks up a product by barcode, first checking local database, then using barcode scanner.
    Uses caching to avoid duplicate API calls.
    
    Args:
        barcode (str): The barcode to look up.
        
    Returns:
        dict: Product information with 'source' field indicating 'local' or 'api'
        
    Raises:
        ValidationError: If barcode is invalid
        ExternalServiceError: If API lookup fails
        DatabaseError: If database operation fails
    """
    if not barcode or len(barcode.strip()) == 0:
        raise ValidationError("Barcode cannot be empty", field="barcode")
    
    # First check if we have this barcode in our local database
    try:
        local_ingredient = find_ingredient_by_barcode(barcode)
        if local_ingredient:
            logger.debug(f"Found local ingredient for barcode {barcode}")
            return {
                'source': 'local',
                'name': local_ingredient.name,
                'brand': local_ingredient.brand,
                'quantity': local_ingredient.quantity,
                'quantity_unit': local_ingredient.quantity_unit,
                'price': local_ingredient.price,
                'barcode': local_ingredient.barcode
            }
    except Exception as e:
        logger.error(f"Error checking local ingredient by barcode: {e}")
        raise DatabaseError("Failed to check local ingredient database", operation="find_ingredient_by_barcode")
    
    # Check cache first to avoid duplicate API calls
    if barcode in _barcode_cache:
        logger.debug(f"Found cached result for barcode {barcode}")
        return _barcode_cache[barcode]
    
    try:
        # If not found locally or in cache, try barcode scanner
        scanner = BarcodeScanner()
        api_product = scanner.lookup_product(barcode=barcode)
        if api_product:
            api_product['source'] = 'api'
            logger.info(f"Successfully looked up product for barcode {barcode} via API")
        else:
            logger.info(f"No product found for barcode {barcode}")
        
        # Cache the result (even if None) to avoid repeated API calls
        _barcode_cache[barcode] = api_product
        
        return api_product
        
    except Exception as e:
        logger.error(f"Error looking up product by barcode {barcode}: {e}")
        raise ExternalServiceError("Failed to lookup product by barcode", "barcode_scanner")


def check_barcode_exists(barcode):
    """
    Checks if a barcode already exists in the local database.
    
    Args:
        barcode (str): The barcode to check.
        
    Returns:
        bool: True if barcode exists, False otherwise.
        
    Raises:
        ValidationError: If barcode is invalid
        DatabaseError: If database operation fails
    """
    if not barcode or len(barcode.strip()) == 0:
        raise ValidationError("Barcode cannot be empty", field="barcode")
    
    try:
        exists = barcode_exists(barcode)
        logger.debug(f"Barcode {barcode} existence check: {exists}")
        return exists
    except Exception as e:
        logger.error(f"Error checking barcode existence: {e}")
        raise DatabaseError("Failed to check barcode existence", operation="check_barcode_exists")


def fetch_nutrition_from_nutrifinder(food_item_name):
    """
    Legacy function - replaced by barcode module.
    Fetch nutrition information from NutriFinder API for simple ingredients.
    Returns nutrition data per 100g basis.
    Args:
        food_item_name (str): Name of the food item to look up.
    Returns:
        dict: Nutrition data if found, None otherwise.
    """
    import re
    
    # Validate input (1-32 characters, English letters only)
    if not re.match(r'^[a-åA-Å]{1,32}$', food_item_name):
        logging.warning(f"Invalid food item name for NutriFinder: {food_item_name}")
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
                'fiber': data.get('fiber')
            }
            
            logging.info(f"Successfully fetched nutrition data for {food_item_name} from NutriFinder")
            return nutrition
        elif response.status_code == 404:
            logging.info(f"Food item not found in NutriFinder: {food_item_name}")
            return None
        else:
            logging.warning(f"NutriFinder API returned status {response.status_code} for {food_item_name}")
            return None
            
    except requests.RequestException as e:
        logging.error(f"Error fetching nutrition from NutriFinder: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error in fetch_nutrition_from_nutrifinder: {e}")
        return None


def extract_nutrition_from_off_product(product_data):
    """
    Legacy function - replaced by barcode module.
    Extract nutrition information from OpenFoodFacts product data.
    All values standardized to per 100g basis.
    Args:
        product_data (dict): Raw product data from OpenFoodFacts API.
    Returns:
        dict: Nutrition data if found, None otherwise.
    """
    try:
        nutriments = product_data.get('nutriments', {})
        
        if not nutriments:
            logging.info("No nutriments data found in OpenFoodFacts product")
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
            logging.info(f"Successfully extracted nutrition data from OpenFoodFacts: {list(valid_nutrition.keys())}")
            return nutrition
        else:
            logging.info("No valid nutrition data found in OpenFoodFacts product")
            return None
            
    except Exception as e:
        logging.error(f"Error extracting nutrition from OpenFoodFacts product: {e}")
        return None


def get_nutrition_data_dual_source(ingredient_name, barcode=None):
    """
    Legacy function - replaced by barcode module.
    Get nutrition data using dual-source strategy.
    Priority: OpenFoodFacts (if barcode) -> NutriFinder -> Manual entry
    Args:
        ingredient_name (str): Name of the ingredient.
        barcode (str, optional): Barcode of the ingredient.
    Returns:
        dict: Nutrition data if found, None if both sources fail.
    """
    scanner = BarcodeScanner()
    return scanner.get_nutrition_data(barcode=barcode, name=ingredient_name)


def calculate_recipe_nutrition(recipe_id):
    """
    Calculate total nutrition for a recipe based on ingredients and quantities.
    Returns nutrition per recipe and per serving.
    
    Args:
        recipe_id (int): ID of the recipe to calculate nutrition for.
        
    Returns:
        dict: Nutrition data with total and per-serving values
        
    Raises:
        ValidationError: If recipe_id is invalid
        ResourceNotFoundError: If recipe doesn't exist
        ServiceError: If calculation fails
    """
    if not recipe_id or recipe_id <= 0:
        raise ValidationError("Recipe ID must be a positive integer", field="recipe_id")
    
    try:
        recipe = get_recipe_with_ingredients_from_db(recipe_id)
        if not recipe:
            raise ResourceNotFoundError(
                f"Recipe with ID {recipe_id} not found",
                resource_type="recipe",
                resource_id=str(recipe_id)
            )
        
        # Initialize totals
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'carbohydrates': 0,
            'fat': 0,
            'fiber': 0
        }
        
        # Track ingredients with missing nutrition data
        ingredients_with_nutrition = 0
        total_ingredients = len(recipe.recipe_ingredients)
        
        # Calculate nutrition for each ingredient
        for recipe_ingredient in recipe.recipe_ingredients:
            ingredient = recipe_ingredient.ingredient
            quantity_used = recipe_ingredient.quantity
            quantity_unit = recipe_ingredient.quantity_unit
            
            # Only process if ingredient has nutrition data
            if ingredient.calories is not None or ingredient.protein is not None:
                ingredients_with_nutrition += 1
                
                # Convert quantity to calculate actual nutrition values
                # All nutrition is stored per 100g basis
                nutrition_factor = calculate_nutrition_factor(
                    quantity_used, 
                    quantity_unit, 
                    ingredient.quantity, 
                    ingredient.quantity_unit
                )
                
                # Add to totals (handle None values)
                total_nutrition['calories'] += (ingredient.calories or 0) * nutrition_factor
                total_nutrition['protein'] += (ingredient.protein or 0) * nutrition_factor
                total_nutrition['carbohydrates'] += (ingredient.carbohydrates or 0) * nutrition_factor
                total_nutrition['fat'] += (ingredient.fat or 0) * nutrition_factor
                total_nutrition['fiber'] += (ingredient.fiber or 0) * nutrition_factor
        
        # Round values to 2 decimal places
        for key in total_nutrition:
            total_nutrition[key] = round(total_nutrition[key], 2)
        
        # Calculate per serving (assuming 4 servings by default)
        servings = 4
        per_serving_nutrition = {
            key: round(value / servings, 2) for key, value in total_nutrition.items()
        }
        
        result = {
            'total': total_nutrition,
            'per_serving': per_serving_nutrition,
            'servings': servings,
            'ingredients_with_nutrition': ingredients_with_nutrition,
            'total_ingredients': total_ingredients,
            'nutrition_completeness': (ingredients_with_nutrition / total_ingredients) * 100 if total_ingredients > 0 else 0
        }
        
        logger.debug(f"Successfully calculated nutrition for recipe {recipe_id}")
        return result
        
    except (ValidationError, ResourceNotFoundError):
        # Re-raise specific errors
        raise
    except Exception as e:
        logger.error(f"Error calculating recipe nutrition: {e}")
        raise ServiceError("Failed to calculate recipe nutrition", service="nutrition_service", operation="calculate_recipe_nutrition")


def calculate_nutrition_factor(quantity_used, quantity_unit, ingredient_quantity, ingredient_unit):
    """
    Calculate the nutrition factor for converting from per 100g basis to actual quantity used.
    Args:
        quantity_used (float): Amount used in recipe
        quantity_unit (str): Unit of amount used
        ingredient_quantity (float): Total quantity of ingredient purchased
        ingredient_unit (str): Unit of ingredient purchased
    Returns:
        float: Factor to multiply nutrition values by
    """
    try:
        # Convert both quantities to grams for calculation
        # This is a simplified conversion - in production, you might want to use Pint library
        
        def convert_to_grams(quantity, unit):
            """Convert quantity to grams"""
            unit = unit.lower()
            if unit in ['g', 'gram', 'grams']:
                return quantity
            elif unit in ['kg', 'kilogram', 'kilograms']:
                return quantity * 1000
            elif unit in ['ml', 'milliliter', 'milliliters']:
                return quantity  # Assume 1ml = 1g for simplicity
            elif unit in ['l', 'liter', 'liters']:
                return quantity * 1000
            elif unit in ['cup', 'cups']:
                return quantity * 250  # Approximate
            elif unit in ['tbsp', 'tablespoon', 'tablespoons']:
                return quantity * 15
            elif unit in ['tsp', 'teaspoon', 'teaspoons']:
                return quantity * 5
            else:
                # Default assumption: treat as grams
                return quantity
        
        used_grams = convert_to_grams(quantity_used, quantity_unit)
        
        # Calculate factor: (grams used / 100g) since nutrition is per 100g
        factor = used_grams / 100
        
        return factor
        
    except Exception as e:
        logging.error(f"Error calculating nutrition factor: {e}")
        # Return safe default
        return 0.01  # 1g worth of nutrition


def get_recipe_with_nutrition(recipe_id):
    """
    Get recipe with calculated nutrition information.
    
    Args:
        recipe_id (int): ID of the recipe.
        
    Returns:
        dict: Recipe data with nutrition information.
        
    Raises:
        ValidationError: If recipe_id is invalid
        ResourceNotFoundError: If recipe doesn't exist
        ServiceError: If nutrition calculation fails
    """
    if not recipe_id or recipe_id <= 0:
        raise ValidationError("Recipe ID must be a positive integer", field="recipe_id")
    
    try:
        recipe = get_recipe_with_ingredients_from_db(recipe_id)
        if not recipe:
            raise ResourceNotFoundError(
                f"Recipe with ID {recipe_id} not found",
                resource_type="recipe",
                resource_id=str(recipe_id)
            )
        
        # Calculate nutrition
        nutrition = calculate_recipe_nutrition(recipe_id)
        
        # Convert recipe to dictionary format
        recipe_data = {
            'id': recipe.id,
            'name': recipe.name,
            'instructions': recipe.instructions,
            'total_price': recipe.total_price,
            'ingredients': [
                {
                    'name': ri.ingredient.name,
                    'quantity': ri.quantity,
                    'unit': ri.quantity_unit,
                    'nutrition': {
                        'calories': ri.ingredient.calories,
                        'protein': ri.ingredient.protein,
                        'carbohydrates': ri.ingredient.carbohydrates,
                        'fat': ri.ingredient.fat,
                        'fiber': ri.ingredient.fiber
                    }
                }
                for ri in recipe.recipe_ingredients
            ],
            'nutrition': nutrition
        }
        
        logger.debug(f"Successfully retrieved recipe {recipe_id} with nutrition")
        return recipe_data
        
    except (ValidationError, ResourceNotFoundError):
        # Re-raise specific errors
        raise
    except Exception as e:
        logger.error(f"Error getting recipe with nutrition: {e}")
        raise ServiceError("Failed to get recipe with nutrition", service="recipe_service", operation="get_recipe_with_nutrition")
