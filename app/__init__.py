from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from twilio.rest import Client

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
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
        return render_template('index.html')
    
    return app
