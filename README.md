# Flask User Authentication API

This is a Flask-based API for user registration and authentication.

## Prerequisites

- Python 3.x
- PostgreSQL database

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/your-username/flask-user-authentication-api.git
   ```

2. Install the dependencies:

   ```shell
   pip install -r requirements.txt
   ```

3. Set up the PostgreSQL database by updating the `config.py` file with your database credentials.

4. Apply the database migrations:

   ```shell
   flask db upgrade
   ```

## Usage

1. Start the server:

   ```shell
   python app.py
   ```

2. Register a new user:

   ```http
   POST /auth/register
   Content-Type: application/json

   {
     "email": "user@example.com",
     "password": "password123",
     "full_name": "John Doe"
   }
   ```

   Response:

   ```json
   {
     "message": "Registration successful."
   }
   ```

3. Log in with the registered user:

   ```http
   POST /auth/login
   Content-Type: application/json

   {
     "email": "user@example.com",
     "password": "password123"
   }
   ```

   Response:

   ```json
   {
     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   }
   ```

   Note: The token is valid for 1 hour.

## License

This project is licensed under the [MIT License](LICENSE).

