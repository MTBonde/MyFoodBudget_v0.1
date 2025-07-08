# app_factory.py; Factory pattern for initializin app, and avoiding circular imports

import os
from config import DevelopmentConfig, ProductionConfig
from flask import Flask, g, session
from flask_session import Session
from extensions import db


def initialize_database():
    """
    Initialize database using SQLAlchemy models for consistency between environments.
    This ensures the same schema is used in both IDE and staging/production.
    Must be called within an app context.
    """
    from models import User, Ingredient, Recipe, RecipeIngredient
    from flask import current_app
    
    try:
        # Ensure database directory exists
        db_path = current_app.config.get('DATABASE')
        if db_path and db_path != ':memory:':
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                print(f"Created database directory: {db_dir}")
        
        # Create all tables using SQLAlchemy models
        db.create_all()
        
        # Ensure all database connections are properly closed
        db.session.close()
        db.engine.dispose()
        
        print(f"Database initialized successfully using SQLAlchemy models")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        # Ensure cleanup even on error
        try:
            db.session.close()
            db.engine.dispose()
        except:
            pass
        raise


def create_app(config_class=None):
    """
    create the application, inject configuration dependencies
    """
    if config_class is None:
        # Auto-detect environment
        if os.environ.get('FLASK_ENV') == 'production':
            config_class = ProductionConfig
        else:
            config_class = DevelopmentConfig
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize SQLAlchemy with app context
    db.init_app(app)
    # Initialize session
    Session(app)

    # Initialize the database schema and run migrations
    with app.app_context():
        initialize_database()
        
        # Run database migrations after schema creation
        try:
            from migrations import migrate_database
            migrate_database()
        except Exception as e:
            print(f"Migration warning: {e}")
            # Don't fail app startup on migration errors

    @app.teardown_appcontext
    def teardown_db(exception):
        """
        Close the database connection and clear the session at the end of the request.
        """
        from db_helper import close_db
        close_db(exception)


    @app.after_request
    def after_request(response):
        """
        Ensure responses aren't cached
        """
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    # Import and initialize routes
    from routes import init_routes
    init_routes(app)

    return app
