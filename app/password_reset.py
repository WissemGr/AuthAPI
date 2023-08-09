import os
import jwt
from flask import Blueprint, request, jsonify
from flask_mail import Mail, Message
from app.models import db, User
from werkzeug.security import generate_password_hash
from flask_restx import Namespace, Resource
# Create the API blueprint
password_reset_api = Blueprint('password_reset_api', __name__)

# password_reset.py
#@app.route('/password-reset/forget-password', methods=['POST'])
@password_reset_api.route('/forget-password', methods=['POST'])
def send_forgot_password_email():
    """
    Endpoint to send a reset password email to the user's email address.
    """
    # Get the email from the request payload
    email = request.json.get('email')

    # Check if the email is valid and registered in the database
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({'message': 'No record found with this email. Please signup first.'}), 404

    # Generate a password reset token
    token = jwt.encode({'user_id': user.id}, 'your-secret-key', algorithm='HS256')

    # Compose the email message
    mail_subject = "Reset your password"
    # domain = os.environ.get("API_URL")
    # domain =  reset_password_link = f"{domain}/pages/auth/reset-password/{user.id}/{token}"

    # Prepare the email message
    reset_password_link = f"http://localhost:5000/pages/auth/reset-password/{user.id}/{token}"
    msg = Message(
        mail_subject,
        sender="authapi5@gmail.com",
        recipients=[user.email]
    )
    msg.html = f"Please click on the link to reset your password: {reset_password_link}"

    # Send the email
    try:
        mail.send(msg)
        return jsonify({'message': 'Password reset link sent to your email address.'}), 200
    except Exception as e:
        return jsonify({'error': f"Error sending email: {str(e)}"}), 500
#app.route('/password-reset/reset-password/<string:token>', methods=['POST'])
@password_reset_api.route('/reset-password/<string:token>', methods=['POST'])
def reset_password(token):
    """
    Endpoint to reset the user's password with the provided reset token.
    """
    # Get the new password from the request payload
    new_password = request.json.get('new_password')

    # Check if the reset token is valid
    try:
        user.password = generate_password_hash(new_password).decode("utf-8")
        db.session.commit()
        return jsonify({'message': 'Password successfully reset.'}), 200
    except Exception as e:
        return jsonify({'error': f"Error resetting password: {str(e)}"}), 500