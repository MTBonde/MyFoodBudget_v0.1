# routes directs all the html requests, acting as a trafic controller
# uses the services to do the actions required by the requests
# Layered Architecture Pattern: organise into layers aech with a specific responsebility

from flask import render_template, request, redirect, session, url_for
from helpers import apology, login_required
from services import authenticate_user, register_user
from services import create_ingredient, create_recipe
from services import get_all_ingredients, get_all_recipes, get_all_recipes_with_ingredients

def init_routes(app):
    @app.route('/')
    def home():
        if 'user_id' in session:
            # If user is logged in, display the dashboard/home page
            return render_template("index.html", user=session.get('user_id'))
        else:
            # If user is not logged in, display the public landing page
            return render_template("landing.html")



    # registration route
    @app.route("/register", methods=["GET", "POST"])
    def register():
        # if post; when user is sending a filled out form
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            confirmation = request.form.get("confirmation")

            # EO
            # if not all fileds filled out
            if not username or not email or not password or not confirmation:
                return apology("All fields are required", 400)

            # if password doesn't match confirmation
            if password != confirmation:
                return apology("Passwords must match", 400)

            # redirect to login after succefull registration, else show apology
            if register_user(username, email, password):
                return redirect("/login")
            else:
                return apology("Username or email already exists", 400)

        # else get; show registration page
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
        # Clears all data in the session
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
    
            # Process the form data
            name = request.form.get('name')
            instructions = request.form.get('instructions')
    
            existing_ingredient_ids = request.form.getlist('existing_ingredients[]')
            existing_ingredient_quantities = request.form.getlist('existing_ingredient_quantities[]')
            existing_ingredient_units = request.form.getlist('existing_ingredient_units[]')
    
            new_ingredient_names = request.form.getlist('new_ingredient_names[]')
            new_ingredient_quantities = request.form.getlist('new_ingredient_quantities[]')
            new_ingredient_units = request.form.getlist('new_ingredient_units[]')
            new_ingredient_prices = request.form.getlist('new_ingredient_prices[]')
    
            ingredients = []
    
            # Process existing ingredients
            for i in range(len(existing_ingredient_ids)):
                if existing_ingredient_ids[i] and existing_ingredient_quantities[i]:
                    try:
                        ingredient_id = int(existing_ingredient_ids[i])
                        quantity = float(existing_ingredient_quantities[i])
                    except ValueError as e:
                        print("Conversion error for existing ingredient:", e)
                        continue
                    unit = existing_ingredient_units[i]
                    price = next((ing.price for ing in get_all_ingredients() if ing.id == ingredient_id), 0)
                    ingredients.append({'id': ingredient_id, 'quantity': quantity, 'quantity_unit': unit, 'price': price})
    
            # Process new ingredients
            for i in range(len(new_ingredient_names)):
                if new_ingredient_names[i] and new_ingredient_quantities[i]:
                    try:
                        quantity = float(new_ingredient_quantities[i])
                        price = float(new_ingredient_prices[i])
                    except ValueError as e:
                        print("Conversion error for new ingredient:", e)
                        continue
                    unit = new_ingredient_units[i]
                    new_ingredient = create_ingredient(new_ingredient_names[i], quantity, unit, price)
                    if new_ingredient:
                        ingredients.append({'id': new_ingredient.id, 'quantity': quantity, 'quantity_unit': unit, 'price': price})         
    
            if create_recipe(name, instructions, ingredients):
                return redirect(url_for('recipes'))
            else:
                return apology('Error adding recipe', 400)
    
        ingredients_list = get_all_ingredients()
        ingredients = [{'id': ing.id, 'name': ing.name, 'price': ing.price} for ing in ingredients_list]
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
