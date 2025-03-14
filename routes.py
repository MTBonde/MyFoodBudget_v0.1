from flask import render_template, request, redirect, session, url_for
from helpers import apology, login_required
from services import (
    authenticate_user,
    register_user,
    create_ingredient,
    create_recipe,
    get_all_ingredients,
    get_all_recipes,
    get_all_recipes_with_ingredients, delete_recipe_service, delete_ingredient_service
)

def init_routes(app):
    @app.route('/')
    def home():
        if 'user_id' in session:
            return render_template("index.html", user=session.get('user_id'))
        else:
            return render_template("landing.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            confirmation = request.form.get("confirmation")
            if not username or not email or not password or not confirmation:
                return apology("All fields are required", 400)
            if password != confirmation:
                return apology("Passwords must match", 400)
            if register_user(username, email, password):
                return redirect("/login")
            else:
                return apology("Username or email already exists", 400)
        else:
            return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            if not username or not password:
                return apology("Must provide username and password", 400)
            user = authenticate_user(username, password)
            if user:
                session["user_id"] = user.id
                return redirect("/")
            else:
                return apology("Invalid username or password", 403)
        else:
            return render_template("login.html")

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.route('/add_ingredient', methods=['GET', 'POST'])
    @login_required
    def add_ingredient_route():
        if request.method == 'POST':
            name = request.form.get('name')
            brand = request.form.get('brand')
            quantity = float(request.form.get('quantity'))
            quantity_unit = request.form.get('quantity_unit')
            price = float(request.form.get('price'))
            if create_ingredient(name, quantity, quantity_unit, price):
                return redirect(url_for('ingredients'))
            else:
                return apology('Error adding ingredient', 400)
        return render_template('add_ingredient.html')

    @app.route('/add_meal', methods=['GET', 'POST'])
    @login_required
    def add_meal_route():
        if request.method == 'POST':
            # Recipe basic info
            name = request.form.get('name')
            instructions = request.form.get('instructions')

            # Retrieve fields for existing ingredients
            existing_ingredient_ids = request.form.getlist('existing_ingredients[]')
            existing_quantity_purchased = request.form.getlist('existing_quantity_purchased[]')
            existing_quantity_used = request.form.getlist('existing_quantity_used[]')
            existing_ingredient_units = request.form.getlist('existing_ingredient_units[]')

            # Retrieve fields for new ingredients
            new_ingredient_names = request.form.getlist('new_ingredient_names[]')
            new_quantity_purchased = request.form.getlist('new_quantity_purchased[]')
            new_quantity_used = request.form.getlist('new_quantity_used[]')
            new_unit = request.form.getlist('new_unit[]')
            new_ingredient_prices = request.form.getlist('new_ingredient_prices[]')

            ingredients = []

            # Process existing ingredients
            for ingr_id, qty_purchased_str, qty_used_str, unit in zip(
                    existing_ingredient_ids,
                    existing_quantity_purchased,
                    existing_quantity_used,
                    existing_ingredient_units):
                if ingr_id and qty_purchased_str and qty_used_str:
                    try:
                        ingredient_id = int(ingr_id)
                        quantity_purchased = float(qty_purchased_str)
                        quantity_used = float(qty_used_str)
                    except ValueError as e:
                        print("Conversion error for existing ingredient:", e)
                        continue
                    # Get the price from the database
                    price = next((ing.price for ing in get_all_ingredients() if ing.id == ingredient_id), 0)
                    ingredients.append({
                        'id': ingredient_id,
                        'quantity_purchased': quantity_purchased,
                        'quantity_used': quantity_used,
                        'quantity_unit': unit,
                        'price': price
                    })

            # Process new ingredients
            for name_val, qty_purchased_str, qty_used_str, unit, price_str in zip(
                    new_ingredient_names,
                    new_quantity_purchased,
                    new_quantity_used,
                    new_unit,
                    new_ingredient_prices):
                if name_val and qty_purchased_str and qty_used_str:
                    try:
                        quantity_purchased = float(qty_purchased_str)
                        quantity_used = float(qty_used_str)
                        price = float(price_str)
                    except ValueError as e:
                        print("Conversion error for new ingredient:", e)
                        continue
                    new_ing = create_ingredient(name_val, quantity_purchased, unit, price)
                    if new_ing:
                        ingredients.append({
                            'id': new_ing.id,
                            'quantity_purchased': quantity_purchased,
                            'quantity_used': quantity_used,
                            'quantity_unit': unit,
                            'price': price
                        })

            if create_recipe(name, instructions, ingredients):
                return redirect(url_for('recipes'))
            else:
                return apology('Error adding recipe', 400)

        # GET request: provide ingredients data for the dropdowns
        ingredients_list = get_all_ingredients()
        ingredients = [{
            'id': ing.id,
            'name': ing.name,
            'price': ing.price,
            'quantity': ing.quantity,
            'quantity_unit': ing.quantity_unit
        } for ing in ingredients_list]
        return render_template('add_meal.html', ingredients=ingredients)

    @app.route('/recipes')
    @login_required
    def recipes():
        recipes_list = get_all_recipes_with_ingredients()
        return render_template('recipes.html', recipes=recipes_list)

    @app.route('/ingredients')
    @login_required
    def ingredients():
        ingredients_list = get_all_ingredients()
        return render_template('ingredients.html', ingredients=ingredients_list)

    @app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
    @login_required
    def delete_recipe(recipe_id):
        # Call a service function that deletes the recipe.
        if delete_recipe_service(recipe_id):
            return redirect(url_for('recipes'))
        else:
            return apology("Error deleting recipe", 400)

    @app.route('/delete_ingredient/<int:ingredient_id>', methods=['POST'])
    @login_required
    def delete_ingredient(ingredient_id):
        if delete_ingredient_service(ingredient_id):
            return redirect(url_for('ingredients'))
        else:
            return apology("Error deleting ingredient", 400)
