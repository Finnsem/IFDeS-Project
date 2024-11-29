from app import db
from sqlalchemy import inspect
from app import db
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


def print_table_names():
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    print("Tables in the database:", table_names)

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    inquiry_type = db.Column(db.String(50))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    risk_level = db.Column(db.String(50))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    search_credits = db.Column(db.Integer, default=10)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

from app import db
from datetime import datetime

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(120), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    reporter_email = db.Column(db.String(120), nullable=False)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Report {self.platform_name}>'
    
class AlertList(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    remarks = db.Column(db.Text, nullable=False)
    years = db.Column(db.Integer, nullable=False)



# Comment out or remove this line to avoid the RuntimeError
# print(db.engine.table_names())




