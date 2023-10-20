import jwt
from app.config import *
from datetime import datetime
from flask import request, jsonify
from app.models import user_model
from flask_restx import Resource, Namespace

# Password Reset API
protected_ns = Namespace('protected', description='Protected APIs')

api_user_model = protected_ns.model('User', user_model)

@protected_ns.route('/protected')
class ProtectedResource(Resource):
    @protected_ns.expect(api_user_model, validate=True)
    @protected_ns.doc(security='Bearer Token')
    def post(self):
        """
        Protected resource that requires authentication.
        """
        # Access the decoded token from the request headers
        bearer = request.headers.get('Authorization')
        if not bearer:
            return jsonify({'error': 'Authorization header is missing.'}), 401

        token = bearer.split(' ')[1]

        try:
            # Decode the token and verify its authenticity
            decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])

            # Check if the token has expired
            expiration_time = datetime.utcfromtimestamp(decoded_token['exp'])
            if expiration_time < datetime.utcnow():
                return jsonify({'error': 'Token has expired.'}), 401
        except jwt.exceptions.DecodeError:
            return jsonify({'error': 'Invalid token'}), 401

        return {'token': decoded_token}, 200
