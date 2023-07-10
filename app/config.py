import os


# Set up the database configuration and connection string
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/auth')
SQLALCHEMY_TRACK_MODIFICATIONS = False
