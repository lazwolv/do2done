# Contributing to do2done

Thank you for considering contributing to do2done! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Getting Started

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 12 or higher
- Git
- Virtual environment tool (venv or virtualenv)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd do2done
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   flask cli init-db
   # Or use Flask-Migrate
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python run.py
   # Or
   flask run
   ```

## Project Structure

```
do2done/
├── app/
│   ├── __init__.py          # Application factory
│   ├── cli.py               # CLI commands
│   ├── errors.py            # Error handlers
│   ├── forms.py             # WTForms form classes
│   ├── models/              # Database models
│   │   ├── users.py
│   │   └── tasks.py
│   ├── routes/              # Route blueprints
│   │   ├── users.py
│   │   └── tasks.py
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py
│   │   ├── task_service.py
│   │   └── sms_service.py
│   ├── static/              # CSS, JS, images
│   ├── templates/           # Jinja2 templates
│   └── translations/        # i18n translations
├── migrations/              # Database migrations
├── tests/                   # Test suite
├── config.py                # Configuration classes
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── .env.example             # Example environment variables
```

## Coding Standards

### Python Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use docstrings for all functions, classes, and modules

### Code Organization
- **Models**: Database models go in `app/models/`
- **Routes**: HTTP route handlers go in `app/routes/`
- **Services**: Business logic goes in `app/services/`
- **Forms**: WTForms classes go in `app/forms.py`

### Naming Conventions
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Documentation
```python
def example_function(param1, param2):
    """
    Brief description of function.

    Args:
        param1 (type): Description of param1
        param2 (type): Description of param2

    Returns:
        type: Description of return value

    Raises:
        ExceptionType: Description of when this is raised
    """
    pass
```

## Making Changes

### Branch Naming
- Feature: `feature/description`
- Bug fix: `bugfix/description`
- Hotfix: `hotfix/description`
- Documentation: `docs/description`

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(tasks): add priority field to tasks
fix(auth): correct phone number validation
docs(readme): update installation instructions
```

### Development Workflow

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Follow coding standards
   - Add tests for new features

3. **Test your changes**
   ```bash
   pytest tests/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_user_registration
```

### Writing Tests
- Place test files in `tests/` directory
- Name test files: `test_*.py`
- Name test functions: `test_*`
- Use fixtures for common setup
- Aim for high code coverage

**Example:**
```python
def test_create_task(client, auth):
    auth.login()
    response = client.post('/tasks/add', data={'task': 'Test Task'})
    assert response.status_code == 302
    assert Task.query.filter_by(title='Test Task').first() is not None
```

## Database Migrations

### Creating Migrations
```bash
# Auto-generate migration
flask db migrate -m "Description of changes"

# Review the generated migration file
# Edit if necessary

# Apply migration
flask db upgrade
```

### Migration Best Practices
- Always review auto-generated migrations
- Test migrations on development database first
- Include both `upgrade()` and `downgrade()` functions
- Keep migrations small and focused
- Document complex migrations

## Internationalization (i18n)

### Adding Translations

1. **Mark strings for translation**
   ```python
   from flask_babel import _
   message = _('Hello World')
   ```

2. **Extract strings**
   ```bash
   pybabel extract -F babel.cfg -o messages.pot .
   ```

3. **Update translations**
   ```bash
   pybabel update -i messages.pot -d app/translations
   ```

4. **Edit translation files**
   - Edit `app/translations/<lang>/LC_MESSAGES/messages.po`

5. **Compile translations**
   ```bash
   pybabel compile -d app/translations
   ```

## Submitting Changes

### Pull Request Process

1. **Ensure your code:**
   - Follows coding standards
   - Includes tests
   - Has no linting errors
   - Passes all tests
   - Is properly documented

2. **Update documentation:**
   - Update README if needed
   - Add docstrings
   - Update CHANGELOG

3. **Create pull request:**
   - Use descriptive title
   - Reference related issues
   - Describe changes in detail
   - Include screenshots for UI changes

4. **Pull request template:**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Tests pass locally
   - [ ] Added new tests
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No new warnings generated
   ```

### Code Review
- Be open to feedback
- Respond to comments promptly
- Make requested changes
- Keep discussions professional

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-WTF Documentation](https://flask-wtf.readthedocs.io/)
- [Twilio Documentation](https://www.twilio.com/docs/)

## Questions?

If you have questions about contributing, please open an issue with the `question` label.

Thank you for contributing to do2done!
