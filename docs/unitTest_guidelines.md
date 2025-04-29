# Pytest Testing Conventions

## General Principles

- Use `pytest` as the testing framework.
- Write tests formally, following enterprise-level discipline.
- Use `unittest.mock.patch` to mock external dependencies (e.g., repositories, database access, external APIs).
- Follow the Arrange–Act–Assert (AAA) structure in all test functions.
- Focus each test on a single, well-defined purpose.
- Never mix test layers (e.g., unit tests should not access the database).

## Naming Conventions

- All test function names must be lowercase.
- Use underscores to separate words.
- Follow the pattern: `test_<what_is_tested>_<expected_result>()`.
- Be descriptive but concise.

**Examples:**
- `test_create_ingredient_success()`
- `test_authenticate_user_invalid_password()`
- `test_delete_recipe_not_found()`

## Function Structure

- Each test must be structured using AAA:
  ```
  ARRANGE: Set up all variables, mocks, and inputs.
  ACT: Perform a single action (e.g., call the function under test).
  ASSERT: Verify the expected result.
  ```
- Use the following block-style docstring template at the top of each test:
  ```python
  """
  ARRANGE: <what you prepared>
  ACT: <what you did>
  ASSERT: <what you expect>
  """
  ```
- Keep all variables and test inputs in the Arrange phase.
- Avoid defining or changing test inputs during the Act phase.
- No magic numbers in the Act phase: declare all inputs (including IDs and constants) in the Arrange section.

## Comments and Documentation

- Each test function should have a short docstring explaining the purpose of the test and outlining the AAA structure.
- Use triple-quoted strings for inline comments and docstrings, for example:
  ```python
  """
  Setup mock return values and test inputs.
  """
  ```
- Use section comments in code to mark AAA phases:
  ```python
  # Arrange
  # Act
  # Assert
  ```

## File Organization

- Group test files by functionality or service (one concern per file).
- Use a consistent directory layout such as:
  ```
  /tests
      test_userauth.py
      test_ingredient_service.py
      test_recipe_service.py
      test_routes_auth.py
      test_routes_ingredient.py
      test_routes_recipe.py
      conftest.py
  ```

## Design Discipline

- Mock all external systems or I/O in unit tests.
- Reserve integration tests for route and database-level behavior.
- Avoid duplicate assertions unless explicitly needed.
- Prefer clarity and maintainability over test cleverness.

