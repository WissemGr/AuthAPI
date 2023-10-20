# Import necessary modules
import logging
from app.config import *
from app.routes.auth import auth_ns
from app.routes.reset import password_reset_api
from app.routes.protected import protected_ns
from app.authorizations import json as authorizations
from flask import Flask
from app.models import db
from flask_migrate import Migrate
from functools import wraps
from flask_mail import Mail
from flask_restx import Api

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

# Initialize the API
api = Api(app, authorizations=authorizations)
api.add_namespace(auth_ns)
api.add_namespace(protected_ns)
api.add_namespace(password_reset_api)

# Initialize the Flask Mail extension with the app
mail = Mail(app)

# Entry point of the application when run directly
if __name__ == '__main__':
    # Run the application
    app.run(host="0.0.0.0", port=5000, debug=True)
