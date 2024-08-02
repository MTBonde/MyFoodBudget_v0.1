# app_factory.py; Factory pattern for initializin app, and avoiding circular imports

from config import DevelopmentConfig
from db_init import initialize_database
from flask import Flask, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from extensions import db


def create_app(config_class=DevelopmentConfig):
    """
    create the application, inject configuration dependencies
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize SQLAlchemy with app context
    db.init_app(app)
    # Initialize session
    Session(app)

    # Initialize the database schema
    with app.app_context():
        initialize_database()

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
