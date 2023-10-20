import jwt
from app.config import secret_key
from flask import Flask,request
from flask_restx import Resource, Namespace
from app.authorizations import json as authorizations


# Create a Flask application
app = Flask(__name__)

verify_ns = Namespace('verify', description='Token verification operations',authorizations=authorizations)

@verify_ns.route('/')
class TokenVerification(Resource):
    @verify_ns.doc(security='Bearer Token')
    def post(self):
        """
        Verify a JWT token.
        """
        # Retrieve the token from the request
        token = request.headers.get('Authorization')

        if not token:
            return {'error': 'Token is missing from the request headers.'}, 401

        # Remove the 'Bearer ' prefix if present
        token = token.replace('Bearer ', '')

        try:
            # Verify the token using the secret_key
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return {
                'user_id': payload['user_id'],
                'token_expiration': payload['exp']
            }, 200
        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired.'}, 401
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token.'}, 401
