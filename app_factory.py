# app_factory.py; Factory pattern for initializin app, and avoiding circular imports

import os
import uuid
import time
from config import DevelopmentConfig, ProductionConfig
from flask import Flask, g, session, request
from flask_session import Session
from extensions import db
from logging_config import setup_logging, log_request_start, log_request_end, get_logger


def initialize_database():
    """
    Initialize database using SQLAlchemy models for consistency between environments.
    This ensures the same schema is used in both IDE and staging/production.
    Must be called within an app context.
    """
    from models import User, Ingredient, Recipe, RecipeIngredient
    from flask import current_app
    
    logger = get_logger(__name__)
    
    try:
        # Ensure database directory exists
        db_path = current_app.config.get('DATABASE')
        if db_path and db_path != ':memory:':
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Created database directory: {db_dir}")
        
        # Create all tables using SQLAlchemy models
        db.create_all()
        
        # Ensure all database connections are properly closed
        db.session.close()
        db.engine.dispose()
        
        logger.info("Database initialized successfully using SQLAlchemy models")
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}", exc_info=True)
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

    # Initialize logging as early as possible
    setup_logging(app.config)
    logger = get_logger(__name__)
    logger.info("Application startup initiated")

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
            logger.warning(f"Migration warning: {e}")
            # Don't fail app startup on migration errors

    # Request tracking middleware
    @app.before_request
    def before_request():
        """Track request start time and assign request ID."""
        g.request_start_time = time.time()
        g.request_id = str(uuid.uuid4())[:8]  # Short UUID for logging
        log_request_start()

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
        Ensure responses aren't cached and log request completion
        """
        # Calculate request duration
        if hasattr(g, 'request_start_time'):
            duration = (time.time() - g.request_start_time) * 1000  # Convert to milliseconds
            g.request_duration = round(duration, 2)
        
        # Log request completion
        log_request_end(response)
        
        # Cache control headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    # Register error handlers
    from error_handlers import register_error_handlers
    register_error_handlers(app)

    # Import and initialize routes
    from routes import init_routes
    init_routes(app)

    logger.info("Application initialization completed successfully")
    return app
