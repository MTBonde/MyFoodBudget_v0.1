#!/usr/bin/env python3
"""
Management commands for MyFoodBudget application.
Provides CLI commands for database operations, migrations, etc.
"""
import sys
import os
import argparse
from app_factory import create_app
from migrations import migrate_database, MigrationManager, create_migrations
from extensions import db
from models import User, Ingredient, Recipe


def init_db():
    """Initialize the database with fresh schema."""
    app = create_app()
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Running migrations...")
        migrate_database()
        print("Database initialized successfully!")


def migrate():
    """Run database migrations."""
    app = create_app()
    with app.app_context():
        migrate_database()


def migration_status():
    """Show migration status."""
    app = create_app()
    with app.app_context():
        db_path = app.config.get('DATABASE', 'myfoodbudget.db')
        manager = MigrationManager(db_path)
        
        current_version = manager.get_current_version()
        print(f"Current database version: {current_version}")
        
        all_migrations = create_migrations()
        print(f"Available migrations: {len(all_migrations)}")
        
        for migration in all_migrations:
            status = "✅ Applied" if migration.version <= current_version else "⏳ Pending"
            print(f"  {migration.version}: {migration.description} - {status}")


def rollback_migration(target_version: int):
    """Rollback to a specific migration version."""
    app = create_app()
    with app.app_context():
        db_path = app.config.get('DATABASE', 'myfoodbudget.db')
        manager = MigrationManager(db_path)
        
        for migration in create_migrations():
            manager.add_migration(migration)
        
        print(f"Rolling back to version {target_version}...")
        manager.rollback(target_version)
        print("Rollback completed!")


def reset_db():
    """Reset database completely (WARNING: loses all data)."""
    response = input("⚠️  This will delete ALL data. Type 'yes' to confirm: ")
    if response.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    print("Resetting database...")
    init_db()
    print("Database reset completed!")


def create_test_data():
    """Create some test data for development."""
    app = create_app()
    with app.app_context():
        print("Creating test data...")
        
        # Create test user
        from services import register_user
        if not User.query.filter_by(username='testuser').first():
            register_user('testuser', 'test@example.com', 'password123')
            print("Created test user: testuser/password123")
        
        # Create test ingredients using the butter barcode
        from services import create_ingredient
        
        test_ingredients = [
            {
                'name': 'Krægården Smør',
                'quantity': 200.0,
                'quantity_unit': 'g',
                'price': 25.0,
                'barcode': '5740900403376',
                'brand': 'Lurpak'
            },
            {
                'name': 'Test Flour',
                'quantity': 1000.0,
                'quantity_unit': 'g',
                'price': 8.50,
                'barcode': '1234567890128',
                'brand': 'Test Brand'
            }
        ]
        
        for ing_data in test_ingredients:
            existing = Ingredient.query.filter_by(barcode=ing_data['barcode']).first()
            if not existing:
                ingredient = create_ingredient(**ing_data)
                if ingredient:
                    print(f"Created test ingredient: {ingredient.name}")
        
        print("Test data created!")


def backup_db(backup_path: str):
    """Create a backup of the database."""
    app = create_app()
    with app.app_context():
        db_path = app.config.get('DATABASE', 'myfoodbudget.db')
        
        if not os.path.exists(db_path):
            print(f"Database file not found: {db_path}")
            return
        
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to: {backup_path}")


def restore_db(backup_path: str):
    """Restore database from backup."""
    if not os.path.exists(backup_path):
        print(f"Backup file not found: {backup_path}")
        return
    
    app = create_app()
    with app.app_context():
        db_path = app.config.get('DATABASE', 'myfoodbudget.db')
        
        response = input(f"⚠️  This will replace current database. Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            print("Operation cancelled.")
            return
        
        import shutil
        shutil.copy2(backup_path, db_path)
        print(f"Database restored from: {backup_path}")
        
        # Run migrations to ensure schema is up to date
        print("Running migrations on restored database...")
        migrate_database()
        print("Restore completed!")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='MyFoodBudget Management Commands')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Database commands
    subparsers.add_parser('init-db', help='Initialize database with fresh schema')
    subparsers.add_parser('migrate', help='Run database migrations')
    subparsers.add_parser('migration-status', help='Show migration status')
    subparsers.add_parser('reset-db', help='Reset database completely (WARNING: loses all data)')
    
    # Migration rollback
    rollback_parser = subparsers.add_parser('rollback', help='Rollback to specific migration version')
    rollback_parser.add_argument('version', type=int, help='Target migration version')
    
    # Test data
    subparsers.add_parser('create-test-data', help='Create test data for development')
    
    # Backup/restore
    backup_parser = subparsers.add_parser('backup', help='Create database backup')
    backup_parser.add_argument('path', help='Backup file path')
    
    restore_parser = subparsers.add_parser('restore', help='Restore database from backup')
    restore_parser.add_argument('path', help='Backup file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    try:
        if args.command == 'init-db':
            init_db()
        elif args.command == 'migrate':
            migrate()
        elif args.command == 'migration-status':
            migration_status()
        elif args.command == 'rollback':
            rollback_migration(args.version)
        elif args.command == 'reset-db':
            reset_db()
        elif args.command == 'create-test-data':
            create_test_data()
        elif args.command == 'backup':
            backup_db(args.path)
        elif args.command == 'restore':
            restore_db(args.path)
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()