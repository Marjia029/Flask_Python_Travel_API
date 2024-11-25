import unittest
from models.destination import Destination


class TestDestinationModel(unittest.TestCase):
    def setUp(self):
        """Set up a sample destination object for testing."""
        self.destination = Destination(
            id=1,
            name="Paris",
            description="The city of light and love.",
            location="France",
            price_per_night=200.0
        )

    def test_destination_initialization(self):
        """Test the initialization of the Destination object."""
        self.assertEqual(self.destination.id, 1)
        self.assertEqual(self.destination.name, "Paris")
        self.assertEqual(
            self.destination.description, "The city of light and love."
        )
        self.assertEqual(self.destination.location, "France")
        self.assertEqual(self.destination.price_per_night, 200.0)

    def test_to_dict_method(self):
        """Test the to_dict method of the Destination class."""
        expected_dict = {
            'id': 1,
            'name': "Paris",
            'description': "The city of light and love.",
            'location': "France",
            'price_per_night': 200.0
        }
        self.assertEqual(self.destination.to_dict(), expected_dict)

    def test_to_dict_method_edge_case(self):
        """Test to_dict for edge cases with empty strings and zero price."""
        destination = Destination(
            id=2,
            name="",
            description="",
            location="",
            price_per_night=0.0
        )
        expected_dict = {
            'id': 2,
            'name': "",
            'description': "",
            'location': "",
            'price_per_night': 0.0
        }
        self.assertEqual(destination.to_dict(), expected_dict)


if __name__ == '__main__':
    unittest.main()
