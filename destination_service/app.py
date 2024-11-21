import os
import requests
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

# Configure Swagger UI with security definitions
authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    },
}

api = Api(app, 
          version='1.0', 
          title='Destination Service',
          description='Travel Destination Management',
          authorizations=authorizations,
          security='Bearer Auth')  # Default security scheme

# Namespace
dest_ns = api.namespace('destinations', description='Destination operations')

# Destination Model
destination_model = api.model('Destination', {
    'id': fields.String(required=True, description='Destination unique identifier'),
    'name': fields.String(required=True, description='Destination name'),
    'description': fields.String(required=True, description='Short description'),
    'location': fields.String(required=True, description='Location name'),
    'price_per_night': fields.Float(required=True, description='Cost per night')
})

# In-memory destination storage (replace with database in production)
destinations = {
    '1': {
        'id': '1',
        'name': 'Maldives Resort',
        'description': 'Luxurious tropical paradise',
        'location': 'Maldives',
        'price_per_night': 500.00
    },
    '2': {
        'id': '2',
        'name': 'Tokyo City Hotel',
        'description': 'Modern urban experience',
        'location': 'Japan',
        'price_per_night': 250.00
    }
}

def validate_admin_token(token):
    """Validate admin token with Authentication Service"""
    try:
        response = requests.get(
            'http://localhost:5003/user/validate',
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        return data.get('role') == 'Admin'
    except Exception:
        return False

@dest_ns.route('/')
class DestinationList(Resource):
    def get(self):
        """Retrieve all destinations"""
        return list(destinations.values()), 200

    @api.doc(security='Bearer Auth')
    @api.expect(destination_model)
    def post(self):
        """Add a new destination (Admin only)"""
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return {'message': 'Invalid authorization header'}, 401
        
        token = auth_header.split(' ')[1]
        
        if not validate_admin_token(token):
            return {'message': 'Admin access required'}, 403
        
        data = request.json
        # Ensure the data includes an ID
        if 'id' not in data:
            data['id'] = str(len(destinations) + 1)
        
        destinations[data['id']] = data
        return {'message': 'Destination added', 'id': data['id']}, 201

@dest_ns.route('/<string:destination_id>')
class DestinationResource(Resource):
    def get(self, destination_id):
        """Retrieve a specific destination"""
        destination = destinations.get(destination_id)
        if destination:
            return destination, 200
        return {'message': 'Destination not found'}, 404

    @api.doc(security='Bearer Auth')
    def delete(self, destination_id):
        """Delete a destination (Admin only)"""
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return {'message': 'Invalid authorization header'}, 401
        
        token = auth_header.split(' ')[1]
        
        if not validate_admin_token(token):
            return {'message': 'Admin access required'}, 403
        
        if destination_id in destinations:
            del destinations[destination_id]
            return {'message': 'Destination deleted'}, 200
        return {'message': 'Destination not found'}, 404

if __name__ == '__main__':
    app.run(port=5001, debug=True)