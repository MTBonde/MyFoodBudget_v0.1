from flask import render_template, request, redirect, session, url_for, jsonify, flash
from helpers import apology, login_required, validate_required_fields, validate_numeric_field
from exceptions import ValidationError, AuthenticationError, DatabaseError, ServiceError
from logging_config import get_logger
from services import (
    authenticate_user,
    register_user,
    create_ingredient,
    create_recipe,
    get_all_ingredients,
    get_all_recipes,
    get_all_recipes_with_ingredients, 
    delete_recipe_service, 
    delete_ingredient_service,
    lookup_product_by_barcode,
    check_barcode_exists,
    get_nutrition_data_dual_source,
    calculate_recipe_nutrition
)

# Get logger for routes
logger = get_logger('routes')

def init_routes(app):
    @app.route('/')
    def home():
        if 'user_id' in session:
            try:
                # Get user's ingredients and recipes for dashboard metrics
                ingredients = get_all_ingredients()
                recipes = get_all_recipes()
                
                # Calculate metrics
                ingredients_count = len(ingredients) if ingredients else 0
                recipes_count = len(recipes) if recipes else 0
                
                # Get latest ingredient name
                latest_ingredient_name = None
                if ingredients:
                    latest_ingredient = max(ingredients, key=lambda x: x.id)
                    latest_ingredient_name = latest_ingredient.name
                
                # Combine recent items (simplified)
                recent_items = []
                if ingredients:
                    for ingredient in ingredients[-3:]:
                        recent_items.append({
                            'name': f"Added ingredient: {ingredient.name}",
                            'type': 'Ingredient'
                        })
                if recipes:
                    for recipe in recipes[-2:]:
                        recent_items.append({
                            'name': f"Created recipe: {recipe.name}",
                            'type': 'Recipe'
                        })
                
                # Sort recent items by adding newest first
                recent_items = recent_items[-5:]  # Last 5 items
                
                return render_template("index.html", 
                                     user=session.get('user_id'),
                                     ingredients_count=ingredients_count,
                                     recipes_count=recipes_count,
                                     latest_ingredient_name=latest_ingredient_name,
                                     recent_items=recent_items)
            except Exception as e:
                logger.error(f"Error loading dashboard data: {str(e)}")
                # Fallback to basic dashboard
                return render_template("index.html", 
                                     user=session.get('user_id'),
                                     ingredients_count=0,
                                     recipes_count=0,
                                     latest_ingredient_name=None,
                                     recent_items=[])
        else:
            return render_template("landing.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            try:
                # Validate required fields
                validate_required_fields(request.form, ["username", "email", "password", "confirmation"])
                
                username = request.form.get("username")
                email = request.form.get("email")
                password = request.form.get("password")
                confirmation = request.form.get("confirmation")
                
                # Validate password confirmation
                if password != confirmation:
                    raise ValidationError("Passwords must match", field="confirmation")
                
                # Register the user (this will handle validation and raise appropriate exceptions)
                register_user(username, email, password)
                
                flash('Registration successful! You can now log in.', 'success')
                logger.info(f"User {username} registered successfully")
                return redirect("/login")
                
            except ValidationError as e:
                flash(e.message, 'error')
                logger.warning(f"Registration validation error: {e.message}")
                return render_template("register.html", 
                                     username=request.form.get("username", ""),
                                     email=request.form.get("email", ""))
            except Exception as e:
                logger.error(f"Unexpected error during registration: {e}")
                flash("An unexpected error occurred. Please try again.", 'error')
                return render_template("register.html")
        else:
            return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            try:
                # Validate required fields
                validate_required_fields(request.form, ["username", "password"])
                
                username = request.form.get("username")
                password = request.form.get("password")
                
                # Authenticate user (this will handle validation and raise appropriate exceptions)
                user = authenticate_user(username, password)
                
                session["user_id"] = user.id
                flash('Login successful!', 'success')
                logger.info(f"User {username} logged in successfully")
                return redirect("/")
                
            except (ValidationError, AuthenticationError) as e:
                flash(e.message, 'error')
                logger.warning(f"Login error: {e.message}")
                return render_template("login.html", username=request.form.get("username", ""))
            except Exception as e:
                logger.error(f"Unexpected error during login: {e}")
                flash("An unexpected error occurred. Please try again.", 'error')
                return render_template("login.html")
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
            try:
                # Validate required fields
                validate_required_fields(request.form, ['name', 'quantity', 'quantity_unit', 'price'])
                
                name = request.form.get('name')
                brand = request.form.get('brand')
                barcode = request.form.get('barcode')
                
                # Validate numeric fields
                quantity = validate_numeric_field(request.form.get('quantity'), 'quantity', min_value=0.001)
                price = validate_numeric_field(request.form.get('price'), 'price', min_value=0)
                
                quantity_unit = request.form.get('quantity_unit')
                
                # Create ingredient (this will handle validation and raise appropriate exceptions)
                create_ingredient(name, quantity, quantity_unit, price, barcode, brand)
                
                flash('Ingredient added successfully!', 'success')
                logger.info(f"Ingredient '{name}' added successfully")
                return redirect(url_for('ingredients'))
                
            except ValidationError as e:
                flash(e.message, 'error')
                logger.warning(f"Add ingredient validation error: {e.message}")
                return render_template('add_ingredient.html', 
                                     name=request.form.get('name', ''),
                                     brand=request.form.get('brand', ''),
                                     barcode=request.form.get('barcode', ''),
                                     quantity=request.form.get('quantity', ''),
                                     quantity_unit=request.form.get('quantity_unit', ''),
                                     price=request.form.get('price', ''))
            except Exception as e:
                logger.error(f"Unexpected error adding ingredient: {e}")
                flash("An unexpected error occurred. Please try again.", 'error')
                return render_template('add_ingredient.html')
        
        # Handle GET with barcode parameter (from scanner redirect)
        barcode = request.args.get('barcode')
        product_data = {}
        
        if barcode:
            # Try to get product information from barcode
            product_info = lookup_product_by_barcode(barcode)
            if product_info:
                product_data = product_info
                
                # Fetch nutrition data for display
                nutrition_data = get_nutrition_data_dual_source(product_info['name'], barcode)
                if nutrition_data:
                    product_data.update(nutrition_data)
                    flash(f'Product found: {product_info["name"]} with nutrition data. Please verify and adjust the information.', 'info')
                else:
                    flash(f'Product found: {product_info["name"]}, but no nutrition data available.', 'info')
                
                if product_info['source'] == 'local':
                    flash('This product already exists in your ingredients.', 'warning')
                    return redirect(url_for('ingredients'))
            else:
                flash('Product not found. Please enter the details manually.', 'warning')
                product_data = {'barcode': barcode}
        
        return render_template('add_ingredient.html', **product_data)

    @app.route('/scan_product', methods=['POST'])
    @login_required
    def scan_product():
        """
        API endpoint for barcode scanning.
        Accepts a barcode and returns product information.
        """
        try:
            data = request.get_json()
            barcode = data.get('barcode')
            
            if not barcode:
                raise ValidationError('Barcode is required', field='barcode')
            
            # Check if barcode already exists in our database
            if check_barcode_exists(barcode):
                return jsonify({
                    'status': 'exists',
                    'message': 'This product already exists in your ingredients.',
                    'redirect': url_for('ingredients')
                })
            
            # Look up product information
            product_info = lookup_product_by_barcode(barcode)
            
            if product_info:
                logger.info(f"Product found for barcode {barcode}")
                return jsonify({
                    'status': 'found',
                    'product': product_info,
                    'redirect': url_for('add_ingredient_route', barcode=barcode)
                })
            else:
                logger.info(f"Product not found for barcode {barcode}")
                return jsonify({
                    'status': 'not_found',
                    'message': 'Product not found. You can add it manually.',
                    'redirect': url_for('add_ingredient_route', barcode=barcode)
                })
                
        except ValidationError as e:
            logger.warning(f"Scan product validation error: {e.message}")
            return jsonify({'error': e.message}), 400
        except Exception as e:
            logger.error(f"Unexpected error during product scan: {e}")
            return jsonify({'error': 'Server error occurred'}), 500

    @app.route('/add_meal', methods=['GET', 'POST'])
    @login_required
    def add_meal_route():
        if request.method == 'POST':
            try:
                # Recipe basic info
                name = request.form.get('name')
                instructions = request.form.get('instructions')
                
                # Validate required fields
                if not name or not instructions:
                    raise ValidationError("Recipe name and instructions are required")

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
                            logger.warning(f"Conversion error for existing ingredient: {e}")
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
                            logger.warning(f"Conversion error for new ingredient: {e}")
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

                # Create recipe (this will handle validation and raise appropriate exceptions)
                create_recipe(name, instructions, ingredients)
                
                flash('Recipe added successfully!', 'success')
                logger.info(f"Recipe '{name}' added successfully")
                return redirect(url_for('recipes'))
                
            except ValidationError as e:
                flash(e.message, 'error')
                logger.warning(f"Add recipe validation error: {e.message}")
                # Return to form with current data
                ingredients_list = get_all_ingredients()
                ingredients_data = [{
                    'id': ing.id,
                    'name': ing.name,
                    'price': ing.price,
                    'quantity': ing.quantity,
                    'quantity_unit': ing.quantity_unit
                } for ing in ingredients_list]
                return render_template('add_meal.html', ingredients=ingredients_data)
            except Exception as e:
                logger.error(f"Unexpected error adding recipe: {e}")
                flash("An unexpected error occurred. Please try again.", 'error')
                # Return to form
                ingredients_list = get_all_ingredients()
                ingredients_data = [{
                    'id': ing.id,
                    'name': ing.name,
                    'price': ing.price,
                    'quantity': ing.quantity,
                    'quantity_unit': ing.quantity_unit
                } for ing in ingredients_list]
                return render_template('add_meal.html', ingredients=ingredients_data)

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
        
        # Add nutrition data to each recipe
        for recipe in recipes_list:
            recipe['nutrition'] = calculate_recipe_nutrition(recipe['id'])
        
        return render_template('recipes.html', recipes=recipes_list)

    @app.route('/ingredients')
    @login_required
    def ingredients():
        ingredients_list = get_all_ingredients()
        return render_template('ingredients.html', ingredients=ingredients_list)

    @app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
    @login_required
    def delete_recipe(recipe_id):
        try:
            # Delete the recipe (this will handle validation and raise appropriate exceptions)
            delete_recipe_service(recipe_id)
            
            flash('Recipe deleted successfully!', 'success')
            logger.info(f"Recipe {recipe_id} deleted successfully")
            return redirect(url_for('recipes'))
            
        except ValidationError as e:
            flash(e.message, 'error')
            logger.warning(f"Delete recipe validation error: {e.message}")
            return redirect(url_for('recipes'))
        except Exception as e:
            logger.error(f"Unexpected error deleting recipe {recipe_id}: {e}")
            flash("An unexpected error occurred while deleting the recipe.", 'error')
            return redirect(url_for('recipes'))

    @app.route('/delete_ingredient/<int:ingredient_id>', methods=['POST'])
    @login_required
    def delete_ingredient(ingredient_id):
        try:
            # Delete the ingredient (this will handle validation and raise appropriate exceptions)
            delete_ingredient_service(ingredient_id)
            
            flash('Ingredient deleted successfully!', 'success')
            logger.info(f"Ingredient {ingredient_id} deleted successfully")
            return redirect(url_for('ingredients'))
            
        except ValidationError as e:
            flash(e.message, 'error')
            logger.warning(f"Delete ingredient validation error: {e.message}")
            return redirect(url_for('ingredients'))
        except Exception as e:
            logger.error(f"Unexpected error deleting ingredient {ingredient_id}: {e}")
            flash("An unexpected error occurred while deleting the ingredient.", 'error')
            return redirect(url_for('ingredients'))
