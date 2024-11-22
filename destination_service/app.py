# app.py

from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from routes.destination_routes import register_destination_routes
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS if needed

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

# Configure Swagger UI with Bearer Token Authorization
authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    },
}

# Initialize Flask-RESTX API with security configuration
api = Api(
    app,
    version='1.0',
    title='Destination Service',
    description='Travel Destination Management',
    authorizations=authorizations,
    security='Bearer Auth'  # This makes sure the Authorization header is expected
)

# Register destination routes
register_destination_routes(api)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
