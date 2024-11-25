import unittest
from unittest.mock import MagicMock
from controllers.user_controller import UserController
from models.user import UserDTO, UserRole


class TestUserController(unittest.TestCase):

    def setUp(self):
        # Mock dependencies
        self.mock_user_repository = MagicMock()
        self.mock_user_service = MagicMock()
        
        # Create controller instance with mocked dependencies
        self.controller = UserController(
            self.mock_user_repository, 
            self.mock_user_service
        )

    def test_register_user_success(self):
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User',
            'role': 'user'  # Adjusted to match the actual UserRole enum value
        }
        self.mock_user_service.hash_password.return_value = 'hashed_password'
        self.mock_user_repository.create_user.return_value = None

        # Act
        response, status_code = self.controller.register_user(data)

        # Debugging logs
        print("Response:", response)
        print("Status Code:", status_code)

        # Assert
        self.assertEqual(status_code, 201)
        self.assertEqual(response['message'], 'User registered successfully')
        self.mock_user_repository.create_user.assert_called_once()
        self.mock_user_service.hash_password.assert_called_once_with(
            data['password']
        )

    def test_register_user_missing_fields(self):
        # Arrange
        data = {'email': 'test@example.com'}

        # Act
        response, status_code = self.controller.register_user(data)

        # Assert
        self.assertEqual(status_code, 400)
        self.assertEqual(response['message'], 'Missing required fields')

    def test_register_user_invalid_role(self):
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User',
            'role': 'invalid_role'
        }

        # Act
        response, status_code = self.controller.register_user(data)

        # Assert
        self.assertEqual(status_code, 400)
        self.assertIn('Invalid role', response['message'])

    def test_login_user_success(self):
        # Arrange
        data = {'email': 'test@example.com', 'password': 'password123'}
        mock_user = UserDTO(
            email='test@example.com',
            name='Test User',
            role=UserRole.USER,
            password_hash='hashed_password'
        )
        self.mock_user_repository.get_user.return_value = mock_user
        self.mock_user_service.verify_password.return_value = True
        self.mock_user_service.generate_token.return_value = 'mock_token'

        # Act
        response, status_code = self.controller.login_user(data)

        # Assert
        self.assertEqual(status_code, 200)
        self.assertIn('token', response)
        self.mock_user_repository.get_user.assert_called_once_with(
            data['email']
        )
        self.mock_user_service.verify_password.assert_called_once_with(
            'hashed_password', data['password']
        )
        self.mock_user_service.generate_token.assert_called_once_with(
            mock_user.email, mock_user.role.value
        )

    def test_login_user_invalid_credentials(self):
        # Arrange
        data = {'email': 'test@example.com', 'password': 'wrongpassword'}
        mock_user = UserDTO(
            email='test@example.com',
            name='Test User',
            role=UserRole.USER,
            password_hash='hashed_password'
        )
        self.mock_user_repository.get_user.return_value = mock_user
        self.mock_user_service.verify_password.return_value = False

        # Act
        response, status_code = self.controller.login_user(data)

        # Assert
        self.assertEqual(status_code, 401)
        self.assertEqual(response['message'], 'Invalid credentials')

    def test_get_all_users_success(self):
        # Arrange
        mock_users = [
            UserDTO(
                email='user1@example.com',
                name='User One',
                role=UserRole.ADMIN,
                password_hash='hash1'
            ),
            UserDTO(
                email='user2@example.com',
                name='User Two',
                role=UserRole.USER,
                password_hash='hash2'
            )
        ]
        self.mock_user_repository.get_all_users.return_value = mock_users

        # Act
        response, status_code = self.controller.get_all_users()

        # Assert
        self.assertEqual(status_code, 200)
        self.assertIn('user1@example.com', response)
        self.assertIn('user2@example.com', response)

    def test_get_user_profile_success(self):
        # Arrange
        token = 'mock_token'
        self.mock_user_service.verify_token.return_value = {
            'email': 'test@example.com'
        }
        mock_user = UserDTO(
            email='test@example.com',
            name='Test User',
            role=UserRole.USER,
            password_hash='hashed_password'
        )
        self.mock_user_repository.get_user.return_value = mock_user

        # Act
        response, status_code = self.controller.get_user_profile(token)

        # Assert
        self.assertEqual(status_code, 200)
        self.assertEqual(response['email'], mock_user.email)
        self.mock_user_service.verify_token.assert_called_once_with(token)
        self.mock_user_repository.get_user.assert_called_once_with(
            'test@example.com'
        )

    def test_get_user_profile_user_not_found(self):
        # Arrange
        token = 'mock_token'
        self.mock_user_service.verify_token.return_value = {
            'email': 'unknown@example.com'
        }
        self.mock_user_repository.get_user.return_value = None

        # Act
        response, status_code = self.controller.get_user_profile(token)

        # Assert
        self.assertEqual(status_code, 404)
        self.assertEqual(response['message'], 'User not found')


if __name__ == "__main__":
    unittest.main()
