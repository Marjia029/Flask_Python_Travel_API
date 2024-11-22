# services/auth_service.py

import requests

class AuthService:
    @staticmethod
    def validate_admin_token(token):
        try:
            response = requests.get(
                'http://localhost:5006/auth/validate',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = response.json()
            return data.get('role') == 'Admin'
        except Exception as e:
            print("Error:", e)
            return False
