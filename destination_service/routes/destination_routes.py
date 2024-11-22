# routes/destination_routes.py

from flask import request
from flask_restx import Namespace, Resource
from services.auth_service import AuthService
from models.destination_repository import DestinationRepository

def register_destination_routes(api):
    ns = Namespace('destinations', description='Destination operations')
    api.add_namespace(ns)

    repository = DestinationRepository()
    auth_service = AuthService()

    @ns.route('/')
    class DestinationList(Resource):
        def get(self):
            """Retrieve all destinations"""
            return repository.get_all(), 200

    @ns.route('/<string:destination_id>')
    class DestinationResource(Resource):
        @api.doc(security='Bearer Auth')  # Enable Swagger UI with Bearer Auth option
        def delete(self, destination_id):
            """Delete a destination (Admin only)"""
            # Extract token from Authorization header
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return {'message': 'Invalid authorization header'}, 401

            token = auth_header.split(' ')[1]

            # Validate the admin token
            if not auth_service.validate_admin_token(token):
                return {'message': 'Admin access required'}, 403

            # Perform the delete operation
            if repository.delete(destination_id):
                return {'message': 'Destination deleted'}, 200

            return {'message': 'Destination not found'}, 404
