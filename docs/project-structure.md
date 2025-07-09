# MyFoodBudget Project Structure

## File Organization Guidelines

This document defines the organizational structure for the MyFoodBudget project to maintain consistency and make the codebase easier to navigate.

## Root Directory Files

### Core Application Files
- `app.py` - Main Flask application entry point
- `app_factory.py` - Application factory pattern implementation
- `config.py` - Configuration settings for different environments
- `models.py` - SQLAlchemy ORM data models
- `routes.py` - Flask route definitions and controllers
- `services.py` - Business logic layer
- `repositories.py` - Data access layer (Repository pattern)
- `helpers.py` - Utility functions and decorators
- `extensions.py` - Flask extension initialization
- `error_handlers.py` - Custom error handling and HTTP error responses
- `exceptions.py` - Custom exception classes for application errors
- `logging_config.py` - Centralized logging configuration
- `migrations.py` - Database migration system for schema updates
- `manage.py` - CLI commands for database operations
- `db_helper.py` - Database utility functions
- `db_init.py` - Database schema initialization (legacy)

### Database Files
- `myfoodbudget.db` - SQLite database file (development)

### Configuration Files
- `requirements.txt` - Python package dependencies (production)
- `requirements-dev.txt` - Development dependencies (pytest, coverage)
- `CLAUDE.md` - Claude Code guidance (root level for visibility)
- `Dockerfile` - Container configuration for deployment
- `entrypoint.sh` - Docker entrypoint script

## Directory Structure

```
MyFoodBudget/
├── barcode/                # Barcode scanning module
│   ├── readers/           # API readers for nutrition data
│   └── [scanner files]    # Barcode processing logic
├── docs/                  # Documentation files
├── logs/                  # Application logs
├── static/                # Static web assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── images/           # Images and icons (future)
├── templates/             # Jinja2 HTML templates
│   └── errors/           # Error page templates
├── tests/                 # Test files
│   └── flask_session/    # Test session storage
├── flask_session/         # Flask session storage
├── local_tests/          # Local development tests
└── [root files]          # Core application files
```

## Documentation (`docs/`)

**Purpose**: All project documentation except Claude Code guidance

**Contents**:
- `README.md` - Project overview and features
- `tasks.md` - Development task tracking and roadmap
- `unitTest_guidelines.md` - Testing conventions and standards
- `project-structure.md` - This file - project organization guide
- `design.md` - UI/UX design specifications (future)
- `nutrition-feature-plan.md` - Nutrition system architecture documentation
- `cicd-homelab-plan.md` - CI/CD deployment planning
- `api-docs.md` - API documentation (future)
- `deployment.md` - Deployment instructions (future)

**Guidelines**:
- Use Markdown format for all documentation
- Keep documentation up to date with code changes
- Include examples and code snippets where helpful
- Use consistent formatting and structure

## Static Assets (`static/`)

### CSS Files (`static/css/`)
- `styles.css` - Main stylesheet with custom styles
- `components.css` - Reusable component styles (future)
- `variables.css` - CSS custom properties (future)

### JavaScript Files (`static/js/`)
- `deleteConfirmation.js` - Delete confirmation dialogs
- `meal_scripts.js` - Recipe/meal related functionality
- `priceCalculations.js` - Price calculation utilities
- `charts.js` - Data visualization scripts (future)
- `utils.js` - Common utility functions (future)

### Images (`static/images/`)
**Future directory for**:
- `icons/` - Application icons and favicons
- `ingredients/` - Ingredient placeholder images
- `logos/` - Brand logos and graphics

## Templates (`templates/`)

**Purpose**: Jinja2 HTML templates for web pages

**Structure**:
- `layout.html` - Base template with common structure
- `Landing.html` - Landing/welcome page
- `index.html` - Dashboard/home page
- `login.html` - User login form
- `register.html` - User registration form
- `ingredients.html` - Ingredient list page
- `add_ingredient.html` - Add ingredient form
- `recipes.html` - Recipe list page
- `add_meal.html` - Add recipe form
- `apology.html` - Error page template

