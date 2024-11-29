import os
from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify
import openai
import requests
from app import db
from app.models import Inquiry, Investment, Report, User
from datetime import datetime
from app.gpt import gpt_generate_additional_info
from flask import current_app
from sqlalchemy import text
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import render_template,abort
from flask_login import current_user
import subprocess
import json
from collections import namedtuple
import re
from app.chatbot import chatai



# Create a blueprint
bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
# Simulate a conversation state
CONVERSATION_STATE = {}


# Helper function to add a record and commit
def add_record_to_db(record):
    db.session.add(record)
    db.session.commit()

@bp.route('/')
@bp.route('/home')
def index():
    print(f"Current User: {current_user}")
    print(f"Is Admin: {getattr(current_user, 'is_admin', False)}")
    print(f"Is Authenticated: {current_user.is_authenticated}")

    if current_user.is_authenticated:
        username = current_user.username
        search_credits = current_user.search_credits
    else:
        username = "Guest"
        search_credits = "N/A"

    return render_template('index.html', username=username, search_credits=search_credits)

@bp.route('/contact')
def contact():
    return render_template('contact.html')

@bp.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    inquiry_type = request.form['inquiry_type']
    message = request.form['message']

    # Create and add new inquiry
    new_inquiry = Inquiry(name=name, email=email, inquiry_type=inquiry_type, message=message)
    add_record_to_db(new_inquiry)

    return redirect(url_for('main.thank_you'))

@bp.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@bp.route('/api/chat', methods=['POST'])
def chat():
    user_id = request.json.get('user_id', 'guest')  # Track conversations per user
    user_message = request.json.get('message', '')

    # Initialize conversation if new
    if user_id not in CONVERSATION_STATE:
        CONVERSATION_STATE[user_id] = {
            "step": 0,  # Track conversation steps
            "context": []  # Store conversation history for GPT context
        }

    state = CONVERSATION_STATE[user_id]

    # Predefined questions based on the step
    predefined_questions = [
        "What company are you planning to invest in?",
        "How much are you planning to invest?",
        "Are you aware of any risks associated with this investment?",
        "Have you reviewed any previous complaints or fraud alerts about this company?",
    ]

    # If it's a predefined step
    if state["step"] < len(predefined_questions):
        # If the user is responding to a question, add their response to the context
        if user_message:
            state["context"].append({"role": "user", "content": user_message})

        # Send the next predefined question
        bot_message = predefined_questions[state["step"]]
        state["context"].append({"role": "assistant", "content": bot_message})
        state["step"] += 1

    # If predefined questions are complete, involve GPT
    else:
        # Provide the entire conversation context to GPT
        prompt = "Based on this conversation, analyze the situation:\n\n"
        for exchange in state["context"]:
            prompt += f"{exchange['role'].capitalize()}: {exchange['content']}\n"

        # Add GPT analysis
        gpt_response = gpt_generate_additional_info(prompt)
        bot_message = gpt_response

    # Add the bot's message to the conversation context
    state["context"].append({"role": "assistant", "content": bot_message})

    # Return bot response
    return jsonify({"response": bot_message})

# Helper function for querying the database
def query_alert_list(query, params):
    return db.session.execute(text(query), params).fetchall()

@bp.route('/search', methods=['POST'])
def search():
    # Check if the user is logged in by verifying 'user_id' in the session
    if not current_user.is_authenticated:
        flash("Please log in to use the search function.", "warning")
        return jsonify({'success': False, 'message': 'You need to be logged in to perform a search.'}), 401

    # Fetch the logged-in user
    user = User.query.get(current_user.id)

    if not user:
        flash("Invalid user session. Please log in again.", "warning")
        return jsonify({'success': False, 'message': 'Invalid session. Please log in again.'}), 401

    # Allow admin users to bypass credit checks
    if not user.is_admin:
        if user.search_credits <= 0:
            return jsonify({'success': False, 'message': 'You have reached your search credit limit.'})

        # Deduct a credit for non-admin users
        user.search_credits -= 1
        db.session.commit()  # Save the updated credit count to the database

    # Proceed with the search
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'success': False, 'message': 'No search term provided.'}), 400

    query = "SELECT Name, years, remarks FROM Alert_list_Nov WHERE Name = :name"
    results = query_alert_list(query, {'name': name})

    if results:
        chosen_result = max(results, key=lambda x: len(x[2]))
        ai_analysis = gpt_generate_additional_info(f"Based on our data, {chosen_result[0]} is flagged due to: {chosen_result[2]}.")

        return jsonify({
            'success': True,
            'company_name': chosen_result[0],
            'remarks': chosen_result[2],
            'years': chosen_result[1],
            'ai_analysis': ai_analysis,
            'remaining_credits': user.search_credits if not user.is_admin else "Unlimited"
        })
    else:
        return jsonify({'success': False, 'message': 'No results found.', 'remaining_credits': user.search_credits if not user.is_admin else "Unlimited"})



