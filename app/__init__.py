from datetime import timedelta
import os
import logging
from flask import Flask, g, redirect, render_template, request, session, current_app, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_babel import Babel, get_translations, refresh, gettext as _, ngettext
from twilio.rest import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message = _('Please log in to access this page.')

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True
    
    def get_locale():
        try:
            if request.args.get('lang'):
                return request.args.get('lang')
            if request.cookies.get('lang'):
                return request.cookies.get('lang')
            if 'lang' in session:
                return session['lang']
            return request.accept_languages.best_match(['en', 'es'])
        except RuntimeError:
            return 'en'

    babel = Babel()
    babel.init_app(app, locale_selector=get_locale)

    @app.context_processor
    def inject_babel():
        return dict(babel=babel)

    @app.before_request
    def before_request():
        g.locale = str(get_locale())
        if hasattr(current_app, 'babel'):
            current_app.babel.refresh()
        refresh()
        # Force Jinja to reload translations
        current_app.jinja_env.cache = {}

    with app.app_context():
        translations = get_translations()
        app.jinja_env.add_extension('jinja2.ext.i18n')
        app.jinja_env.install_gettext_translations(translations)
        
        logger.info(f"Translation directory: {app.config['BABEL_TRANSLATION_DIRECTORIES']}")
        logger.info(f"Available translations: {[trans.language for trans in babel.list_translations()]}")

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    global client
    client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])
    global TWILIO_PHONE_NUMBER
    TWILIO_PHONE_NUMBER = app.config['TWILIO_PHONE_NUMBER']

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
        if lang in app.config['LANGUAGES']:
            session['lang'] = lang
            session.permanent = True
            session.modified = True
            
            next_url = request.referrer or url_for('home')
            response = redirect(next_url)
            
            max_age = 365 * 24 * 60 * 60
            response.set_cookie(
                'lang',
                lang,
                max_age=max_age,
                httponly=False,
                samesite='Lax',
                secure=False
            )
            
            response.headers['Cache-Control'] = 'no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.vary.add('Cookie')
            
            return response
        return redirect(url_for('home'))

    @app.route('/translation-state')
    def translation_state():
        trans_file = os.path.join(app.root_path, app.config['BABEL_TRANSLATION_DIRECTORIES'], 'es/LC_MESSAGES/messages.mo')
        file_exists = os.path.exists(trans_file)
        file_size = os.path.getsize(trans_file) if file_exists else 0
        translations = None

        if file_exists:
            with open(trans_file, 'rb') as f:
                from babel.support import Translations
                translations = Translations(f)

        current_translations = get_translations()

        return {
            'file_exists': file_exists,
            'file_size': file_size,
            'translations': str(translations._catalog) if translations else 'No translations',
            'current_translations': str(current_translations._catalog) if current_translations else 'No current translations',
            'locale': str(get_locale()),
            'translation_dir': app.config['BABEL_TRANSLATION_DIRECTORIES']
        }

    return app

app = create_app()
