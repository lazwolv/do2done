import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration with common settings"""

    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"postgresql://postgres:{os.environ.get('DB_PASSWORD', 'postgres')}@localhost:5432/do2done"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Twilio SMS
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    TWILIO_ENABLED = all([
        os.environ.get('TWILIO_ACCOUNT_SID'),
        os.environ.get('TWILIO_AUTH_TOKEN'),
        os.environ.get('TWILIO_PHONE_NUMBER')
    ])

    # Internationalization
    LANGUAGES = ['en', 'es']
    BABEL_DEFAULT_LOCALE = os.environ.get('BABEL_DEFAULT_LOCALE', 'en')
    BABEL_DEFAULT_TIMEZONE = os.environ.get('BABEL_DEFAULT_TIMEZONE', 'UTC')
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(BASE_DIR, 'app/translations')

    # Session
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 30)))

    # Pagination
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 20))

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/do2done.log')

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # Verification
    VERIFICATION_CODE_LENGTH = 6
    VERIFICATION_CODE_EXPIRY_MINUTES = 10
    MAX_VERIFICATION_ATTEMPTS = 3
    VERIFICATION_LOCKOUT_MINUTES = 15


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

    # Require SECRET_KEY in production
    def __init__(self):
        super().__init__()
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("SECRET_KEY must be set in production!")


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    TWILIO_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