@bp.route('/report', methods=['GET'])
def report_page():
    return render_template('report.html')

@bp.route('/report_suspicious_activity', methods=['POST'])
def report_suspicious_activity():
    platform_name = request.form['platform_name']
    activity_type = request.form['activity_type']
    description = request.form['description']
    reporter_email = request.form['reporter_email']

    # Create and add new report
    new_report = Report(platform_name=platform_name, activity_type=activity_type,
                        description=description, reporter_email=reporter_email, 
                        reported_at=datetime.now())
    add_record_to_db(new_report)

    return redirect(url_for('main.thank_you'))

@bp.route('/suggestions', methods=['POST'])
def suggestions():
    try:
        # Extract the partial company name from the request
        partial_name = request.json.get('name', '').strip()

        # Return an empty list if no partial name is provided
        if not partial_name:
            return jsonify(suggestions=[])

        # Execute the query to fetch matching names
        query = 'SELECT Name FROM Alert_list_Nov WHERE Name LIKE :name LIMIT 5'
        results = query_alert_list(query, {'name': f'%{partial_name}%'})

        # Extract and return the suggestions as a list of names
        return jsonify(suggestions=[result[0] for result in results])

    except Exception as e:
        # Handle unexpected errors
        return jsonify({'error': 'An error occurred while fetching suggestions', 'details': str(e)}), 500


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('Email or username already registered.', 'danger')
            return redirect(url_for('auth.register'))

        # Create a new user and hash the password
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


from flask_login import login_user



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Find the user by email
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            print(f"Logging in User: {user}")  # Debugging
            login_user(user)  # Flask-Login sets `current_user`
            flash('Login successful!', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')




from flask_login import logout_user

@auth_bp.route('/logout')
def logout():
    logout_user()  # This clears the current_user
    session.clear()  # Clear the session to ensure no lingering data
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))  # Redirect to login page



def fetch_data_with_replacements(query, params=None):
    results = db.session.execute(text(query), params).fetchall()
    
    # Replace "•" with <br> in each string field within the results
    processed_results = [
        tuple(field.replace("•", "<br>") if isinstance(field, str) else field for field in row)
        for row in results
    ]
    return processed_results

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/profile')
def profile():
    if not current_user.is_authenticated:
        flash("Please log in to view your profile.", "warning")
        return redirect(url_for('auth.login'))
    
    return render_template('profile.html', user=current_user)



# Admin-only decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:  # Ensure the user is logged in
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not getattr(current_user, 'is_admin', False):  # Ensure the user is an admin
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))  # Redirect to a safe page
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/company_list')
@admin_required
def company_list():
    companies = db.session.execute(
        text("SELECT id, Name, years, Remarks FROM Alert_list_Nov")
    ).fetchall()
    return render_template('company_list.html', companies=companies)



@bp.route('/verify-phone-form')
def render_verification_form():
    return render_template('verify_phone.html')  # Ensure this matches your HTML filename

@bp.route('/verify-phone', methods=['POST'])
def verify_phone_number():
    # Extract data from the request
    data = request.json
    number = data.get('number')
    country_code = data.get('country_code')
    installation_id = data.get('installation_id')

    try:
        # Execute the Node.js script to handle phone verification
        result = subprocess.check_output(
            ['node', 'app/static/js/truecaller_service.js', number, country_code, installation_id],
            universal_newlines=True
        )
        
        # Parse and return the result as JSON
        result_json = json.loads(result)
        return jsonify(result_json), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Phone verification failed', 'details': str(e)}), 500
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid response format from the verification service'}), 500

