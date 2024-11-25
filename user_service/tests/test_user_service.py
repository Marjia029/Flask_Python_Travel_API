import unittest
from unittest.mock import patch
from flask import Flask
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash

from services.user_service import UserService


class TestUserService(unittest.TestCase):

    def setUp(self):
        # Setting up a test Flask application
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        self.test_email = "test@example.com"
        self.test_role = "user"
        self.test_password = "password123"
        self.hashed_password = generate_password_hash(self.test_password)

        # Activate the app context for testing
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        # Teardown the app context after tests
        self.app_context.pop()

    def test_generate_token(self):
        # Test the token generation
        token = UserService.generate_token(self.test_email, self.test_role)
        self.assertIsInstance(token, str)

        decoded_token = jwt.decode(
            token,
            self.app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        self.assertEqual(decoded_token['email'], self.test_email)
        self.assertEqual(decoded_token['role'], self.test_role)
        self.assertIn('exp', decoded_token)

    def test_verify_token(self):
        # Test token verification
        token = UserService.generate_token(self.test_email, self.test_role)
        decoded_token = UserService.verify_token(token)
        self.assertEqual(decoded_token['email'], self.test_email)
        self.assertEqual(decoded_token['role'], self.test_role)
        self.assertIn('exp', decoded_token)

    def test_hash_password(self):
        # Test password hashing
        hashed_password = UserService.hash_password(self.test_password)
        self.assertNotEqual(self.test_password, hashed_password)

        # Verify that the hashed password works with the password verifier
        self.assertTrue(UserService.verify_password(
            hashed_password,
            self.test_password
        ))

    def test_verify_password(self):
        # Test password verification
        is_valid = UserService.verify_password(
            self.hashed_password,
            self.test_password
        )
        self.assertTrue(is_valid)

        is_invalid = UserService.verify_password(
            self.hashed_password,
            "wrongpassword"
        )
        self.assertFalse(is_invalid)


if __name__ == "__main__":
    unittest.main()
