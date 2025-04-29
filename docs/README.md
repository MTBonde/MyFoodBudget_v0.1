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

- **User Authentication**: Registration, login, and logout with secure password hashing (Flask-Login).
- **Ingredient Management**: Add, view, and delete ingredients with quantity and price; automatic price-per-unit calculation.
- **Recipe Management**: Create, view, and delete recipes by combining existing or new ingredients; automatic cost breakdown.
- **Cost Calculation**: Computes total recipe cost using ingredient usage ratios.
- **Future Enhancements**: 
  - Receipt scanning (OCR).
  - nutritional information lookup. 
  - Deal finder integrations.

## Technology Stack

- **Backend**: Python, Flask, SQLAlchemy, SQLite
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Authentication**: Flask-Login
- **Forms & Validation**: Flask-WTF

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
├── app.py            # Flask app initialization
├── config.py         # Configuration settings
├── models.py         # ORM data models
├── forms.py          # Flask-WTF forms
├── routes.py         # Controllers (Flask routes)
├── repositories.py   # Data access layer
├── services.py       # Business logic layer
├── helpers/          # Utility functions
│   └── utils.py
├── templates/        # Jinja2 templates
├── static/           # CSS and JS files
└── requirements.txt  # Python dependencies
```

## Database Schema

- **users**: `id`, `username`, `hash`, `email`, `created_at`
- **ingredients**: `id`, `name`, `quantity`, `quantity_unit`, `price`
- **recipes**: `id`, `name`, `instructions`, `total_price`
- **recipe_ingredients**: `recipe_id`, `ingredient_id`, `quantity`, `quantity_unit`

## Personal Use

This project is intended solely for my own use and experimentation. 
All code and documentation are for personal reference; 
no external contributions or licensing considerations apply at this stage.

