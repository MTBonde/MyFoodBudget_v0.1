# services defines an action, a service
# Layered Architecture Pattern: organise into layers aech with a specific responsebility

# how to create an user is defined in the repository, so we import that blueprint
from werkzeug.security import check_password_hash
from repositories import create_user, find_by_username
from repositories import add_ingredient, add_recipe, add_recipe_ingredient
from repositories import get_all_ingredients_from_db, get_all_recipes_from_db, get_all_recipes_with_ingredients_from_db



# blueprint for autheticating a user login
def authenticate_user(username, password):
    """
    Authenticate a user based on username and password.

    :param username: The username of the user to authenticate.
    :param password: The password of the user for authentication.
    :return: The user object if authentication is successful, None otherwise.
    """
    user = find_by_username(username)
    # Returns the user if authentication is successful, else None
    if user and check_password_hash(user.hash, password):
        return user
    return None


# this is a blue print for how to register a new user
def register_user(username, email, password):
    """
    Register a new user with a username, email, and password.

    :param username: Username for the new user.
    :param email: Email for the new user.
    :param password: Password for the new user.
    :return: True if user creation is successful, False otherwise.
    """
    # EO; if user already exist
    if find_by_username(username) is not None:
        return False

    # If not, proceed to create a new user
    user = create_user(username, email, password)
    return user is not None


def create_ingredient(name, quantity, quantity_unit, price):
    """
    Service to create a new ingredient.
    Args:
        name (str): The name of the ingredient.
        quantity (float): The quantity of the ingredient.
        quantity_unit (str): The unit of measurement for the quantity.
        price (float): The price of the ingredient.
    Returns:
        Ingredient: The newly created ingredient object, or None if creation failed.
    """
    return add_ingredient(name, quantity, quantity_unit, price)

def create_recipe(name, instructions, ingredients):
    """
    Service to create a new recipe and add ingredients to it, with transaction management
    handled in the repository layer.
    """
    total_price = sum(ingredient['price'] for ingredient in ingredients)
    recipe = add_recipe(name, instructions, total_price)
    if recipe:
        for ingredient in ingredients:
            if not add_recipe_ingredient(recipe.id, ingredient['id'], ingredient['quantity'], ingredient['quantity_unit']):
                return None
        return recipe
    else:
        return None


def get_all_ingredients():
    """
    Service to get all ingredients.
    Returns:
        List: A list of all ingredient objects.
    """
    return get_all_ingredients_from_db()


def get_all_recipes():
    """
    Service to get all recipes.
    Returns:
        List: A list of all recipe objects.
    """
    return get_all_recipes_from_db()


def get_all_recipes_with_ingredients():
    """
    Service to get all recipes with their ingredients.
    Returns:
        List: A list of all recipes with their associated ingredients.
    """
    return get_all_recipes_with_ingredients_from_db()