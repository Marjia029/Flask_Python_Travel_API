from functools import wraps
from typing import Optional
from flask import request
from flask_restx import Namespace, Resource, fields
import jwt
from controllers.user_controller import UserController
from services.user_service import UserService
from models.user import UserRole

def setup_user_routes(api, user_controller: UserController, user_service: UserService):
    user_ns = api.namespace('user', description='User operations')

    def token_required(roles: Optional[list] = None):
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

    user_model = api.model('User', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password'),
        'name': fields.String(required=True, description='User full name'),
        'role': fields.String(
            required=True,
            description='User role',
            enum=[role.value for role in UserRole]
        )
    })

    @user_ns.route('/register')
    class UserRegistration(Resource):
        @api.expect(user_model)
        def post(self):
            """Register a new user"""
            return user_controller.register_user(request.json)

    @user_ns.route('/login')
    class UserLogin(Resource):
        @api.expect(api.model('Login', {
            'email': fields.String(required=True),
            'password': fields.String(required=True)
        }))
        def post(self):
            """Authenticate user and return token"""
            return user_controller.login_user(request.json)

    @user_ns.route('/list')
    class UserList(Resource):
        @token_required(roles=[UserRole.ADMIN.value])
        def get(self):
            """Get all users (Admin only)"""
            return user_controller.get_all_users()

    @user_ns.route('/profile')
    class UserProfile(Resource):
        @token_required()
        def get(self):
            """Get current user profile"""
            token = request.headers['Authorization'].split(' ')[1]
            return user_controller.get_user_profile(token)


    return user_ns