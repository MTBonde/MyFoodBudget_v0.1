# models.py define what data is;
# Models are part of Object-Relational Mapping (ORM), ORM will be used for simple db operations,
# for more complex queries raw SQL will be used.
# Layered Architecture Pattern: organize into layers each with a specific responsibility.

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index
from extensions import db

# User model: defines what a user is.
class User(db.Model):
    """
    User model for storing user-related data.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        Index('idx_username', 'username', unique=True),
        Index('idx_email', 'email', unique=True),
    )


# Ingredient model: stores details of food ingredients.
class Ingredient(db.Model):
    """
    Ingredient model for storing details of food ingredients.
    """
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    quantity_unit = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    barcode = db.Column(db.String(50), nullable=True, unique=True, index=True)
    brand = db.Column(db.String(100), nullable=True)


# Recipe model: stores recipes.
class Recipe(db.Model):
    """
    Recipe model for storing recipes.
    """
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text)
    total_price = db.Column(db.Float)

    # Define relationship with RecipeIngredient with cascade deletion.
    recipe_ingredients = db.relationship(
        'RecipeIngredient',
        cascade="all, delete-orphan",
        lazy=True
    )


# RecipeIngredient model: associative table between recipes and ingredients.
class RecipeIngredient(db.Model):
    """
    Associative table between recipes and ingredients to manage many-to-many relationship.
    """
    __tablename__ = 'recipe_ingredients'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
    quantity = db.Column(db.Float, nullable=False)
    quantity_unit = db.Column(db.Text, nullable=False)

    # Relationship to Recipe without backref to avoid conflict.
    recipe = db.relationship('Recipe')
    # Relationship to Ingredient; here we still provide a backref for convenience.
    ingredient = db.relationship('Ingredient', backref=db.backref('recipe_ingredients', lazy=True))
