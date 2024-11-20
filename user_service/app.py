from flask import Flask, jsonify, request

app = Flask(__name__)

# Mock user database
users = []


@app.route('/register', methods=['POST'])
def register_user():
    """Register a new user."""
    data = request.json
    if not all(k in data for k in ("name", "email", "password", "role")):
        return jsonify({"error": "Missing fields"}), 400

    users.append(data)
    return jsonify({"message": "User registered successfully"}), 201


@app.route('/login', methods=['POST'])
def login_user():
    """Authenticate a user and provide an access token."""
    data = request.json
    user = next(
        (
            u for u in users
            if u["email"] == data["email"]
            and u["password"] == data["password"]
        ),
        None
    )
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify({"message": "Login successful",
                    "token": "dummy_token"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
