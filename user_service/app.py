import os
import ast
from functools import wraps
from typing import Dict, Optional, Union

from flask import Flask, request
from flask_restx import Api, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

# Configure Swagger UI Authorization
authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

# Initialize API with authorization
api = Api(
    app,
    version='1.0',
    title='User Service',
    description='Authentication and Authorization Service',
    authorizations=authorizations,
    security='Bearer Auth'
)

# Namespace
auth_ns = api.namespace('user', description='User operations')

# Models
user_model = api.model('User', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'name': fields.String(required=True, description='User full name'),
    'role': fields.String(required=True, description='User role (Admin/User)')
})

USER_FILE = 'users.py'

# Load users from Python file
def load_users() -> Dict[str, Dict[str, str]]:
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, 'r') as file:
                content = file.read()
                # Extract the dictionary from the content
                users_dict = ast.literal_eval(content.split('=')[1].strip())
                return users_dict
        except (FileNotFoundError, SyntaxError, IndexError, ValueError):
            print(f"Error loading users from {USER_FILE}")
            return {}
    return {}

# Global users dictionary
users = load_users()

def save_users():
    """
    Save users to the Python file
    """
    try:
        with open(USER_FILE, 'w') as file:
            # Use repr to create a string representation of the dictionary
            file.write(f"users = {repr(users)}")
        print("Users saved successfully")
    except Exception as e:
        print(f"Error saving users: {e}")

def generate_token(user_email: str, role: str) -> str:
    """
    Generate JWT token for authentication.

    Args:
        user_email (str): Email of the user
        role (str): Role of the user

    Returns:
        str: JWT token
    """
    payload = {
        'email': user_email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def token_required(roles: Optional[list] = None):
    """
    Decorator to validate JWT token and user roles.

    Args:
        roles (Optional[list]): List of allowed roles

    Returns:
        Callable: Decorated function
    """
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            token = None

            if 'Authorization' in request.headers:
                try:
                    token = request.headers['Authorization'].split(' ')[1]
                except IndexError:
                    return {'message': 'Invalid Authorization header format'}, 401

            if not token:
                return {'message': 'Authentication token is missing'}, 401

            try:
                data = jwt.decode(
                    token,
                    app.config['SECRET_KEY'],
                    algorithms=['HS256']
                )

                if roles and data['role'] not in roles:
                    return {'message': 'Insufficient permissions'}, 403

                return func(*args, **kwargs)

            except jwt.ExpiredSignatureError:
                return {'message': 'Token has expired'}, 401
            except jwt.InvalidTokenError:
                return {'message': 'Invalid token'}, 401

        return decorated
    return decorator


@auth_ns.route('/register')
class UserRegistration(Resource):
    @api.expect(user_model)
    def post(self) -> Union[Dict[str, str], tuple]:
        """Register a new user"""
        data = request.json

        # Validate input
        if not all(k in data for k in ('email', 'password', 'name', 'role')):
            return {'message': 'Missing required fields'}, 400

        if data['email'] in users:
            return {'message': 'User already exists'}, 409

        # Hash password
        hashed_password = generate_password_hash(data['password'])

        # Store user
        users[data['email']] = {
            'name': data['name'],
            'password': hashed_password,
            'role': data['role']
        }

        save_users()

        print(f"Registered user: {data['email']} with role {data['role']}")
        print(f"Current users: {users}")

        return {'message': 'User registered successfully'}, 201


@auth_ns.route('/users')
class UserList(Resource):
    @token_required(roles=['Admin'])
    def get(self) -> Dict[str, Dict[str, str]]:
        """
        Retrieve all registered users (Admin only)
        Excludes password for security
        """
        return {
            email: {
                'name': user['name'],
                'role': user['role']
            } for email, user in users.items()
        }


@auth_ns.route('/login')
class UserLogin(Resource):
    @api.expect(api.model('Login', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password')
    }))
    def post(self) -> Union[Dict[str, str], tuple]:
        """Authenticate user and return token"""
        data = request.json

        email = data.get('email')
        password = data.get('password')

        print(f"Login attempt for: {email}")
        print(f"Registered users: {users}")

        user = users.get(email)

        if user and check_password_hash(user['password'], password):
            token = generate_token(email, user['role'])
            return {
                'token': token,
                'role': user['role']
            }, 200

        return {'message': 'Invalid credentials'}, 401


@auth_ns.route('/profile')
class UserProfile(Resource):
    @token_required()
    def get(self) -> Union[Dict[str, str], tuple]:
        """
        Retrieve the profile of the currently authenticated user.
        """
        # Extract the token from the Authorization header
        token = request.headers.get('Authorization', '').split(' ')[1]

        try:
            # Decode the JWT token to get user data
            data = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            user_email = data.get('email')

            # Fetch the user's details from the in-memory storage
            user = users.get(user_email)

            if not user:
                return {'message': 'User not found'}, 404

            # Return user details excluding the password
            return {
                'email': user_email,
                'name': user['name'],
                'role': user['role']
            }, 200

        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401


@auth_ns.route('/validate')
class TokenValidation(Resource):
    def get(self) -> Union[Dict, tuple]:
        """Validate JWT token"""
        try:
            token = request.headers.get('Authorization', '').split(' ')[1]
        except IndexError:
            return {'message': 'Invalid Authorization header'}, 401

        try:
            data = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return data, 200
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401


if __name__ == '__main__':
    # Explicitly load users when the app starts
    users.update(load_users())
    app.run(port=5003, debug=True)