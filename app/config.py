import os
import secrets


# Set up the database configuration and connection string
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://auth:auth@localhost:5432/auth')
SQLALCHEMY_TRACK_MODIFICATIONS = False
#generate a secret thta will be used in coding and decodin all jwt tokens used in this app
secret_key = secrets.token_hex(32)

# Set up email configuration with default values
mail_server = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
mail_port = int(os.environ.get("MAIL_PORT", 465))  # Default to 465
mail_username = os.environ.get("MAIL_USERNAME", "authapi5")
mail_password = os.environ.get("MAIL_PASSWORD", "")
mail_use_tls = os.environ.get("MAIL_USE_TLS", "False").lower() == "true"
mail_use_ssl = os.environ.get("MAIL_USE_SSL", "True").lower() == "true"