@bp.route('/get-contact', methods=['POST'])
def get_contact_details():
    data = request.json
    phone_number = data.get('phone_number')

    try:
        # Run the main.py script for contact lookup
        result = subprocess.check_output(['python', 'getcontact/src/main.py', phone_number], universal_newlines=True)
        
        # Parse and return the result as JSON
        result_json = json.loads(result)
        return jsonify(result_json), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Failed to get contact details', 'details': str(e)}), 500
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid response format from the contact service'}), 500

@bp.route('/edit/<int:company_id>', methods=['GET', 'POST'])
@admin_required
def edit_company(company_id):
    company = db.session.execute(
        text("SELECT * FROM Alert_list_Nov WHERE id = :id"),
        {'id': company_id}
    ).fetchone()

    if not company:
        flash("Company not found.", "danger")
        return redirect(url_for('main.company_list'))

    if request.method == 'POST':
        updated_name = request.form.get('name')
        updated_remarks = request.form.get('remarks')
        updated_years = request.form.get('years')

        db.session.execute(
            text("""
                UPDATE Alert_list_Nov
                SET Name = :name, Remarks = :remarks, years = :years
                WHERE id = :id
            """),
            {'id': company_id, 'name': updated_name, 'remarks': updated_remarks, 'years': updated_years}
        )
        db.session.commit()
        flash("Company updated successfully.", "success")

        return redirect(url_for('main.company_list'))

    return render_template('edit_company.html', company=company)

@bp.route('/delete/<int:company_id>', methods=['POST'])
@admin_required
def delete_company(company_id):
    company = db.session.execute(
        text("SELECT * FROM Alert_list_Nov WHERE id = :id"), {'id': company_id}
    ).fetchone()

    if company:
        db.session.execute(
            text("DELETE FROM Alert_list_Nov WHERE id = :id"), {'id': company_id}
        )
        db.session.commit()
        flash("Company deleted successfully.", "success")
    else:
        flash("Company not found.", "danger")

    return redirect(url_for('main.company_list'))

@bp.route('/add_company_page', methods=['GET'])
@admin_required
def add_page():
    """
    Render the form for adding a new company.
    """
    return render_template('add_company.html')


@bp.route('/add_company', methods=['GET', 'POST'])
@admin_required
def add_company():
    if request.method == 'POST':
        # Retrieve data from the form
        name = request.form.get('name')
        remarks = request.form.get('remarks')
        years = request.form.get('years')

        # Add new company to the database
        try:
            db.session.execute(
                text("""
                    INSERT INTO Alert_list_Nov (Name, Remarks, years)
                    VALUES (:name, :remarks, :years)
                """),
                {'name': name, 'remarks': remarks, 'years': years}
            )
            db.session.commit()
            flash("New company added successfully!", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "danger")
            print(f"Error occurred: {e}")

        return redirect(url_for('main.company_list'))

    # Render the add_company.html template for GET requests
    username = current_user.username if current_user.is_authenticated else "Guest"
    return render_template('add_company.html', username=username)


@bp.route('/chat')
def chat_page():
    # Check if the user is authenticated
    username = current_user.username if current_user.is_authenticated else "Guest"
    return render_template('chat.html', username=username)

from flask import request, jsonify




@bp.route("/chat/send", methods=["POST"], endpoint="chat_send")
def chat_send():
    try:
        user_id = request.json.get("user_id", "guest")  # Use "guest" if no user_id is provided
        user_message = request.json.get("message", "")

        # If no message is provided, start with a greeting
        if not user_message:
            initial_message = (
                "Hi there! 😊 I’m here to help you with your investments. Let’s get started—what would you like to know?"
            )
            return jsonify({"response": initial_message}), 200

        # Pass the user_id and user_message to chatai
        bot_response = chatai(user_id, user_message)

        # Return the bot's response
        return jsonify({"response": bot_response}), 200

    except Exception as e:
        print(f"Error in chat_send: {e}")
        return jsonify({"response": "Oops! Something went wrong. Let’s try again, shall we?"}), 500

@bp.route('/api/news', methods=['GET'])
def get_news():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'latest_news.json'), 'r') as news_file:
            news_data = json.load(news_file)
           
            return jsonify(news_data)
    except FileNotFoundError:
      
        return jsonify([])
  


