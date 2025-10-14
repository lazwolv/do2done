"""
do2done Application Factory
"""
from datetime import timedelta
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, g, redirect, render_template, request, session, current_app, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_babel import Babel, lazy_gettext, get_translations, refresh, gettext as _, ngettext
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message = _('Please log in to access this page.')

# Twilio client (initialized in create_app)
client = None
TWILIO_PHONE_NUMBER = None


def configure_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')

        # File handler
        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE', 'logs/do2done.log'),
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # Set app log level
        log_level = app.config.get('LOG_LEVEL', 'INFO')
        app.logger.setLevel(getattr(logging, log_level))
        app.logger.info('do2done application startup')


def create_app(config_name=None):
    """
    Application factory function

    Args:
        config_name: Configuration name ('development', 'production', 'testing')
                    Defaults to FLASK_ENV environment variable or 'development'
    """
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    from config import config
    app.config.from_object(config.get(config_name, config['default']))
    
    # Configure logging
    configure_logging(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Initialize Twilio client if enabled
    global client, TWILIO_PHONE_NUMBER
    if app.config.get('TWILIO_ENABLED'):
        from twilio.rest import Client
        client = Client(
            app.config['TWILIO_ACCOUNT_SID'],
            app.config['TWILIO_AUTH_TOKEN']
        )
        TWILIO_PHONE_NUMBER = app.config['TWILIO_PHONE_NUMBER']
        app.logger.info('Twilio SMS service initialized')
    else:
        app.logger.warning('Twilio SMS service is disabled (missing credentials)')

    # Configure Babel for i18n
    def get_locale():
        try:
            if request.args.get('lang'):
                return request.args.get('lang')
            if request.cookies.get('lang'):
                return request.cookies.get('lang')
            if 'lang' in session:
                return session['lang']
            return app.config.get('BABEL_DEFAULT_LOCALE', 'en')
        except RuntimeError:
            return app.config.get('BABEL_DEFAULT_LOCALE', 'en')

    babel = Babel()
    babel.init_app(app, locale_selector=get_locale)

    # Context processors
    @app.context_processor
    def inject_babel():
        return dict(babel=babel)

    @app.context_processor
    def utility_processor():
        return {
            'get_locale': get_locale,
            'get_translations': get_translations
        }

    # Request handlers
    @app.before_request
    def before_request():
        g.locale = str(get_locale())
        refresh()
        translations = get_translations()
        current_app.jinja_env.install_gettext_translations(translations)

    with app.app_context():
        translations = get_translations()
        app.jinja_env.add_extension('jinja2.ext.i18n')
        app.jinja_env.install_gettext_translations(translations)

    # Register blueprints
    from app.routes.tasks import tasks_bp
    from app.routes.users import users_bp
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(users_bp)

    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)

    # Register CLI commands
    from app.cli import register_cli_commands
    register_cli_commands(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.users import User
        return User.query.get(int(user_id))

    # Main routes
    @app.route('/')
    def home():
        return render_template('login.html')

    @app.route('/set-language/<lang>')
    def set_language(lang):
        if lang in app.config['LANGUAGES']:
            session['lang'] = lang
            session.permanent = True

            # Clear caches
            if hasattr(current_app, 'babel_translations'):
                delattr(current_app, 'babel_translations')
            current_app.jinja_env.cache.clear()

            # Force reload translations
            with app.app_context():
                refresh()
                translations = get_translations()
                app.jinja_env.install_gettext_translations(translations)

            response = redirect(request.referrer or url_for('home'))
            response.set_cookie('lang', lang, max_age=365*24*60*60)
            response.headers['Cache-Control'] = 'no-store, must-revalidate'
            return response
        return redirect(url_for('home'))

    app.logger.info(f'do2done initialized in {config_name} mode')
    return app


# Create default app instance for backwards compatibility
app = create_app()
