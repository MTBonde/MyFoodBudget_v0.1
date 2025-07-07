import os
from app_factory import create_app
from extensions import db
from models import User, Ingredient, Recipe, RecipeIngredient

def initialize_database():
    """
    Initialize database using SQLAlchemy models for consistency between environments.
    This ensures the same schema is used in both IDE and staging/production.
    """
    try:
        # Create app and get database configuration
        app = create_app()
        
        with app.app_context():
            # Ensure the directory exists for the database file
            db_path = app.config.get('DATABASE')
            if db_path and db_path != ':memory:':
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
            
            # Create all tables using SQLAlchemy models
            db.create_all()
            
            print(f"Database initialized successfully using SQLAlchemy models")
            print(f"Database location: {app.config.get('DATABASE', 'configured in SQLALCHEMY_DATABASE_URI')}")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise

if __name__ == "__main__":
    initialize_database()
