import os
import json
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
    title='Authorization Service',
    description='Authentication and Authorization Service',
    authorizations=authorizations,
    security='Bearer Auth'
)

# Namespace
auth_ns = api.namespace('auth', description='Authorization operations')


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
    app.run(port=5006, debug=True)
