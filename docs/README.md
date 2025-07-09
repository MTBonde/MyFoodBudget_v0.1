# MyFoodBudget

MyFoodBudget is a web application designed to help users track ingredients, manage recipes, and calculate food costs efficiently.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Personal Use](#personal-use)

## Features

- **User Authentication**: Registration, login, and logout with secure password hashing (Flask-Session).
- **Ingredient Management**: Add, view, and delete ingredients with quantity and price; automatic price-per-unit calculation.
- **Recipe Management**: Create, view, and delete recipes by combining existing or new ingredients; automatic cost breakdown.
- **Cost Calculation**: Computes total recipe cost using ingredient usage ratios.
- **Barcode Scanning**: Integration with OpenFoodFacts and NutriFinder DTU for automatic ingredient lookup
- **Nutrition Tracking**: Complete nutritional information (calories, protein, carbs, fat, fiber) per serving
- **Error Handling**: Comprehensive error handling with custom error pages and logging
- **Database Migrations**: Custom migration system for schema updates

## Technology Stack

- **Backend**: Python, Flask, SQLAlchemy, SQLite
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Authentication**: Flask-Session
- **Database**: SQLite with SQLAlchemy ORM
- **Unit Conversion**: Pint library
- **External APIs**: OpenFoodFacts, NutriFinder DTU (nutrition data)
- **Testing**: pytest with comprehensive test coverage

## Architecture

- **Layered Architecture (MVC)**
    - **Models** (`models.py`): ORM definitions for Users, Ingredients, Recipes, and RecipeIngredients.
    - **Repositories** (`repositories.py`): Data access layer implementing the Repository pattern.
    - **Services** (`services.py`): Business logic for authentication, ingredient/recipe operations.
    - **Controllers** (`routes.py`): Flask routes handling HTTP requests and rendering templates.
    - **Views** (`templates/`, `static/`): Jinja2 templates and static assets (CSS/JS).

- **Design Patterns**: Factory for app initialization, separation of concerns, cascading deletes for recipe-ingredient relationships.
- **Future Blueprint/Microservices**: Split into independent Flask Blueprints or microservices for Auth, Ingredients, and Recipes.

## Usage

- Navigate to `http://localhost:5000/` in your browser.
- **Register** a new user or **Login**.
- **Add Ingredients**: `/add_ingredient`
- **Add Recipes**: `/add_meal`
- **View Ingredients**: `/ingredients`
- **View Recipes**: `/recipes`

## Project Structure

```
MyFoodBudget/
├── app.py                 # Flask app initialization
├── app_factory.py         # Application factory pattern
├── config.py              # Configuration settings
├── models.py              # ORM data models
├── routes.py              # Controllers (Flask routes)
├── repositories.py        # Data access layer
├── services.py            # Business logic layer
├── helpers.py             # Utility functions and decorators
├── extensions.py          # Flask extension initialization
├── error_handlers.py      # Custom error handling
├── exceptions.py          # Custom exception classes
├── logging_config.py      # Logging configuration
├── migrations.py          # Database migration system
├── manage.py              # Database management CLI
├── barcode/               # Barcode scanning module
│   ├── scanner.py
│   └── readers/
├── docs/                  # Documentation
├── tests/                 # Test suite
├── templates/             # Jinja2 templates
├── static/                # CSS and JS files
├── logs/                  # Application logs
└── requirements.txt       # Python dependencies
```

## Database Schema

- **users**: `id`, `username`, `hash`, `email`, `created_at`
- **ingredients**: `id`, `name`, `quantity`, `quantity_unit`, `price`, `user_id`, `barcode`, `calories_per_100g`, `protein_per_100g`, `carbs_per_100g`, `fat_per_100g`, `fiber_per_100g`
- **recipes**: `id`, `name`, `instructions`, `total_price`, `user_id`, `servings`
- **recipe_ingredients**: `recipe_id`, `ingredient_id`, `quantity`, `quantity_unit`
- **schema_version**: `version` (for migration tracking)

## Personal Use

This project is intended solely for my own use and experimentation. 
All code and documentation are for personal reference; 
no external contributions or licensing considerations apply at this stage.

