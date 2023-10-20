import jwt
from app.config import *
from flask import Flask
from app.models import db, user_model, User
from werkzeug.security import generate_password_hash
from flask_mail import Mail, Message
from flask_restx import Resource, Namespace, reqparse

# Create a Flask application
app = Flask(__name__)

# Set up email configuration
app.config["MAIL_SERVER"] = mail_server
app.config["MAIL_PORT"] = int(mail_port)  # Make sure to convert to an integer
app.config["MAIL_USERNAME"] = mail_username
app.config["MAIL_PASSWORD"] = mail_password

# Optional: Set TLS and SSL configuration
app.config["MAIL_USE_TLS"] = mail_use_tls == "True"  # Convert to bool
app.config["MAIL_USE_SSL"] = mail_use_ssl == "True"  # Convert to bool

# Initialize the Flask-Mail extension
mail = Mail(app)

# Password Reset API
password_reset_api = Namespace('password-reset', description='Password reset operations')

# Define the user model for API documentation
api_user_model = password_reset_api.model('User', user_model)

# Function to send a reset password email
def send_forgot_password_email(email):
    user = User.query.filter_by(email=email).first()

    if user is None:
        return False

    # Generate a password reset token
    token = jwt.encode({'user_id': user.id}, secret_key, algorithm='HS256')

    # Compose the email message
    mail_subject = "Reset your password"

    # Generate the reset password token (for now, it's just the user ID and token)
    reset_password_id_token = f"{user.id}/{token}"

    msg = Message(
        mail_subject,
        sender="authapi5@gmail.com",
        recipients=[user.email]
    )
    msg.html = f"Please use this token (after /) to reset your password: {reset_password_id_token}"

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
            return {'message': 'No record found with this email. Please sign up first.'}, 404

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
