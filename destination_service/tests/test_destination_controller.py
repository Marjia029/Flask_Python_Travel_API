import unittest
from unittest.mock import MagicMock, ANY
from flask_restx import Api, Model
from controllers.destination_controller import DestinationController
from models.destination_repository import DestinationRepository
from services.auth_service import AuthService


class TestDestinationController(unittest.TestCase):
    def setUp(self):
        """Set up a mock API and controller for testing."""
        self.mock_api = MagicMock(spec=Api)

        # Mock the `model` method and its return value
        self.mock_api.model = MagicMock(return_value=MagicMock(spec=Model))

        self.controller = DestinationController(self.mock_api)

    def test_initialization(self):
        """Test that the controller initializes with the correct attributes."""
        self.assertIsInstance(
            self.controller.repository, DestinationRepository
        )
        self.assertEqual(self.controller.api, self.mock_api)

    def test_destination_model_definition(self):
        """Test that the Swagger model is defined correctly."""
        # Ensure that the `model` method is called with the correct arguments
        self.mock_api.model.assert_called_with(
            'Destination',
            {
                'id': ANY,  # Match any fields.String object
                'name': ANY,
                'description': ANY,
                'location': ANY,
                'price_per_night': ANY,
            }
        )


if __name__ == '__main__':
    unittest.main()
