# do2done Quick Start Guide

Get up and running with do2done in 5 minutes!

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- (Optional) Twilio account for SMS features

## Installation

### 1. Clone and Setup
```bash
cd do2done
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example environment file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

Edit `.env` with your settings:
```bash
SECRET_KEY=your-secret-key-here
DB_PASSWORD=your_postgres_password

# Optional: Twilio SMS (leave blank to disable)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

### 3. Setup Database
```bash
# Create PostgreSQL database
# psql -U postgres
# CREATE DATABASE do2done;

# Initialize database with migrations
flask db upgrade

# OR initialize without migrations
flask cli init-db
```

### 4. (Optional) Seed Test Data
```bash
flask cli seed-data --count 5
```

This creates:
- Test user: `+15555551234` / `password123`
- 5 sample tasks

### 5. Run the Application
```bash
python run.py
```

Visit: http://127.0.0.1:5000

## Quick Commands

### User Management
```bash
# Create a new user
flask cli create-user

# List all users
flask cli list-users

# Database statistics
flask cli db-stats
```

### Database Operations
```bash
# Reset database (WARNING: deletes all data)
flask cli reset-db

# Run migrations
flask db upgrade

# Create new migration
flask db migrate -m "Description"
```

### Development
```bash
# Run with debug mode
export FLASK_DEBUG=1  # Linux/Mac
set FLASK_DEBUG=1     # Windows
flask run

# Run with auto-reload
flask run --reload
```

## First Steps

### 1. Register an Account
1. Go to http://127.0.0.1:5000
2. Click "Sign Up"
3. Enter your details
4. If Twilio is configured, verify your phone
5. If not, use the test account or CLI to create users

### 2. Create Your First Task
1. Click "New Task" or "Add Task"
2. Enter task title
3. (Optional) Add description, due date, priority
4. Click "Save"

### 3. Manage Tasks
- **Complete**: Click checkbox next to task
- **Edit**: Click on task title
- **Delete**: Click delete button
- **Filter**: Use tabs to filter by status

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | `development` |
| `SECRET_KEY` | Flask secret key | Random |
| `DATABASE_URL` | Full database URL | PostgreSQL localhost |
| `DB_PASSWORD` | PostgreSQL password | `postgres` |
| `TWILIO_*` | Twilio SMS credentials | Disabled if not set |
| `BABEL_DEFAULT_LOCALE` | Default language | `en` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Application Settings

Edit `config.py` for advanced configuration:
- Session lifetime
- Verification code settings
- Pagination settings
- Security options

## Language Support

Switch between English and Spanish:
1. Click language selector in navigation
2. Or append `?lang=es` to URL
3. Preference saved in cookies

## Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
# Windows: Check Services
# Linux: sudo systemctl status postgresql

# Verify database exists
psql -U postgres -l
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

### Port Already in Use
```bash
# Use different port
flask run --port 5001
```

### SMS Not Working
- Verify Twilio credentials in `.env`
- Check Twilio account status
- Ensure phone numbers are in E.164 format (+1XXXXXXXXXX)
- SMS features are optional - app works without Twilio

## Development Tips

### Hot Reload
```bash
export FLASK_DEBUG=1
flask run
```

### View Logs
```bash
# Development: Console output
# Production: Check logs/do2done.log
```

### Database Shell
```bash
flask shell
>>> from app import db
>>> from app.models.users import User
>>> User.query.all()
```

### Translations
```bash
# Extract translatable strings
pybabel extract -F babel.cfg -o messages.pot .

# Compile translations
pybabel compile -d app/translations
```

## Next Steps

- [ ] Read [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- [ ] Check [README.md](README.md) for full documentation
- [ ] Configure Twilio for SMS notifications
- [ ] Set up production deployment
- [ ] Customize templates and styling

## Need Help?

- Check README.md for detailed documentation
- Review CONTRIBUTING.md for development info
- Open an issue on GitHub
- Check Flask documentation: https://flask.palletsprojects.com/

---

**Happy Task Managing with do2done!**
