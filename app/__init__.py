import logging
from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from app.models import db, user_model,login_model, User
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError


# create the app
app = Flask(__name__)

# configure the Postgresql database, relative to the app instance folder
app.config.from_pyfile('config.py')

# initialize the app with the extension
db.init_app(app)

migrate = Migrate(app, db)

api = Api(app)

auth_ns = api.namespace('auth', description='Authentication operations')

api_user_model = api.model('User', user_model)
api_login_model = api.model('Login', login_model)

@auth_ns.route('/register')
class UserRegistration(Resource):
    @auth_ns.expect(api_user_model, validate=True)
    def post(self):
        # Retrieve user data from the request
        user_data = api.payload

        # Extract email and password from user data
        email = user_data.get('email')
        password = user_data.get('password')
        full_name = user_data.get('full_name')

        # Perform validation on email and password
        if not email or not password or not full_name:
            return {'error': 'Email and password are required.'}, 400

        # Create a new User object
        new_user = User(email=email, password=password, full_name=full_name)

        try:
            # Add the user to the session
            db.session.add(new_user)
            
            # Commit changes to the database
            db.session.commit()

            # Return success response
            return {'message': 'Registration successful.'}, 200

        except SQLAlchemyError as e:
            # Handle any database-related errors
            db.session.rollback()  # Rollback the transaction
            # Log the error
            logging.exception(f"{e}")
            return {'error': 'Failed to register user.'}, 500
        
@auth_ns.route('/login')
class UserLogin(Resource):
    @auth_ns.expect(api_login_model, validate=True)
    def post(self):

        # Retrieve user data from the request
        user_data = api.payload
        
        # Extract email and password from user data
        email = user_data.get('email')
        password = user_data.get('password')

        # TODO: Implement code to validate user credentials

        # Placeholder code for demonstration
        if email == 'user@example.com' and password == 'password123':
            return {'message': 'Login successful.'}, 200
        else:
            return {'error': 'Invalid credentials.'}, 401

    


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000 ,debug=True)

