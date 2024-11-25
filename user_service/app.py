# app.py
import logging
from flask import Flask
from flask_restx import Api
from config import DevelopmentConfig
from repositories.user_repository import UserRepository
from services.user_service import UserService
from controllers.user_controller import UserController
from routes.user_routes import setup_user_routes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    authorizations = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    }

    api = Api(
        app,
        version='1.0',
        title='User Service API',
        description='User Management Service',
        authorizations=authorizations,
        security='Bearer Auth'
    )

    # Initialize components
    user_repository = UserRepository('users.py')
    user_service = UserService()
    user_controller = UserController(user_repository, user_service)

    # Setup routes
    setup_user_routes(api, user_controller, user_service)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=5003)
