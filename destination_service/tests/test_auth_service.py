import unittest
from unittest.mock import patch
from services.auth_service import AuthService


class TestAuthService(unittest.TestCase):
    @patch('services.auth_service.requests.get')
    def test_validate_admin_token_success(self, mock_get):
        """Test token validation when the user has an Admin role."""
        # Mock the response from requests.get
        mock_get.return_value.json.return_value = {'role': 'Admin'}
        mock_get.return_value.status_code = 200

        token = "valid_admin_token"
        is_admin = AuthService.validate_admin_token(token)

        # Assert that the token is validated and the role is Admin
        self.assertTrue(is_admin)
        mock_get.assert_called_once_with(
            'http://localhost:5006/auth/validate',
            headers={'Authorization': f'Bearer {token}'}
        )

    @patch('services.auth_service.requests.get')
    def test_validate_admin_token_non_admin(self, mock_get):
        """Test token validation when the user does not have an Admin role."""
        mock_get.return_value.json.return_value = {'role': 'User'}
        mock_get.return_value.status_code = 200

        token = "valid_user_token"
        is_admin = AuthService.validate_admin_token(token)

        # Assert that the token is validated but the role is not Admin
        self.assertFalse(is_admin)
        mock_get.assert_called_once_with(
            'http://localhost:5006/auth/validate',
            headers={'Authorization': f'Bearer {token}'}
        )

    @patch('services.auth_service.requests.get')
    def test_validate_admin_token_invalid_token(self, mock_get):
        """Test token validation when an invalid token is provided."""
        mock_get.return_value.json.return_value = {'message': 'Invalid token'}
        mock_get.return_value.status_code = 401

        token = "invalid_token"
        is_admin = AuthService.validate_admin_token(token)

        # Assert that the validation fails for an invalid token
        self.assertFalse(is_admin)
        mock_get.assert_called_once_with(
            'http://localhost:5006/auth/validate',
            headers={'Authorization': f'Bearer {token}'}
        )

    @patch('services.auth_service.requests.get')
    def test_validate_admin_token_exception(self, mock_get):
        """Test token validation when an exception occurs."""
        mock_get.side_effect = Exception("Connection error")

        token = "any_token"
        is_admin = AuthService.validate_admin_token(token)

        # Assert that the validation gracefully handles exceptions
        self.assertFalse(is_admin)
        mock_get.assert_called_once_with(
            'http://localhost:5006/auth/validate',
            headers={'Authorization': f'Bearer {token}'}
        )


if __name__ == '__main__':
    unittest.main()
