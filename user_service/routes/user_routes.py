from functools import wraps
from typing import Optional, Dict, Any
from flask import request
from flask_restx import Namespace, Resource, fields
import jwt
from controllers.user_controller import UserController
from services.user_service import UserService
from models.user import UserRole


def setup_user_routes(api, user_controller: UserController, user_service: UserService):
    """
    Setup user-related routes with Swagger documentation.
    
    Args:
        api: Flask-RESTX API instance
        user_controller: Controller handling user operations
        user_service: Service handling user business logic
    
    Returns:
        Namespace: Flask-RESTX namespace containing user routes
    """
    user_ns = api.namespace(
        'user',
        description='User management operations including registration, login, and profile management'
    )

    def token_required(roles: Optional[list] = None):
        """
        Decorator for JWT token validation and role-based access control.
        
        Args:
            roles: Optional list of allowed roles
            
        Returns:
            Callable: Decorated function with token validation
        """
        def decorator(func):
            @wraps(func)
            def decorated(*args, **kwargs):
                try:
                    auth_header = request.headers.get('Authorization', '')
                    if not auth_header:
                        raise jwt.InvalidTokenError("Missing token")
                    token = auth_header.split(' ')[1]
                    data = user_service.verify_token(token)
                    if roles and data['role'] not in roles:
                        return {'message': 'Insufficient permissions'}, 403
                    return func(*args, **kwargs)
                except jwt.ExpiredSignatureError:
                    return {'message': 'Token has expired'}, 401
                except (jwt.InvalidTokenError, IndexError) as e:
                    return {'message': f'Invalid token: {str(e)}'}, 401
            return decorated
        return decorator

    # Response Models
    error_response = user_ns.model('ErrorResponse', {
        'message': fields.String(
            description='Error message',
            example='Invalid credentials'
        )
    })

    token_response = user_ns.model('TokenResponse', {
        'token': fields.String(
            description='JWT access token',
            example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        ),
        'role': fields.String(example='user')
    })

    user_profile_response = user_ns.model('UserProfileResponse', {
        'user@gmail.com': fields.Nested(user_ns.model('UserProfile', {
            'name': fields.String(example='John Doe'),
            'role': fields.String(example='user')
        }))
    })

    # Request Models
    user_model = api.model('UserRegistration', {
        'email': fields.String(
            required=True,
            description='User email address',
            example='john.doe@example.com'
        ),
        'password': fields.String(
            required=True,
            description='User password (min 8 characters)',
            example='SecureP@ssw0rd'
        ),
        'name': fields.String(
            required=True,
            description='User full name',
            example='John Doe'
        ),
        'role': fields.String(
            required=True,
            description='User role',
            enum=[role.value for role in UserRole],
            example='user'
        )
    })

    login_model = api.model('Login', {
        'email': fields.String(
            required=True,
            description='User email address',
            example='john.doe@example.com'
        ),
        'password': fields.String(
            required=True,
            description='User password',
            example='SecureP@ssw0rd'
        )
    })

    @user_ns.route('/register')
    class UserRegistration(Resource):
        @api.expect(user_model)
        @api.response(201, 'User successfully created', user_profile_response)
        @api.response(400, 'Validation Error', error_response)
        @api.response(409, 'User already exists', error_response)
        def post(self) -> Dict[str, Any]:
            """
            Register a new user
            
            Creates a new user account with the provided details
            and returns a JWT token.
            Password must be at least 8 characters long and contain
            at least one uppercase letter,
            one lowercase letter, one number, and one special character.
            """
            return user_controller.register_user(request.json)

    @user_ns.route('/login')
    class UserLogin(Resource):
        @api.expect(login_model)
        @api.response(200, 'Login successful', token_response)
        @api.response(401, 'Invalid credentials', error_response)
        def post(self) -> Dict[str, Any]:
            """
            Authenticate user and return token
            
            Validates user credentials and returns a JWT token for
            authenticated requests.
            The token should be included in the Authorization header of
            subsequent requests
            using the Bearer scheme.
            """
            return user_controller.login_user(request.json)

    @user_ns.route('/list')
    class UserList(Resource):
        @api.doc(security='Bearer Auth')
        @token_required(roles=[UserRole.ADMIN.value])
        @api.response(200, 'Success', [user_profile_response])
        @api.response(401, 'Authentication error', error_response)
        @api.response(403, 'Insufficient permissions', error_response)
        def get(self) -> Dict[str, Any]:
            """
            Get all users (Admin only)
            
            Returns a list of all registered users.
            This endpoint is restricted to
            administrators only and requires a valid JWT token with admin role.
            """
            return user_controller.get_all_users()

    @user_ns.route('/profile')
    class UserProfile(Resource):
        @api.doc(security='Bearer Auth')
        @token_required()
        @api.response(200, 'Success', user_profile_response)
        @api.response(401, 'Authentication error', error_response)
        def get(self) -> Dict[str, Any]:
            """
            Get current user profile
            Returns the profile information of the
            currently authenticated user.
            Requires a valid JWT token in the Authorization header.
            """
            token = request.headers['Authorization'].split(' ')[1]
            return user_controller.get_user_profile(token)

    return user_ns
