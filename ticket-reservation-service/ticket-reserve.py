# - id (autogen)
# - source (from)
# - destination (to)
# - date (Departure)
# - Class
# - available_seats

from os import getenv
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import socket
import requests

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
app.config["MONGO_URI"] = (
    f"mongodb+srv://root:{getenv('MONGODB_PASS')}@flight-booking-microser.sjjihwa.mongodb.net/AssignmentDB?retryWrites=true&w=majority&appName=Flight-Booking-Microservice"
)

# Initialize PyMongo to work with MongoDB
mongo = PyMongo(app)

db = mongo.db.booking


# This function will be invoked by Vendors/Admin
# This function adds new flights to the database
@app.route("/makereservation", methods=["POST"])
def add_flight():
    data = request.json
    if (
        "source" not in data
        or "destination" not in data
        or "date" not in data
        or "class" not in data
        or "available_seats" not in data
        or "booking_id" not in data
    ):
        return jsonify({"message": "Invalid data"}), 400

    # TODO: Check if user is admin by calling the authentication service
    # get current url
    url = request.url
    print(url)

    try:
        result = db.insert_one(
            {
                "source": data["source"],
                "destination": data["destination"],
                "date": data["date"],
                "class": data["class"],
                "available_seats": data["available_seats"],
                "booking_id": data["booking_id"],
            }
        )  # Insert data into collection
        return jsonify(
            {
                "id": str(result.inserted_id),
                "source": data["source"],
                "destination": data["destination"],
                "date": data["date"],
                "class": data["class"],
                "available_seats": data["available_seats"],
            }
        )  # Convert inserted_id to string
    except Exception as e:
        return jsonify({"id": -1, "error": e.args[0]}), 500


def is_port_in_use(port, host="127.0.0.1"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False  # Port is not in use
        except socket.error:
            return True  # Port is in use


START_PORT = 5001

if __name__ == "__main__":
    while is_port_in_use(START_PORT):
        START_PORT += 1
    app.run(debug=True, port=START_PORT)
    requests.post(
        "http://localhost:5000/", json={"action": "register", "port": START_PORT, "servicename": "reserveservice"}
    )
