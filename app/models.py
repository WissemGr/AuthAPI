from flask_restx import fields
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

user_model = {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'full_name': fields.String(required=True, description='User full name')
}

login_model = {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)