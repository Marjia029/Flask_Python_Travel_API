# controllers/destination_controller.py

from flask_restx import Resource, fields
from services.auth_service import AuthService
from models.destination_repository import DestinationRepository

class DestinationController:
    def __init__(self, api):
        self.api = api
        self.repository = DestinationRepository()
        self.auth_service = AuthService()

        # Define the Destination model for Swagger
        self.destination_model = api.model('Destination', {
            'id': fields.String(required=True, description='Destination unique identifier'),
            'name': fields.String(required=True, description='Destination name'),
            'description': fields.String(required=True, description='Short description'),
            'location': fields.String(required=True, description='Location name'),
            'price_per_night': fields.Float(required=True, description='Cost per night')
        })
