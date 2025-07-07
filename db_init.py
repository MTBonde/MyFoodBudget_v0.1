import sqlite3
import os
from config import DevelopmentConfig, ProductionConfig, TestingConfig

env = os.getenv("FLASK_ENV", "development")

if env == "development":
    config = DevelopmentConfig()
elif env == "testing":
    config = TestingConfig()
else:
    config = ProductionConfig()

DATABASE_URL = config.DATABASE

def initialize_database():
    conn = None
    try:
        # Ensure the directory exists for the database file
        db_dir = os.path.dirname(DATABASE_URL)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hash TEXT NOT NULL, -- Hashed password
            email TEXT NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create indexes for users table
        cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_username ON users (username);
        """)
        cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_email ON users (email);
        """)

        # Create ingredients table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity REAL NOT NULL,
            quantity_unit TEXT NOT NULL,
            price REAL NOT NULL
        );
        """)

        # Create recipes table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            instructions TEXT,
            total_price REAL
        );
        """)

        # Create recipe_ingredients table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            recipe_id INTEGER,
            ingredient_id INTEGER,
            quantity REAL NOT NULL,
            quantity_unit TEXT NOT NULL,
            PRIMARY KEY (recipe_id, ingredient_id),
            FOREIGN KEY (recipe_id) REFERENCES recipes(id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
        );
        """)

        conn.commit()
        conn.close()
        print(f"Database initialized successfully at: {DATABASE_URL}")
        
    except Exception as e:
        print(f"Error during database operations: {e}")
        if conn:
            conn.close()
        raise

if __name__ == "__main__":
    initialize_database()
