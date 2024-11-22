# controllers/user_controller.py
import logging
from typing import Dict
from services.user_service import UserService
from repositories.user_repository import UserRepository
from models.user import UserDTO, UserRole

logger = logging.getLogger(__name__)

class UserController:
    def __init__(self, user_repository: UserRepository, user_service: UserService):
        self.user_repository = user_repository
        self.user_service = user_service

    def register_user(self, data: Dict) -> tuple:
        try:
            if not all(k in data for k in ['email', 'password', 'name', 'role']):
                return {'message': 'Missing required fields'}, 400

            try:
                role = UserRole(data['role'])
            except ValueError:
                return {'message': f'Invalid role. Must be one of: {[r.value for r in UserRole]}'}, 400

            user = UserDTO(
                email=data['email'],
                name=data['name'],
                role=role,
                password_hash=self.user_service.hash_password(data['password'])
            )
            
            self.user_repository.create_user(user)
            logger.info(f"User registered: {user.email}")
            return {'message': 'User registered successfully'}, 201
        except ValueError as e:
            return {'message': str(e)}, 409
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return {'message': 'Internal server error'}, 500

    def login_user(self, data: Dict) -> tuple:
        try:
            user = self.user_repository.get_user(data['email'])

            if user and self.user_service.verify_password(
                user.password_hash,
                data['password']
            ):
                token = self.user_service.generate_token(
                    user.email,
                    user.role.value
                )
                return {
                    'token': token,
                    'role': user.role.value
                }, 200

            return {'message': 'Invalid credentials'}, 401
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return {'message': 'Internal server error'}, 500

    def get_all_users(self) -> tuple:
        try:
            users = self.user_repository.get_all_users()
            return {
                user.email: user.to_safe_dict()
                for user in users
            }, 200
        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}")
            return {'message': 'Internal server error'}, 500

    def get_user_profile(self, token: str) -> tuple:
        try:
            data = self.user_service.verify_token(token)
            user = self.user_repository.get_user(data['email'])

            if not user:
                return {'message': 'User not found'}, 404

            return user.to_dict(), 200
        except Exception as e:
            logger.error(f"Profile fetch error: {str(e)}")
            return {'message': 'Internal server error'}, 500

