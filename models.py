# models.py define what data is;
# Models are part of Object-Relational Mapping (ORM), ORM will be used for simple db operations, for more complex queries raw sql will be used
# Layered Architecture Pattern: organise into layers aech with a specific responsebility
# chatgpt used to leave cs50 import SQL trainingwheel behind, switched to raw sqlite3 and sqlalchemy

# import SQLAmchemy for database
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index
from extensions import db

# the user model define what a user is
# a "user" has an id, username, hash (of password), email and creation timestamp
class User(db.Model):
    """
    User model for storing user-related data.
    """
    __tablename__ = "users"

    # int id, default to autoincrement
    id = db.Column(db.Integer, primary_key=True)
    # string username, max 50length, must be unique, cant be empty, create index
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    # string password hash, max 255length, cant be empty
    hash = db.Column(db.String(255), nullable=False)
    # string email, max 255length, must be unique, cant be empty
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    # timestamp
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # create index for username and email
    __table_args__ = (
        Index('idx_username', 'username', unique=True),
        Index('idx_email', 'email', unique=True),
    )


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


class Recipe(db.Model):
    """
    Recipe model for storing recipes.
    """
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text)
    total_price = db.Column(db.Float)


class RecipeIngredient(db.Model):
    """
    Associative table between recipes and ingredients to manage many-to-many relationship.
    """
    __tablename__ = 'recipe_ingredients'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
    quantity = db.Column(db.Float, nullable=False)
    quantity_unit = db.Column(db.Text, nullable=False)


    # Relationships
    recipe = db.relationship('Recipe', backref=db.backref('recipe_ingredients', lazy=True))
    ingredient = db.relationship('Ingredient', backref=db.backref('recipe_ingredients', lazy=True))
