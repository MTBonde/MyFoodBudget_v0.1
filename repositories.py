# Repositories.py defines how data is accessed and managed within the application.
# Repository pattern; a repository defines how data is accessed, kinda like a librarian helps retrieve, organize and store books(data)

# in models we difene what a user is
from models import db, User, Ingredient, Recipe, RecipeIngredient
from werkzeug.security import generate_password_hash
from db_helper import get_db
from sqlalchemy.exc import IntegrityError
from helpers import convert_to_standard_unit
import sqlite3



# this  is like a blurprint for how to create a user in the database
def create_user(username, email, password):
    """
    Creates a new user with the given username, email, and password.
    Returns the user object if created successfully, None otherwise.
    """

    # hash password
    hashed_password = generate_password_hash(password)
    # create an instance using the user blueprint defined in models
    new_user = User(username=username, email=email, hash=hashed_password)

    # try adding the new user to db
    try:
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except IntegrityError:
        # Rollback the session if an integrity error occurs (e.g., duplicate username or email)
        db.session.rollback()
        # Return None if the user was not added due to an error
        return None


def find_by_username(username):
    """
    Retrieves a user by username.
    Returns the user object if found, None otherwise.
    """

    return User.query.filter_by(username=username).first()


def add_ingredient(name, quantity, quantity_unit, price, barcode=None, brand=None):
    """
    Adds a new ingredient to the database.
    Args:
        name (str): The name of the ingredient.
        quantity (float): The amount of the ingredient.
        quantity_unit (str): The unit of measurement for the quantity (e.g., kg, g, l).
        price (float): The price of the ingredient.
        barcode (str, optional): The barcode of the ingredient.
        brand (str, optional): The brand of the ingredient.
    Returns:
        ingredient (Ingredient): The newly created ingredient object if successful, None otherwise.
    """
    #quantity, unit = convert_to_standard_unit(quantity, quantity_unit)
    new_ingredient = Ingredient(name=name, quantity=quantity, quantity_unit=quantity_unit, price=price, barcode=barcode, brand=brand)
    try:
        db.session.add(new_ingredient)
        db.session.commit()
        return new_ingredient
    except IntegrityError:
        db.session.rollback()
        return None


def add_recipe(name, instructions, total_price):
    """
    Adds a new recipe to the database.
    Args:
        name (str): The name of the recipe.
        instructions (str): Cooking instructions for the recipe.
        total_price (float): The total cost to prepare the recipe.
    Returns:
        recipe (Recipe): The newly created recipe object if successful, None otherwise.
    """
    new_recipe = Recipe(name=name, instructions=instructions, total_price=total_price)
    try:
        db.session.add(new_recipe)
        db.session.commit()
        return new_recipe
    except IntegrityError:
        db.session.rollback()
        return None


def add_recipe_ingredient(recipe_id, ingredient_id, quantity, quantity_unit):
    """
    Adds an ingredient to a recipe with specified quantity and unit.

    Args:
        recipe_id (int): The ID of the recipe to which the ingredient is being added.
        ingredient_id (int): The ID of the ingredient to be added.
        quantity (float): The amount of the ingredient to be added.
        quantity_unit (str): The unit of measurement for the quantity.

    Returns:
        bool: True if the operation is successful, False otherwise.
    """
    new_recipe_ingredient = RecipeIngredient(
        recipe_id=recipe_id,
        ingredient_id=ingredient_id,
        quantity=quantity,
        quantity_unit=quantity_unit
    )
    try:
        db.session.add(new_recipe_ingredient)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False


def find_recipes_using_ingredient(ingredient_name):
    """
    Finds recipes that use a specific ingredient.

    Args:
        ingredient_name (str): The name of the ingredient to search for in recipes.

    Returns:
        List[str]: A list of recipe names that use the specified ingredient.

    Executes a raw SQL query to retrieve recipes based on ingredient usage.
    This method uses direct SQL to handle complex joins efficiently.
    """
    sql = """
    SELECT recipes.name
    FROM recipes
    JOIN recipe_ingredients ON recipes.id = recipe_ingredients.recipe_id
    JOIN ingredients ON recipe_ingredients.ingredient_id = ingredients.id
    WHERE ingredients.name = :ingredient_name
    """

    with db.engine.connect() as connection:
        result = connection.execute(sql, {'ingredient_name': ingredient_name})
        return [row['name'] for row in result]




def get_all_ingredients_from_db():
    """
    Retrieves all ingredients from the database.
    Returns:
        List[Ingredient]: A list of all ingredient objects.
    """
    return Ingredient.query.all()


def get_all_recipes_from_db():
    """
    Retrieves all recipes from the database.
    Returns:
        List[Recipe]: A list of all recipe objects.
    """
    return Recipe.query.all()


def get_all_recipes_with_ingredients_from_db():
    """
    Retrieves all recipes with their ingredients from the database.
    Returns:
        List[dict]: A list of recipes with their associated ingredients.
    """
    recipes = Recipe.query.all()
    recipes_with_ingredients = []

    for recipe in recipes:
        ingredients = db.session.query(RecipeIngredient, Ingredient).filter(
            RecipeIngredient.recipe_id == recipe.id,
            RecipeIngredient.ingredient_id == Ingredient.id
        ).all()
        recipe_ingredients = [
            {
                'name': ingredient.name,
                'quantity': recipe_ingredient.quantity,
                'unit': recipe_ingredient.quantity_unit
            } for recipe_ingredient, ingredient in ingredients
        ]
        recipes_with_ingredients.append({
            'id': recipe.id,
            'name': recipe.name,
            'instructions': recipe.instructions,
            'total_price': recipe.total_price,
            'ingredients': recipe_ingredients
        })

    return recipes_with_ingredients

def delete_recipe_from_db(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe:
        db.session.delete(recipe)
        db.session.commit()
        return True
    return False

def delete_ingredient_from_db(ingredient_id):
    ingredient = Ingredient.query.get(ingredient_id)
    if ingredient:
        db.session.delete(ingredient)
        db.session.commit()
        return True
    return False


def find_ingredient_by_barcode(barcode):
    """
    Finds an ingredient by its barcode.
    Args:
        barcode (str): The barcode to search for.
    Returns:
        Ingredient: The ingredient object if found, None otherwise.
    """
    return Ingredient.query.filter_by(barcode=barcode).first()


def barcode_exists(barcode):
    """
    Checks if a barcode already exists in the database.
    Args:
        barcode (str): The barcode to check.
    Returns:
        bool: True if the barcode exists, False otherwise.
    """
    return Ingredient.query.filter_by(barcode=barcode).first() is not None


def search_ingredients_by_barcode_or_name(search_term):
    """
    Searches for ingredients by barcode or name.
    Args:
        search_term (str): The term to search for (barcode or name).
    Returns:
        List[Ingredient]: A list of matching ingredients.
    """
    return Ingredient.query.filter(
        (Ingredient.barcode.like(f'%{search_term}%')) |
        (Ingredient.name.like(f'%{search_term}%'))
    ).all()
