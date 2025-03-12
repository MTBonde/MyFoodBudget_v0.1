from werkzeug.security import check_password_hash
from repositories import (
    create_user,
    find_by_username,
    add_ingredient,
    add_recipe,
    add_recipe_ingredient,
    get_all_ingredients_from_db,
    get_all_recipes_from_db,
    get_all_recipes_with_ingredients_from_db, delete_recipe_from_db, delete_ingredient_from_db
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

def create_ingredient(name, quantity, quantity_unit, price):
    return add_ingredient(name, quantity, quantity_unit, price)

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