**Guidelines**:
- Extend `layout.html` for consistent structure
- Use descriptive template names
- Include template-specific CSS/JS at the bottom
- Follow Jinja2 best practices for template inheritance

## Tests (`tests/`)

**Purpose**: Automated test suite

**Structure**:
- `conftest.py` - Pytest configuration and fixtures
- `test_userauth.py` - User authentication tests
- `test_ingredient_service.py` - Ingredient service tests
- `test_nutrition_service.py` - Nutrition data service tests
- `test_barcode_module.py` - Barcode scanning module tests
- `test_integration_barcode.py` - End-to-end barcode integration tests
- `test_database_schema.py` - Database schema validation tests
- `test_config_environment.py` - Configuration and environment tests
- `test_recipe_service.py` - Recipe service tests (future)
- `test_routes_auth.py` - Authentication route tests (future)
- `test_routes_ingredient.py` - Ingredient route tests (future)
- `test_routes_recipe.py` - Recipe route tests (future)
- `flask_session/` - Test session storage

**Guidelines**:
- Follow naming convention: `test_[module]_[functionality].py`
- Use AAA pattern (Arrange, Act, Assert)
- Include docstrings with AAA structure
- Mock external dependencies

## Session Storage (`flask_session/`)

**Purpose**: Flask-Session file-based session storage

**Contents**:
- Session files with hexadecimal names
- Automatically managed by Flask-Session
- Separate directories for different environments (dev/test)

**Guidelines**:
- Do not commit session files to version control
- Clean up old session files periodically
- Consider Redis for production environments

## File Naming Conventions

### Python Files
- Use snake_case for all Python files
- Be descriptive but concise
- Group related functionality (e.g., `test_ingredient_service.py`)

### Templates
- Use snake_case or descriptive names
- Match the primary function (e.g., `add_ingredient.html`)
- Use consistent capitalization

### Static Assets
- CSS: Use kebab-case (`user-profile.css`)
- JavaScript: Use camelCase (`userProfile.js`)
- Images: Use descriptive names (`ingredient-placeholder.png`)

## Environment-Specific Files

### Development
- `myfoodbudget.db` - Development database
- `flask_session/` - Development sessions
- Debug logs (future)

### Testing
- `tests/flask_session/` - Test session storage
- In-memory database for tests
- Test coverage reports (future)

### Production (Future)
- Production database configuration
- Redis session storage
- Log files
- Static asset optimization

## Git Ignore Guidelines

**Include in .gitignore**:
- `myfoodbudget.db` - Database files
- `flask_session/` - Session directories
- `__pycache__/` - Python cache files
- `.env` - Environment variables
- `*.log` - Log files
- `coverage/` - Test coverage reports

**Commit to Repository**:
- All source code files
- Template files
- Static assets (CSS, JS)
- Documentation
- Test files
- Configuration templates

## Adding New Files

### When adding new Python modules:
1. Choose appropriate location (root for core, separate directory for groups)
2. Follow naming conventions
3. Add corresponding tests in `tests/`
4. Update imports in other files as needed

### When adding new templates:
1. Place in `templates/` directory
2. Extend `layout.html` for consistency
3. Add corresponding route in `routes.py`
4. Include template-specific assets

### When adding new static assets:
1. Place in appropriate `static/` subdirectory
2. Use consistent naming conventions
3. Reference properly in templates
4. Consider performance implications

## Documentation Updates

When modifying the project structure:
1. Update this `project-structure.md` file
2. Update `CLAUDE.md` if architectural changes affect development
3. Update `docs/README.md` if user-facing changes
4. Notify team members of significant changes

## Future Considerations

### Potential Restructuring:
- **Blueprints**: Organize routes into feature-based blueprints
- **API Directory**: Separate API endpoints from web routes
- **Utils Directory**: Common utilities and helpers
- **Config Directory**: Multiple configuration files
- **Migrations**: Database migration files (Flask-Migrate)

### Scaling Considerations:
- **Module Separation**: Split large files into smaller modules
- **Package Structure**: Convert to proper Python package
- **Asset Management**: Webpack or similar for static assets
- **Environment Configs**: Separate configuration per environment