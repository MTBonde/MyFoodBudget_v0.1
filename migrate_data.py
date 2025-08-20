#!/usr/bin/env python3
"""
Data migration script to assign existing ingredients and recipes to users.
This script should be run once to migrate existing data to the new user isolation system.
"""

from app_factory import create_app
from models import db, User, Ingredient, Recipe
from logging_config import get_logger

logger = get_logger('migrate_data')

def migrate_existing_data():
    """
    Migrate existing ingredients and recipes to be owned by users.
    Assigns all orphaned records to the first user found in the database.
    """
    app = create_app()
    
    with app.app_context():
        # Get the first user to assign orphaned records to
        first_user = User.query.first()
        if not first_user:
            logger.error("No users found in database. Cannot migrate data.")
            print("ERROR: No users found in database. Please create a user first.")
            return False
        
        logger.info(f"Migrating orphaned data to user: {first_user.username} (ID: {first_user.id})")
        
        # Migrate ingredients without user_id
        orphaned_ingredients = Ingredient.query.filter_by(user_id=None).all()
        logger.info(f"Found {len(orphaned_ingredients)} ingredients without user_id")
        
        for ingredient in orphaned_ingredients:
            ingredient.user_id = first_user.id
            logger.debug(f"Assigned ingredient '{ingredient.name}' to user {first_user.id}")
        
        # Migrate recipes without user_id
        orphaned_recipes = Recipe.query.filter_by(user_id=None).all()
        logger.info(f"Found {len(orphaned_recipes)} recipes without user_id")
        
        for recipe in orphaned_recipes:
            recipe.user_id = first_user.id
            logger.debug(f"Assigned recipe '{recipe.name}' to user {first_user.id}")
        
        try:
            # Commit all changes
            db.session.commit()
            
            logger.info(f"Successfully migrated {len(orphaned_ingredients)} ingredients and {len(orphaned_recipes)} recipes to user {first_user.username}")
            print(f"✅ Migration completed successfully!")
            print(f"   - Migrated {len(orphaned_ingredients)} ingredients")
            print(f"   - Migrated {len(orphaned_recipes)} recipes") 
            print(f"   - All data assigned to user: {first_user.username}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to commit data migration: {e}")
            print(f"❌ Migration failed: {e}")
            return False

def verify_migration():
    """
    Verify that the migration was successful by checking for orphaned records.
    """
    app = create_app()
    
    with app.app_context():
        orphaned_ingredients = Ingredient.query.filter_by(user_id=None).count()
        orphaned_recipes = Recipe.query.filter_by(user_id=None).count()
        
        print(f"\n📊 Migration verification:")
        print(f"   - Orphaned ingredients: {orphaned_ingredients}")
        print(f"   - Orphaned recipes: {orphaned_recipes}")
        
        if orphaned_ingredients == 0 and orphaned_recipes == 0:
            print("✅ All data has been successfully migrated!")
            return True
        else:
            print("⚠️  Some records still need migration")
            return False

if __name__ == "__main__":
    print("🚀 Starting data migration for user isolation...")
    print("This will assign all existing ingredients and recipes to the first user in the database.")
    
    # Ask for confirmation
    response = input("\nContinue with migration? (y/N): ").strip().lower()
    if response != 'y':
        print("Migration cancelled.")
        exit(0)
    
    # Run migration
    success = migrate_existing_data()
    
    if success:
        # Verify migration
        verify_migration()
    else:
        print("\n❌ Migration failed. Please check the logs and try again.")
        exit(1)