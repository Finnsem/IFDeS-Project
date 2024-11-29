from flask import Flask
from .extensions import db, migrate
from flask_session import Session
from flask_login import LoginManager  # Import LoginManager
from .routes import auth_bp, bp as main_bp  # Import blueprints
from .models import User  # Import the User model to use with LoginManager
from flask_login import UserMixin
def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
    app.config['SESSION_TYPE'] = 'filesystem'
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)

    # Initialize and configure LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to the login page if not authenticated
    login_manager.login_message_category = 'info'

    # Define the user loader function for LoginManager
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # Ensure this fetches the correct user by ID
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
