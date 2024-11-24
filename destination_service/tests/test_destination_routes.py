import unittest
from unittest.mock import patch, MagicMock
from app import app


class TestDestinationRoutes(unittest.TestCase):
    def setUp(self):
        """Set up the test client."""
        self.client = app.test_client()
        self.client.testing = True

    @patch('routes.destination_routes.DestinationRepository')
    @patch('routes.destination_routes.AuthService')
    def test_delete_destination_success(self, mock_auth_service, mock_repository):
        """Test successful deletion of a destination by an admin."""
        # Mock admin token validation
        mock_auth_service.return_value.validate_admin_token.return_value = True

        # Mock the repository's delete method
        mock_repository.return_value.delete.return_value = True

        response = self.client.delete('/destinations/1', headers={
            'Authorization': 'Bearer valid_admin_token'
        })
        print("Response JSON:", response.json)  # Debugging output
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Destination deleted')

    @patch('routes.destination_routes.DestinationRepository')
    @patch('routes.destination_routes.AuthService')
    def test_delete_destination_not_found(self, mock_auth_service, mock_repository):
        """Test deletion attempt for a non-existent destination."""
        # Mock admin token validation
        mock_auth_service.return_value.validate_admin_token.return_value = True

        # Mock the repository's delete method to return None
        mock_repository.return_value.delete.return_value = None

        response = self.client.delete('/destinations/99', headers={
            'Authorization': 'Bearer valid_admin_token'
        })
        print("Response JSON:", response.json)  # Debugging output
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], 'Destination not found')


if __name__ == '__main__':
    unittest.main()
