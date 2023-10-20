import jwt
import logging
from app.config import secret_key
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from app.models import db, user_model, login_model, User
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask_mail import Mail, Message
from flask_restx import Api, Resource,Namespace, reqparse


# Create the Flask application
app = Flask(__name__)
mail = Mail(app)
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

        # Check if the email is alfready registered
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
#reset paswsord code starts here 
#mail server config 
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "authapi5"  # Replace with your email username
app.config["MAIL_PASSWORD"] = "udxqoqjwgpqkfdgk"  # Replace with your genearated email password
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)

# Password Reset API
password_reset_api = Namespace('password-reset', description='Password reset operations')
# send reset password email function that will be used next in the api 
def send_forgot_password_email(email):
    user = User.query.filter_by(email=email).first()

    if user is None:
        return False

    # Generate a password reset token
    token = jwt.encode({'user_id': user.id}, secret_key, algorithm='HS256')

    # Compose the email message
    mail_subject = "Reset your password"
#it does not work this way so i will not send a url only a token for now untill i figure it out 
    #reset_password_link = f"http://localhost:5000/pages/auth/reset-password/{user.id}/{token}"
    reset_password_id_token= f"{user.id}/{token}"
    msg = Message(
        mail_subject,
        sender="authapi5@gmail.com",
        recipients=[user.email]
    )
    msg.html = f"Please use this token ( after / ) to reset your password: {reset_password_id_token}"

    # Send the email
    try:
        mail.send(msg)
        return True
    except Exception as e:
        return False
# Define a request parser for the "forget-password" endpoint
forget_password_parser = reqparse.RequestParser()
forget_password_parser.add_argument('email', type=str, required=True, help='User email')
@password_reset_api.route('/forget-password', methods=['POST'])
class ForgetPassword(Resource):
    @password_reset_api.expect(forget_password_parser)
    def post(self):
        args = forget_password_parser.parse_args()

        # Get the email from the parser arguments
        email = args['email']
        
        if not email:
            return {'message': 'Email field is required.'}, 400

        # Send the forgot password email
        email_sent = send_forgot_password_email(email)

        if email_sent:
            return {'message': 'Password reset link sent to your email address.'}, 200
        else:
            return {'message': 'No record found with this email. Please signup first.'}, 404
# Define a request parser for the "reset-password" endpoint
reset_password_parser = reqparse.RequestParser()
reset_password_parser.add_argument('new_password', type=str, required=True, help='New password')
@password_reset_api.route('/reset-password/<string:token>', methods=['POST'])
class ResetPassword(Resource):
    @password_reset_api.expect(reset_password_parser)
    def post(self, token):
        args = reset_password_parser.parse_args()

        # Get the new password from the parser arguments
        new_password = args['new_password']

        try:
            # Decode the token and get user_id
            decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = decoded_token['user_id']

            # Get the user from the database
            user = User.query.get(user_id)

            # Update the user's password
            
            user.password = generate_password_hash(new_password)
            db.session.commit()

            return {'message': 'Password successfully reset.'}, 200
        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired.'}, 401
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token.'}, 401
        except Exception as e:
            return {'error': f"Error resetting password: {str(e)}"}, 500


# Register the password_reset_api namespace
api.add_namespace(password_reset_api)
# Initialize the Flask Mail extension with the app
mail = Mail(app)
if __name__ == '__main__':
    # Run the application
    app.run(host="0.0.0.0", port=5000, debug=True)