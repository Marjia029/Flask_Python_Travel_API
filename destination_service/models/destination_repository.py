# models/destination_repository.py

class DestinationRepository:
    def __init__(self):
        self.destinations = {
            '1': {'id': '1', 'name': 'Maldives Resort', 'description': 'Luxurious tropical paradise', 'location': 'Maldives', 'price_per_night': 500.00},
            '2': {'id': '2', 'name': 'Tokyo City Hotel', 'description': 'Modern urban experience', 'location': 'Japan', 'price_per_night': 250.00}
        }

    def get_all(self):
        return list(self.destinations.values())

    def delete(self, destination_id):
        return self.destinations.pop(destination_id, None)
