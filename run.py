import openai
from app import create_app, db
from dotenv import load_dotenv
import os
from app.models import print_table_names
from sqlalchemy import inspect
from flask_session import Session
from app.routes import auth_bp
from app.models import User  # Import your User model
from flask_login import LoginManager
from flask_login import current_user

# Load environment variables from .env file
load_dotenv()

# Create the Flask app instance
app = create_app()
with app.app_context():
    db.reflect()


# Initialize and configure LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Set login route for unauthorized access
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # Load user by ID


# Set configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SESSION_TYPE'] = 'filesystem'  # or 'redis' for production
with app.app_context():
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    print(table_names)  # This should include 'report'


# Inject current_user into all templates to enable usage of `current_user` in Jinja templates
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

if __name__ == "__main__":
    app.run(debug=True)


    

# Define the GPT function
def gpt_generate_additional_info(base_response):
    # This function calls the OpenAI API to generate additional information
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=base_response + "\n\nPlease provide more details:",
            max_tokens=150,
            temperature=0.7
        )
        return base_response + " " + response.choices[0].text.strip()
    except Exception as e:
        return base_response + " (An error occurred while generating additional AI content: " + str(e) + ")"


app.register_blueprint(auth_bp)


