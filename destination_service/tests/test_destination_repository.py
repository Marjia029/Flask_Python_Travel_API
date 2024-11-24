import unittest
from models.destination_repository import DestinationRepository


class TestDestinationRepository(unittest.TestCase):
    def setUp(self):
        """Set up a repository with initial data."""
        self.repo = DestinationRepository()

    def test_get_all(self):
        """Test that all destinations are returned."""
        expected_destinations = [
            {'id': '1', 'name': 'Maldives Resort', 'description': 'Luxurious tropical paradise', 'location': 'Maldives', 'price_per_night': 500.00},
            {'id': '2', 'name': 'Tokyo City Hotel', 'description': 'Modern urban experience', 'location': 'Japan', 'price_per_night': 250.00}
        ]
        self.assertEqual(self.repo.get_all(), expected_destinations)

    def test_delete_existing(self):
        """Test deleting an existing destination."""
        deleted_destination = self.repo.delete('1')
        expected_deleted = {'id': '1', 'name': 'Maldives Resort', 'description': 'Luxurious tropical paradise', 'location': 'Maldives', 'price_per_night': 500.00}
        self.assertEqual(deleted_destination, expected_deleted)

        # Check that the destination is no longer in the repository
        remaining_destinations = self.repo.get_all()
        expected_remaining = [
            {'id': '2', 'name': 'Tokyo City Hotel', 'description': 'Modern urban experience', 'location': 'Japan', 'price_per_night': 250.00}
        ]
        self.assertEqual(remaining_destinations, expected_remaining)

    def test_delete_nonexistent(self):
        """Test deleting a destination that doesn't exist."""
        deleted_destination = self.repo.delete('3')
        self.assertIsNone(deleted_destination)


if __name__ == '__main__':
    unittest.main()
