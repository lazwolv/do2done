# do2done

A feature-rich personal to-do web application built with Flask, PostgreSQL, and Twilio SMS integration. Manage your tasks efficiently with a clean, responsive interface and receive SMS reminders for important deadlines.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Internationalization](#internationalization)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Overview

do2done is a personal task management web application that helps users organize their daily activities with an intuitive interface. Built using Flask and PostgreSQL, it offers user authentication, task CRUD operations, SMS notifications via Twilio, and multi-language support (English/Spanish).

## Features

### Task Management
- **Create Tasks**: Add new tasks with titles, descriptions, and due dates
- **Edit Tasks**: Update task details at any time
- **Delete Tasks**: Remove completed or unwanted tasks
- **Task Status**: Mark tasks as complete or incomplete
- **Priority Levels**: Organize tasks by priority
- **Due Dates**: Set deadlines for tasks

### User Features
- **User Authentication**: Secure registration and login system
- **User Profiles**: Manage personal information
- **Password Security**: Encrypted password storage
- **Session Management**: Persistent login sessions
- **Profile Customization**: Update user details and preferences

### Communication
- **SMS Notifications**: Twilio integration for task reminders
- **Phone Number Validation**: International phone number format support
- **Customizable Notifications**: Choose when to receive reminders

### Internationalization
- **Multi-language Support**: English and Spanish translations
- **Language Switching**: Easy language toggle
- **Localized Content**: All UI elements translated
- **Babel Integration**: Professional translation management

## System Requirements

### Software
- **Python**: 3.8 or higher
- **PostgreSQL**: 12 or higher
- **pip**: Latest version
- **Web Browser**: Modern browser (Chrome, Firefox, Safari, Edge)

### External Services
- **Twilio Account**: For SMS functionality (free trial available)

### Hardware
- **Storage**: 100MB minimum
- **RAM**: 512MB minimum (1GB+ recommended)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd do2done
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

Dependencies installed:
- `Flask==3.1.0` - Web framework
- `Flask-SQLAlchemy==3.1.1` - ORM and database integration
- `Flask-Login==0.6.3` - User session management
- `Flask-WTF==1.2.1` - Form handling and validation
- `Flask-Migrate==4.0.5` - Database migrations
- `psycopg2-binary==2.9.10` - PostgreSQL adapter
- `twilio==8.13.0` - SMS integration
- `phonenumbers==8.13.32` - Phone number validation
- `python-dotenv==1.0.1` - Environment variable management
- `Flask-Babel` - Internationalization support

### 4. Set Up PostgreSQL Database

**Create Database:**
```bash
# Access PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE do2done;

# Create user (optional)
CREATE USER do2done_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE do2done TO do2done_user;

# Exit
\q
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:
```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/do2done
# Or use DB_PASSWORD if not using full DATABASE_URL
DB_PASSWORD=your_postgres_password

# Flask Secret Key (generate with: python -c "import os; print(os.urandom(24).hex())")
SECRET_KEY=your_secret_key_here

# Twilio Configuration (get from https://www.twilio.com/console)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### 6. Initialize Database
```bash
# Run migrations
flask db upgrade

# If migrations don't exist, create them
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 7. Run the Application
```bash
flask run
```

Access at: `http://127.0.0.1:5000/`

## Configuration

### Database Configuration

Edit `config.py` for database settings:
```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    f"postgresql://postgres:{os.environ.get('DB_PASSWORD')}@localhost:5432/do2done"
```

### Twilio Configuration

1. **Sign up for Twilio**: Visit https://www.twilio.com/try-twilio
2. **Get Credentials**: Find your Account SID and Auth Token in the console
3. **Get Phone Number**: Acquire a Twilio phone number
4. **Add to .env**: Update your environment variables

### Session Configuration

Configure session lifetime in `app/__init__.py`:
```python
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
```

### Language Configuration

Supported languages configured in `config.py`:
```python
LANGUAGES = ['en', 'es']
BABEL_DEFAULT_LOCALE = 'en'
```

## Usage

### User Registration

1. Navigate to registration page
2. Enter username, email, and password
3. Optionally add phone number for SMS notifications
4. Submit to create account

### User Login

1. Enter username or email
2. Enter password
3. Check "Remember Me" for persistent session
4. Click login

### Managing Tasks

**Create New Task:**
1. Click "New Task" button
2. Enter task title (required)
3. Add description (optional)
4. Set due date (optional)
5. Choose priority level
6. Click "Save"

**Edit Task:**
1. Click on task or "Edit" button
2. Modify details
3. Click "Update"

**Complete Task:**
1. Check the checkbox next to task
2. Task marked as complete
3. Option to hide completed tasks

**Delete Task:**
1. Click "Delete" button on task
2. Confirm deletion

### SMS Notifications

**Setup:**
1. Go to Profile settings
2. Add phone number with country code (e.g., +1234567890)
3. Save profile

**Receive Notifications:**
- Automatic reminders for tasks due soon
- Manual notifications via task options
- Customizable notification timing

### Language Switching

1. Click language selector (EN/ES)
2. Page refreshes with selected language
3. Preference saved in cookies

## Project Structure

```
do2done/
├── app/                        # Application package
│   ├── __init__.py             # App factory and configuration
│   ├── models/                 # Database models
│   │   ├── users.py            # User model
│   │   └── tasks.py            # Task model
│   ├── routes/                 # Route handlers
│   │   ├── users.py            # User authentication routes
│   │   └── tasks.py            # Task management routes
│   ├── static/                 # Static files
│   │   ├── css/                # Stylesheets
│   │   ├── js/                 # JavaScript files
│   │   └── images/             # Images
│   ├── templates/              # Jinja2 templates
│   │   ├── base.html           # Base template
│   │   ├── login.html          # Login page
│   │   ├── register.html       # Registration page
│   │   ├── tasks.html          # Task list page
│   │   └── profile.html        # User profile page
│   └── translations/           # Language translations
│       ├── en/                 # English translations
│       └── es/                 # Spanish translations
├── migrations/                 # Database migrations
├── config.py                   # Configuration file
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in git)
└── README.md                   # This file
```

## Database Schema

### User Model
```python
- id: Integer (Primary Key)
- username: String (Unique, Required)
- email: String (Unique, Required)
- password_hash: String (Required)
- phone_number: String (Optional)
- created_at: DateTime
- updated_at: DateTime
- tasks: Relationship to Task model
```

### Task Model
```python
- id: Integer (Primary Key)
- title: String (Required)
- description: Text (Optional)
- completed: Boolean (Default: False)
- priority: Integer (Default: 1)
- due_date: DateTime (Optional)
- created_at: DateTime
- updated_at: DateTime
- user_id: Integer (Foreign Key to User)
- user: Relationship to User model
```

## API Endpoints

### Authentication Routes

**Registration:**
- `GET /register` - Display registration form
- `POST /register` - Create new user account

**Login:**
- `GET /login` - Display login form
- `POST /login` - Authenticate user

**Logout:**
- `GET /logout` - Log out current user

**Profile:**
- `GET /profile` - View user profile
- `POST /profile` - Update user profile

### Task Routes

**Task List:**
- `GET /tasks` - View all user tasks
- `GET /tasks?filter=active` - View active tasks
- `GET /tasks?filter=completed` - View completed tasks

**Task CRUD:**
- `POST /tasks/create` - Create new task
- `GET /tasks/<id>/edit` - Get task for editing
- `POST /tasks/<id>/update` - Update existing task
- `POST /tasks/<id>/delete` - Delete task
- `POST /tasks/<id>/toggle` - Toggle task completion

**SMS Notifications:**
- `POST /tasks/<id>/notify` - Send SMS reminder for task

### Utility Routes

**Language:**
- `GET /set-language/<lang>` - Switch application language

**Translation State:**
- `GET /translation-state` - Debug translation information

## Internationalization

### Supported Languages
- English (en) - Default
- Spanish (es)

### Adding New Translations

1. **Extract translatable strings:**
```bash
pybabel extract -F babel.cfg -o messages.pot .
```

2. **Initialize new language:**
```bash
pybabel init -i messages.pot -d app/translations -l fr
```

3. **Update existing translations:**
```bash
pybabel update -i messages.pot -d app/translations
```

4. **Edit translation files:**
   - Navigate to `app/translations/<lang>/LC_MESSAGES/`
   - Edit `messages.po` file
   - Add translations for each `msgid`

5. **Compile translations:**
```bash
pybabel compile -d app/translations
```

### Using Translations in Code

**In Python:**
```python
from flask_babel import gettext as _
message = _('Hello World')
```

**In Templates:**
```html
{{ _('Welcome to do2done') }}
```

## Development

### Running in Debug Mode

```bash
# Set Flask environment
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows

# Run with debug
flask run --debug
```

### Database Migrations

**Create New Migration:**
```bash
flask db migrate -m "Description of changes"
```

**Apply Migrations:**
```bash
flask db upgrade
```

**Rollback Migration:**
```bash
flask db downgrade
```

### Adding New Features

1. **Create Models**: Define in `app/models/`
2. **Create Routes**: Add to `app/routes/`
3. **Create Templates**: Add to `app/templates/`
4. **Register Blueprint**: Update `app/__init__.py`
5. **Run Migrations**: Create and apply database changes
6. **Test**: Thoroughly test new functionality

### Testing SMS Integration

```python
from twilio.rest import Client

client = Client(account_sid, auth_token)
message = client.messages.create(
    body="Test message",
    from_=twilio_phone_number,
    to=user_phone_number
)
```

## Deployment

### Production Checklist

1. **Set Environment Variables:**
```bash
export FLASK_ENV=production
export SECRET_KEY=<strong-secret-key>
export DATABASE_URL=<production-database-url>
```

2. **Database Migration:**
```bash
flask db upgrade
```

3. **Use Production WSGI Server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

4. **Configure Reverse Proxy** (nginx example):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Deployment Platforms

**Heroku:**
```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run flask db upgrade
```

**AWS/DigitalOcean:**
- Set up Ubuntu server
- Install Python, PostgreSQL, nginx
- Clone repository
- Configure environment
- Set up systemd service
- Configure nginx reverse proxy

**Docker:**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Troubleshooting

### Database Connection Issues

**Problem:** Cannot connect to PostgreSQL
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
# Verify connection string in .env
# Check PostgreSQL allows connections from your IP
```

**Problem:** Database doesn't exist
```bash
createdb do2done
flask db upgrade
```

### Migration Issues

**Problem:** Migration conflicts
```bash
# Reset migrations
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Twilio Issues

**Problem:** SMS not sending
- Verify Twilio credentials in .env
- Check account balance
- Verify phone numbers are in E.164 format (+1234567890)
- Check Twilio console for error messages

**Problem:** Invalid phone number
```python
import phonenumbers
number = phonenumbers.parse(phone, "US")
if not phonenumbers.is_valid_number(number):
    # Handle invalid number
```

### Translation Issues

**Problem:** Translations not appearing
```bash
# Recompile translations
pybabel compile -d app/translations

# Clear Flask cache
flask run  # Restart application
```

### Session Issues

**Problem:** Users logged out unexpectedly
- Check SECRET_KEY is set and consistent
- Verify session configuration in `app/__init__.py`
- Check cookie settings

## Security Considerations

### Password Security
- Passwords hashed using Werkzeug security
- Never store plain-text passwords
- Use strong SECRET_KEY

### Environment Variables
- Never commit .env file to git
- Use strong, random values for secrets
- Rotate credentials regularly

### Database Security
- Use strong database passwords
- Limit database user permissions
- Regular backups

### HTTPS
- Always use HTTPS in production
- Obtain SSL certificate (Let's Encrypt)
- Configure secure cookies

## Contributing

This is a personal project. For bug reports or feature requests, please open an issue.

## License

See LICENSE file for details.

## Support

For issues or questions, please check existing documentation or open an issue on the repository.

---

**Built with Flask** - A personal task management solution
