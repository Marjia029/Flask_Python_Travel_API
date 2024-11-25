# services/user_service.py
from datetime import datetime, timedelta
from typing import Dict
import jwt
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash


class UserService:
    @staticmethod
    def generate_token(user_email: str, role: str) -> str:
        payload = {
            'email': user_email,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_token(token: str) -> Dict:
        return jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )

    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password_hash: str, password: str) -> bool:
        return check_password_hash(password_hash, password)
