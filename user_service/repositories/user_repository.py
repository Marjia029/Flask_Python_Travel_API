# repositories/user_repository.py
import os
import logging
from typing import Dict, List, Optional
from models.user import UserDTO, UserRole

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.users: Dict[str, UserDTO] = {}
        self._load_users()

    def _load_users(self) -> None:
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as file:
                    content = file.read()
                    users_dict = eval(content.split('=')[1].strip())
                    self.users = {
                        email: UserDTO(
                            email=email,
                            name=user['name'],
                            role=UserRole(user['role']),
                            password_hash=user['password']
                        )
                        for email, user in users_dict.items()
                    }
                logger.info(f"Successfully loaded {len(self.users)} users")
        except Exception as e:
            logger.error(f"Error loading users: {str(e)}")
            self.users = {}

    def save_users(self) -> None:
        try:
            users_dict = {
                user.email: {
                    'name': user.name,
                    'password': user.password_hash,
                    'role': user.role.value
                }
                for user in self.users.values()
            }
            with open(self.file_path, 'w') as file:
                file.write(f"users = {repr(users_dict)}")
            logger.info("Users saved successfully")
        except Exception as e:
            logger.error(f"Error saving users: {str(e)}")
            raise

    def get_user(self, email: str) -> Optional[UserDTO]:
        return self.users.get(email)

    def create_user(self, user: UserDTO) -> None:
        if self.get_user(user.email):
            raise ValueError("User already exists")
        self.users[user.email] = user
        self.save_users()

    def get_all_users(self) -> List[UserDTO]:
        return list(self.users.values())