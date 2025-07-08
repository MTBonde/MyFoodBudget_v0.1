"""
Database migration system for MyFoodBudget.
Handles schema changes without losing data.
"""
import sqlite3
import os
import logging
from typing import List, Callable
from flask import current_app


class Migration:
    """Represents a single database migration."""
    
    def __init__(self, version: int, description: str, up_func: Callable, down_func: Callable = None):
        self.version = version
        self.description = description
        self.up_func = up_func
        self.down_func = down_func


class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations: List[Migration] = []
        self.logger = logging.getLogger(__name__)
    
    def add_migration(self, migration: Migration):
        """Add a migration to the list."""
        self.migrations.append(migration)
        # Keep migrations sorted by version
        self.migrations.sort(key=lambda m: m.version)
    
    def get_current_version(self) -> int:
        """Get the current database version."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if migration table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='migration_version'
            """)
            
            if not cursor.fetchone():
                # Migration table doesn't exist, create it
                cursor.execute("""
                    CREATE TABLE migration_version (
                        version INTEGER PRIMARY KEY,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        description TEXT
                    )
                """)
                conn.commit()
                conn.close()
                return 0
            
            # Get the latest version
            cursor.execute("SELECT MAX(version) FROM migration_version")
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result[0] is not None else 0
            
        except Exception as e:
            self.logger.error(f"Error getting current version: {e}")
            return 0
    
    def apply_migration(self, migration: Migration):
        """Apply a single migration."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            self.logger.info(f"Applying migration {migration.version}: {migration.description}")
            
            # Execute the migration
            migration.up_func(cursor)
            
            # Record the migration
            cursor.execute("""
                INSERT INTO migration_version (version, description)
                VALUES (?, ?)
            """, (migration.version, migration.description))
            
            conn.commit()
            self.logger.info(f"Migration {migration.version} applied successfully")
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Migration {migration.version} failed: {e}")
            raise
        finally:
            conn.close()
    
    def migrate(self):
        """Apply all pending migrations."""
        current_version = self.get_current_version()
        self.logger.info(f"Current database version: {current_version}")
        
        pending_migrations = [m for m in self.migrations if m.version > current_version]
        
        if not pending_migrations:
            self.logger.info("No pending migrations")
            return
        
        self.logger.info(f"Found {len(pending_migrations)} pending migrations")
        
        for migration in pending_migrations:
            self.apply_migration(migration)
        
        self.logger.info("All migrations applied successfully")
    
    def rollback(self, target_version: int):
        """Rollback to a specific version (if down_func is available)."""
        current_version = self.get_current_version()
        
        if target_version >= current_version:
            self.logger.info("No rollback needed")
            return
        
        # Find migrations to rollback (in reverse order)
        rollback_migrations = [
            m for m in reversed(self.migrations)
            if m.version > target_version and m.version <= current_version
        ]
        
        for migration in rollback_migrations:
            if migration.down_func:
                self.logger.info(f"Rolling back migration {migration.version}")
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                try:
                    migration.down_func(cursor)
                    cursor.execute("DELETE FROM migration_version WHERE version = ?", (migration.version,))
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    self.logger.error(f"Rollback failed for migration {migration.version}: {e}")
                    raise
                finally:
                    conn.close()
            else:
                self.logger.warning(f"No rollback function for migration {migration.version}")


# Define actual migrations
def create_migrations() -> List[Migration]:
    """Create all defined migrations."""
    migrations = []
    
    # Migration 1: Add nutrition columns to ingredients table
    def add_nutrition_columns(cursor):
        """Add nutrition columns to ingredients table."""
        nutrition_columns = [
            'calories REAL',
            'protein REAL',
            'carbohydrates REAL',
            'fat REAL',
            'fiber REAL'
        ]
        
        for column in nutrition_columns:
            try:
                cursor.execute(f'ALTER TABLE ingredients ADD COLUMN {column}')
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    raise
    
    def remove_nutrition_columns(cursor):
        """Remove nutrition columns (complex in SQLite, requires recreation)."""
        # SQLite doesn't support DROP COLUMN easily
        # This is a simplified version - in practice, you'd recreate the table
        pass
    
    migrations.append(Migration(
        version=1,
        description="Add nutrition columns to ingredients table",
        up_func=add_nutrition_columns,
        down_func=remove_nutrition_columns
    ))
    
    # Migration 2: Add indexes for performance
    def add_indexes(cursor):
        """Add database indexes for better performance."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_ingredients_barcode ON ingredients(barcode)",
            "CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name)",
            "CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(name)",
            "CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe_id ON recipe_ingredients(recipe_id)",
            "CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_ingredient_id ON recipe_ingredients(ingredient_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def remove_indexes(cursor):
        """Remove performance indexes."""
        indexes = [
            "DROP INDEX IF EXISTS idx_ingredients_barcode",
            "DROP INDEX IF EXISTS idx_ingredients_name", 
            "DROP INDEX IF EXISTS idx_recipes_name",
            "DROP INDEX IF EXISTS idx_recipe_ingredients_recipe_id",
            "DROP INDEX IF EXISTS idx_recipe_ingredients_ingredient_id"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    migrations.append(Migration(
        version=2,
        description="Add performance indexes",
        up_func=add_indexes,
        down_func=remove_indexes
    ))
    
    # Migration 3: Add user_id to ingredients (for multi-user support)
    def add_user_id_to_ingredients(cursor):
        """Add user_id column to ingredients for multi-user support."""
        try:
            cursor.execute('ALTER TABLE ingredients ADD COLUMN user_id INTEGER')
            # Add foreign key constraint (note: SQLite has limited FK support)
            # cursor.execute('ALTER TABLE ingredients ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id)')
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                raise
    
    migrations.append(Migration(
        version=3,
        description="Add user_id to ingredients for multi-user support",
        up_func=add_user_id_to_ingredients
    ))
    
    return migrations


def migrate_database(db_path: str = None):
    """Run database migrations."""
    if db_path is None:
        # Use current app config if available
        try:
            db_path = current_app.config.get('DATABASE')
            if not db_path or db_path == ':memory:':
                # Don't migrate in-memory or missing databases
                return
        except RuntimeError:
            # No app context, use default
            db_path = 'myfoodbudget.db'
    
    # Create migration manager
    manager = MigrationManager(db_path)
    
    # Add all migrations
    for migration in create_migrations():
        manager.add_migration(migration)
    
    # Run migrations
    manager.migrate()


if __name__ == "__main__":
    # Run migrations directly
    migrate_database()