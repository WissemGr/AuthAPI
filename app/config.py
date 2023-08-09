import os
import secrets


# Set up the database configuration and connection string
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://ons:ons@localhost:5432/auth')
SQLALCHEMY_TRACK_MODIFICATIONS = False
#generate a secret thta will be used in coding and decodin all jwt tokens used in this app
secret_key = secrets.token_hex(32)