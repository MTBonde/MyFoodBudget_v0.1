import sqlite3
import sqlite3
from config import Config

DATABASE_URL = Config.DATABASE

def initialize_database():
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

if __name__ == "__main__":
    initialize_database()
