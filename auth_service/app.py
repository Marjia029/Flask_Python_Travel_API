from flask import Flask, jsonify, request
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

SECRET_KEY = "your_secret_key"


def generate_token(user):
    """Generate a JWT token."""
    payload = {
        "sub": user["email"],
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def decode_token(token):
    """Decode a JWT token."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


@app.route('/generate-token', methods=['POST'])
def create_token():
    """Generate a token for the user."""
    user = request.json
    token = generate_token(user)
    return jsonify({"token": token}), 200


@app.route('/validate-token', methods=['POST'])
def validate_token():
    """Validate the JWT token."""
    token = request.json.get("token")
    decoded = decode_token(token)
    if "error" in decoded:
        return jsonify(decoded), 401
    return jsonify({"message": "Token is valid"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
