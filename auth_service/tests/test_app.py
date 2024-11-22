import unittest
from app import app
import jwt
from datetime import datetime, timedelta, timezone


class AuthServiceTests(unittest.TestCase):

    def setUp(self):
        """Set up test client and test data."""
        self.app = app.test_client()
        self.app.testing = True
        self.secret_key = app.config['SECRET_KEY']

    def generate_token(self, role=None, expired=False):
        """Helper function to generate test tokens."""
        payload = {
            'user_id': 1,
            'role': role or 'user',
            'exp': datetime.utcnow() + (timedelta(seconds=-1) if expired else timedelta(hours=1))
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def test_validate_token_success(self):
        """Test token validation success."""
        token = self.generate_token()
        response = self.app.get('/auth/validate', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_id', response.json)

    def test_validate_token_missing(self):
        """Test missing token."""
        response = self.app.get('/auth/validate', headers={})
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid Authorization header', response.json['message'])


    def test_validate_token_expired(self):
        """Test expired token."""
        token = self.generate_token(expired=True)
        response = self.app.get('/auth/validate', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn('Token has expired', response.json['message'])

    def test_validate_token_invalid(self):
        """Test invalid token."""
        response = self.app.get('/auth/validate', headers={
            'Authorization': 'Bearer invalidtoken'
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token', response.json['message'])

    def test_token_required_decorator_with_roles(self):
        """Test role-based access control."""
        from app import token_required

        @token_required(roles=['admin'])
        def protected_route():
            return {'message': 'Access granted'}, 200

        # Create a test route
        app.add_url_rule('/protected', 'protected', protected_route)

        # Test with an admin token
        admin_token = self.generate_token(role='admin')
        response = self.app.get('/protected', headers={
            'Authorization': f'Bearer {admin_token}'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Access granted', response.json['message'])

        # Test with a non-admin token
        user_token = self.generate_token(role='user')
        response = self.app.get('/protected', headers={
            'Authorization': f'Bearer {user_token}'
        })
        self.assertEqual(response.status_code, 403)
        self.assertIn('Insufficient permissions', response.json['message'])


if __name__ == '__main__':
    unittest.main()
