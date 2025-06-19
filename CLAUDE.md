# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Run Application:**
```bash
python app.py
# Starts Flask development server on http://localhost:5000 with debug=True
```

**Run Tests:**
```bash
pytest tests/
# Run all tests

pytest tests/test_userauth.py
# Run specific test file

pytest tests/test_userauth.py::test_register_user_success
# Run specific test function
```

**Database Setup:**
```bash
python db_init.py
# Initialize database schema (manual approach, no migrations)
```

## Architecture Overview

**MyFoodBudget** is a Flask web application for ingredient tracking and recipe cost calculation using a layered MVC architecture with clear separation of concerns.

### Core Architectural Patterns

- **Factory Pattern**: `app_factory.py` handles application initialization to avoid circular imports
- **Repository Pattern**: `repositories.py` abstracts data access operations
- **Service Layer**: `services.py` contains business logic between routes and repositories
- **Session-based Authentication**: Flask-Session with login_required decorator

### Application Flow

1. **Entry Point**: `app.py` imports from factory and runs with debug mode
2. **Factory Setup**: `app_factory.py` configures Flask app, initializes SQLAlchemy, sets up database schema
3. **Route Registration**: `routes.py` uses `init_routes(app)` pattern instead of blueprints
4. **Data Flow**: Routes → Services → Repositories → Models → SQLite database

### Key Components

**Models** (`models.py`):
- User, Ingredient, Recipe, RecipeIngredient with SQLAlchemy ORM
- Many-to-many relationship between recipes and ingredients via junction table

**Data Access**:
- **ORM**: SQLAlchemy for simple operations
- **Raw SQL**: Complex queries like `find_recipes_using_ingredient` in repositories
- **Database**: SQLite file-based storage (`myfoodbudget.db`)

**Authentication System**:
- Session-based using Flask-Session (not Flask-Login despite docs)
- Password hashing with Werkzeug security
- `login_required` decorator in `helpers.py`

**Business Logic**:
- Recipe cost calculation algorithms in `services.py`
- Unit conversion utilities using Pint library
- Ingredient and recipe management operations

### Database Relationships

```
Users (1) ← Sessions
↓
Ingredients (M) ←→ (M) Recipes
         ↑              ↓
         └── RecipeIngredients ──┘
```

## Testing Framework

**Structure**: Pytest with enterprise-level discipline following AAA pattern

**Conventions**:
- Use `unittest.mock.patch` for mocking external dependencies
- All test functions lowercase with underscores: `test_<what_is_tested>_<expected_result>()`
- Block-style docstrings with AAA structure documentation
- Mock all external systems in unit tests

**Test Organization**:
- `conftest.py`: In-memory SQLite fixtures and shared setup
- Separate files by service layer: `test_userauth.py`, `test_ingredient_service.py`
- Missing tests for repositories and routes (see `docs/tasks.md`)

## Configuration

**Current Setup**:
- Hardcoded SECRET_KEY and development settings in `config.py`
- DevelopmentConfig class with DEBUG=True and 30-minute sessions
- Missing environment-specific configurations (production/testing)

**Dependencies** (`requirements.txt`):
- Flask 3.0.3, SQLAlchemy 2.0.31, Flask-Session
- Pint for unit conversion, PyTZ for timezones
- No testing dependencies listed (pytest used but not in requirements)

## Development Notes

**Current Limitations**:
- Manual database schema creation (no Flask-Migrate)
- Monolithic routes file instead of blueprints
- Limited error handling and logging
- Hardcoded configuration values

**Key Files for Extension**:
- `app_factory.py`: Add new Flask extensions or configuration
- `repositories.py`: Add new data access methods
- `services.py`: Add new business logic
- `routes.py`: Add new endpoints (consider blueprint refactoring for large changes)