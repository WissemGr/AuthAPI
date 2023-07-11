import logging
import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from app.models import db, user_model, login_model, User
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# Create the Flask application
app = Flask(__name__)

# Configure the Postgresql database, relative to the app instance folder
app.config.from_pyfile('config.py')

# Initialize the database with the app
db.init_app(app)
migrate = Migrate(app, db)

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Add the token to the Swagger documentation
authorizations = {
    'Bearer Token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}

# Initialize the API
api = Api(app, authorizations=authorizations)
auth_ns = api.namespace('auth', description='Authentication operations')
protected_ns = api.namespace('api', description='Protected operations')
api_user_model = api.model('User', user_model)
api_login_model = api.model('Login', login_model)


@auth_ns.route('/register')
class UserRegistration(Resource):
    @auth_ns.expect(api_user_model, validate=True)
    @auth_ns.doc(security=[])
    def post(self):
        """
        Register a new user.
        """
        # Retrieve user data from the request payload
        user_data = api.payload

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
    @auth_ns.doc(security=[])
    def post(self):
        """
        User login with email and password.
        """
        # Retrieve user data from the request payload
        user_data = api.payload

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
                'your-secret-key',  # Replace with your own secret key
                algorithm='HS256'
            )

            return {'token': 'Bearer ' + token}, 200
        else:
            # Invalid credentials
            return {'error': 'Invalid credentials.'}, 401


@protected_ns.route('/protected')
class ProtectedResource(Resource):
    @protected_ns.expect(api_user_model, validate=True)
    @api.doc(security='Bearer Token')
    def post(self):
        """
        Protected resource that requires authentication.
        """
        # Access the decoded token from the request headers
        bearer = request.headers['Authorization']
        token = bearer.split(' ')[1]

        try:
            # Decode the token and verify its authenticity
            decoded_token = jwt.decode(
                token,
                'your-secret-key',  # Replace with your own secret key
                algorithms=['HS256']
            )

            # Check if the token has expired
            expiration_time = datetime.utcfromtimestamp(decoded_token['exp'])
            if expiration_time < datetime.utcnow():
                return jsonify({'error': 'Token has expired.'}), 401
        except jwt.exceptions.DecodeError:
            return {'error': 'Invalid token.'}, 401

        return {'token': decoded_token}, 200


if __name__ == '__main__':
    # Run the application
    app.run(host="0.0.0.0", port=5000, debug=True)
