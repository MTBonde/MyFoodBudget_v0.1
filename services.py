from werkzeug.security import check_password_hash
import requests
import logging
from repositories import (
    create_user,
    find_by_username,
    add_ingredient,
    add_recipe,
    add_recipe_ingredient,
    get_all_ingredients_from_db,
    get_all_recipes_from_db,
    get_all_recipes_with_ingredients_from_db, 
    delete_recipe_from_db, 
    delete_ingredient_from_db,
    find_ingredient_by_barcode,
    barcode_exists
)

def authenticate_user(username, password):
    user = find_by_username(username)
    if user and check_password_hash(user.hash, password):
        return user
    return None

def register_user(username, email, password):
    if find_by_username(username) is not None:
        return False
    user = create_user(username, email, password)
    return user is not None

def create_ingredient(name, quantity, quantity_unit, price, barcode=None, brand=None):
    return add_ingredient(name, quantity, quantity_unit, price, barcode, brand)

def create_recipe(name, instructions, ingredients):
    # Compute total recipe cost using the cost formula:
    # For each ingredient: cost = (quantity_used / quantity_purchased) * price
    total_price = sum(
        (ing['quantity_used'] / ing['quantity_purchased']) * ing['price']
        for ing in ingredients if ing['quantity_purchased'] > 0
    )
    recipe = add_recipe(name, instructions, total_price)
    if recipe:
        for ing in ingredients:
            # Save the ingredient usage in the recipe; note that we pass the used amount.
            if not add_recipe_ingredient(recipe.id, ing['id'], ing['quantity_used'], ing['quantity_unit']):
                return None
        return recipe
    else:
        return None

def get_all_ingredients():
    return get_all_ingredients_from_db()

def get_all_recipes():
    return get_all_recipes_from_db()

def get_all_recipes_with_ingredients():
    return get_all_recipes_with_ingredients_from_db()

def delete_recipe_service(recipe_id):
    try:
        return delete_recipe_from_db(recipe_id)
    except Exception as e:
        print("Error deleting recipe:", e)
        return False

def delete_ingredient_service(ingredient_id):
    try:
        return delete_ingredient_from_db(ingredient_id)
    except Exception as e:
        print("Error deleting ingredient:", e)
        return False


def fetch_product_from_openfoodfacts(barcode):
    """
    Fetches product information from OpenFoodFacts API by barcode.
    Args:
        barcode (str): The barcode to look up.
    Returns:
        dict: Product information if found, None otherwise.
    """
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 1 and data.get('product'):
            return normalize_openfoodfacts_product(data['product'])
        else:
            logging.warning(f"Product not found for barcode: {barcode}")
            return None
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching product from OpenFoodFacts: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error in fetch_product_from_openfoodfacts: {e}")
        return None


def normalize_openfoodfacts_product(product_data):
    """
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
    match = re.search(r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)', quantity_text)
    
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


def lookup_product_by_barcode(barcode):
    """
    Looks up a product by barcode, first checking local database, then OpenFoodFacts.
    Args:
        barcode (str): The barcode to look up.
    Returns:
        dict: Product information with 'source' field indicating 'local' or 'api'
    """
    # First check if we have this barcode in our local database
    local_ingredient = find_ingredient_by_barcode(barcode)
    if local_ingredient:
        return {
            'source': 'local',
            'name': local_ingredient.name,
            'brand': local_ingredient.brand,
            'quantity': local_ingredient.quantity,
            'quantity_unit': local_ingredient.quantity_unit,
            'price': local_ingredient.price,
            'barcode': local_ingredient.barcode
        }
    
    # If not found locally, try OpenFoodFacts API
    api_product = fetch_product_from_openfoodfacts(barcode)
    if api_product:
        api_product['source'] = 'api'
        return api_product
    
    return None


def check_barcode_exists(barcode):
    """
    Checks if a barcode already exists in the local database.
    Args:
        barcode (str): The barcode to check.
    Returns:
        bool: True if barcode exists, False otherwise.
    """
    return barcode_exists(barcode)
