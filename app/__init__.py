import os
from flask import Flask, g, redirect, render_template, render_template_string, request, session, current_app, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_babel import Babel, get_translations, refresh
from flask_babel import gettext as _
from flask_babel import ngettext
from twilio.rest import Client

db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message = 'Please log in to access this page.'

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # 1. Set up Babel configuration first
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_DOMAIN'] = 'messages'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations')
    app.config['LANGUAGES'] = ['en', 'es']

    # 2. Initialize Babel
    babel.init_app(app)

    # 3. Set up locale selector
    def get_locale():
        locale = session.get('lang') or request.accept_languages.best_match(current_app.config['LANGUAGES']) or 'en'
        print(f"Selected Locale: {locale}")
        return locale
    
    babel.locale_selector_func = get_locale

    # 4. Set up Jinja2 with Babel integration


    @app.before_request
    def before_request():
        g.locale = str(get_locale())
        refresh()

    # Force load translations
    with app.app_context():
        translations = get_translations()
        app.jinja_env.add_extension('jinja2.ext.i18n')
        app.jinja_env.install_gettext_translations(translations)
        app.jinja_env.install_gettext_callables(
            gettext=_,
            ngettext=ngettext,
            newstyle=True
        )

        if translations:
            print(f"Initial translations catalog: {translations._catalog}")
            
        print(f"Translation directory: {app.config['BABEL_TRANSLATION_DIRECTORIES']}")
        print(f"Available translations: {babel.list_translations()}")
        for trans in babel.list_translations():
            print(f"Loading translations for: {trans.language}")

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Initialize Twilio client
    global client, TWILIO_PHONE_NUMBER
    client = Client(app.config['TWILIO_ACCOUNT_SID'],
                   app.config['TWILIO_AUTH_TOKEN'])
    TWILIO_PHONE_NUMBER = app.config['TWILIO_PHONE_NUMBER']
    
    # Register blueprints
    from app.routes.tasks import tasks_bp
    from app.routes.users import users_bp
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(users_bp)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.users import User
        return User.query.get(int(user_id))

    @app.route('/')
    def home():
        return render_template('login.html')

    @app.route('/set-language/<lang>')
    def set_language(lang):
        if lang in current_app.config['LANGUAGES']:
            session['lang'] = lang
            session.modified = True  # Force session update
        return redirect(request.referrer or url_for('home'))
    
    @app.route('/translation-state')
    def translation_state():
        from babel.support import Translations
        trans_file = os.path.join(app.config['BABEL_TRANSLATION_DIRECTORIES'], 
                                'es/LC_MESSAGES/messages.mo')
        with open(trans_file, 'rb') as f:
            translations = Translations(f)
        
        # Add detailed diagnostics
        current_translations = get_translations()
        
        return {
            'file_exists': os.path.exists(trans_file),
            'file_size': os.path.getsize(trans_file),
            'translations': str(translations._catalog) if translations else 'No translations',
            'current_translations': str(current_translations._catalog) if current_translations else 'No current translations',
            'locale': str(get_locale()),
            'translation_dir': app.config['BABEL_TRANSLATION_DIRECTORIES']
        }

    return app

app = create_app()
