from flask import Flask, jsonify


app = Flask(__name__)


destinations = [
    {"id": 1, "name": "Paris", "description": "City of lights",
     "location": "France", "price_per_night": 150.0},
    {"id": 2, "name": "New York", "description": "The Big Apple",
     "location": "USA", "price_per_night": 200.0},
]


# Define a route for the root path
@app.route('/')
def home():
    return "Welcome to the Travel API!"


@app.route('/destinations', methods=['GET'])
def get_destinations():
    return jsonify(destinations), 200


@app.route('/destinations/<int:id>', methods=['DELETE'])
def delete_destination(id):
    global destinations
    destinations = [dest for dest in destinations if dest["id"] != id]
    return jsonify({"message": "Destination deleted"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
