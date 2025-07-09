# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

**Operating System**: WSL Ubuntu on Windows  
**Python**: 3.12+ with virtual environment in `.mfb-env/` (WSL) and `.venv/` (Windows)  
**Framework**: Flask  
**Package Manager**: pip  

**Virtual Environment Names**:
- `.mfb-env` (WSL/Claude Code)
- `.venv` (Windows/PyCharm)

**Development Environment Commands**:
```bash
# Activate Virtual Environment (WSL/Claude Code)
source .mfb-env/bin/activate

# Activate Virtual Environment (Windows/PyCharm)
.venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt          # Production dependencies
pip install -r requirements-dev.txt     # Development dependencies (pytest, coverage)
pip install --upgrade Flask             # Upgrade Flask to latest
```

**Dependencies Management**:
- Always activate virtual environment before working
- Production dependencies: tracked in `requirements.txt`
- Development dependencies: tracked in `requirements-dev.txt` (pytest, pytest-cov)
- Never commit `.mfb-env/` or `.venv/` to version control
- Add both to `.gitignore`
- When adding new packages:
  - Production: `pip install <package> && pip freeze > requirements.txt`
  - Development: Add to `requirements-dev.txt` manually

## Development Commands

**Run Application:**
```bash
python app.py
# Starts Flask development server on http://localhost:5000 with debug=True
```

**Run Tests:**
```bash
pytest                                   # Run all tests
pytest --cov                            # Run tests with coverage
pytest -v                               # Run tests with verbose output
pytest tests/test_userauth.py           # Run specific test file
pytest tests/test_userauth.py::test_register_user_success  # Run specific test function
```

**Code Quality (Add these tools to requirements-dev.txt):**
```bash
# Code formatting and linting (install with: pip install flake8 black)
flake8 .                                 # Check code style and potential issues
black .                                  # Auto-format code to PEP 8 standards
black --check .                          # Check if code needs formatting (CI/CD)

# Type checking (install with: pip install mypy)
mypy .                                   # Static type checking
```

**Database Setup:**
```bash
python db_init.py
# Initialize database schema (manual approach, no migrations)

# OR use the new migration system:
python manage.py init-db          # Initialize fresh database
python manage.py migrate          # Run pending migrations
python manage.py migration-status # Check migration status
python manage.py reset-db         # Reset database (WARNING: loses all data)
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

**Test Types**:
- **Unit Tests**: Individual components (`test_userauth.py`, `test_ingredient_service.py`)
- **Integration Tests**: Full workflow testing (`test_integration_barcode.py`)
- **Schema Tests**: Database schema validation (`test_database_schema.py`)

**Conventions**:
- Use `unittest.mock.patch` for mocking external dependencies
- All test functions lowercase with underscores: `test_<what_is_tested>_<expected_result>()`
- Block-style docstrings with AAA structure documentation
- Mock all external systems in unit tests

**Test Organization**:
- `conftest.py`: In-memory SQLite fixtures and shared setup
- Separate files by service layer: `test_userauth.py`, `test_ingredient_service.py`
- Integration tests cover full barcode scanning to database workflow
- Schema tests ensure database migrations work correctly

## Configuration

**Current Setup**:
- Hardcoded SECRET_KEY and development settings in `config.py`
- DevelopmentConfig class with DEBUG=True and 30-minute sessions
- Missing environment-specific configurations (production/testing)

**Dependencies** (`requirements.txt`):
- Flask 3.0.3, SQLAlchemy 2.0.31, Flask-Session
- Pint for unit conversion, PyTZ for timezones
- No testing dependencies listed (pytest used but not in requirements)

**Standard Test Data**:
- **Barcode**: `5740900403376` (Kærgården Smør - verified to exist on OpenFoodFacts)
- Use this barcode for all barcode-related tests and demonstrations
- Product: Kærgården Smør (Arla butter) - Danish product with complete nutrition data

## Development Notes

**Current Limitations**:
- **CRITICAL**: Multi-user data isolation not implemented (users can see each other's data)
- Monolithic routes file instead of blueprints
- Hardcoded configuration values (SECRET_KEY, database path)
- Limited client-side validation and CSRF protection

**Database Migration System**:
- `migrations.py`: Database migration system to handle schema changes
- `manage.py`: CLI commands for database operations
- Automatic migration on app startup (non-breaking)
- Version tracking to avoid schema conflicts
- Backup/restore functionality

**Key Files for Extension**:
- `app_factory.py`: Add new Flask extensions or configuration
- `repositories.py`: Add new data access methods
- `services.py`: Add new business logic
- `routes.py`: Add new endpoints (consider blueprint refactoring for large changes)
- `migrations.py`: Add new database migrations for schema changes
- `error_handlers.py`: Add new custom error handlers
- `exceptions.py`: Add new custom exception classes
- `barcode/`: Extend barcode scanning and nutrition lookup capabilities