import jwt
import logging
from app.config import secret_key  # Import your secret_key from config
from app.authorizations import json as authorizations
from datetime import datetime, timedelta
from flask import Flask
from app.models import db, user_model, login_model, User
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_restx import Resource, Namespace

app = Flask(__name__)

# Initialize the API
auth_ns = Namespace('auth', description='Authentication operations')
protected_ns = Namespace('api', description='Protected operations')
api_user_model = auth_ns.model('User', user_model)
api_login_model = auth_ns.model('Login', login_model)

@auth_ns.route('/register')
class UserRegistration(Resource):
    @auth_ns.expect(api_user_model, validate=True)
    @auth_ns.doc(security=[])
    def post(self):
        """
        Register a new user.
        """
        # Retrieve user data from the request payload
        user_data = auth_ns.payload

        # Extract email and password from user data
        email = user_data.get('email')
        password = user_data.get('password')
        full_name = user_data.get('full_name')

        # Perform validation on email and password
        if not email or not password or not full_name:
            return {'error': 'Email and password are required.'}, 400

        # Check if the email is already registered
        if User.query.filter_by(email=email).first():
            return {'error': 'Email already exists.'}, 409

        # Generate a hashed password
        hashed_password = generate_password_hash(password)

        # Create a new User object
        new_user = User(email=email, password=hashed_password, full_name=full_name)

        try:
            # Add the user to the session
            db.session.add(new_user)

            # Commit changes to the database
            db.session.commit()

            # Return a success response
            return {'message': 'Registration successful.'}, 200

        except SQLAlchemyError as e:
            # Handle any database-related errors
            db.session.rollback()  # Rollback the transaction
            # Log the error
            logging.exception(f"{e}")
            return {'error': 'Failed to register the user.'}, 500

@auth_ns.route('/login')
class UserLogin(Resource):
    @auth_ns.expect(api_login_model, validate=True)
    @auth_ns.doc(security=[])
    def post(self):
        """
        User login with email and password.
        """
        # Retrieve user data from the request payload
        user_data = auth_ns.payload

        # Extract email and password from user data
        email = user_data.get('email')
        password = user_data.get('password')

        # Retrieve the user from the database based on the provided email
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # User credentials are valid
            # Generate an authentication token
            token = jwt.encode(
                {
                    'user_id': user.id,
                    'exp': datetime.utcnow() + timedelta(hours=1)  # Token expiration time
                },
                secret_key,  # Replace with your own secret key
                algorithm='HS256'
            )

            return {'token': 'Bearer ' + token}, 200
        else:
            # Invalid credentials
            return {'error': 'Invalid credentials.'}, 401
