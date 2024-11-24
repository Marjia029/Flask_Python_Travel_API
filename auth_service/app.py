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
        'name': 'Authorization',
        'description': 'Enter your Bearer token in the format: Bearer <token>'
    }
}

# Initialize API with authorization
api = Api(
    app,
    version='1.0',
    title='Authorization Service',
    description='A service for handling authentication and authorization with JWT tokens',
    authorizations=authorizations,
    security='Bearer Auth'
      # Swagger UI will be available at /docs
)

# Namespace
auth_ns = api.namespace(
    'auth',
    description='Authorization operations including token validation'
)

# Define models for Swagger documentation
token_response = auth_ns.model('TokenResponse', {
    'email': fields.String(
        description='User email',
        example='user@example.com'
    ),
    
    'role': fields.String(
        description='User role',
        example='admin'
    ),
    'exp': fields.Integer(
        description='Token issued at timestamp',
        example=1735603200
    )
})

error_response = auth_ns.model('ErrorResponse', {
    'message': fields.String(
        description='Error message',
        example='Token has expired'
    )
})


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
    @auth_ns.doc(
        description='Validate a JWT token and return its decoded contents',
        responses={
            200: ('Token is valid', token_response),
            401: ('Authentication error', error_response)
        }
    )
    @auth_ns.doc(security='Bearer Auth')
    def get(self) -> Union[Dict, tuple]:
        """
        Validate JWT Token
        
        This endpoint validates the provided JWT token and returns its decoded contents
        if valid. The token should be provided in the Authorization header using the
        Bearer <token>.
        
        Returns:
            Union[Dict, tuple]: Decoded token data or error message with status code
        """
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