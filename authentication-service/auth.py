from os import getenv
import sys
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import signal
import socket
import requests
from flask_cors import CORS


# Initialize Flask app
app = Flask(__name__)

CORS(app)

# Connect to MongoDB
app.config["MONGO_URI"] = (
    f"mongodb+srv://root:{getenv('MONGODB_PASS')}@flight-booking-microser.sjjihwa.mongodb.net/AssignmentDB?retryWrites=true&w=majority&appName=Flight-Booking-Microservice"
)

# Initialize PyMongo to work with MongoDB
mongo = PyMongo(app)
db = mongo.db.users

SERVICE_NAME = "authenticationservice"
start_port = 5001


@app.route(f"/{SERVICE_NAME}/")
def home():
    return jsonify({"status": "ok"}), 200


@app.route(f"/{SERVICE_NAME}/signup", methods=["POST"])
def create_item():
    data = request.json
    if "username" not in data or "password" not in data:
        return jsonify({"message": "Invalid data"}), 400

    try:
        result = db.insert_one(
            {"username": data["username"], "password": data["password"]}
        )  # Insert data into collection
        return jsonify(
            {"id": str(result.inserted_id), "name": data["username"]}
        )  # Convert inserted_id to string
    except Exception as e:
        return jsonify({"id": -1, "error": e.args[0]}), 500


@app.route(f"/{SERVICE_NAME}/login", methods=["POST"])
def login_user():
    data = request.json
    if "username" not in data or "password" not in data:
        return jsonify({"message": "Invalid data"}), 400

    print("Login request received for user: " + data["username"] + " with password: " + data["password"])

    try:
        user = db.find_one({"username": data["username"], "password": data["password"]})
        if user:
            return jsonify({"id": str(user["_id"]), "name": user["username"]}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"id": -1, "error": e.args[0]}), 500


@app.route(f"/{SERVICE_NAME}/isadmin", methods=["GET"])
def is_admin():
    data = request.json
    if "username" not in data:
        return jsonify({"message": "Invalid data"}), 400

    try:
        user = db.find_one({"username": data["username"]})
        if user:
            return jsonify({"isAdmin": user["isAdmin"]}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"id": -1, "error": e.args[0]}), 500


@app.route(f"/{SERVICE_NAME}/addadmin", methods=["POST"])
def add_admin():
    data = request.json
    if "username" not in data:
        return jsonify({"message": "Invalid data"}), 400

    try:
        result = db.update_one(
            {"username": data["username"]}, {"$set": {"isAdmin": True}}
        )
        return jsonify({"id": str(result.inserted_id), "name": data["username"]}), 200
    except Exception as e:
        return jsonify({"id": -1, "error": e.args[0]}), 500


def unregister_service():
    try:
        res = requests.post(
            "http://localhost:5000/unregister",
            json={"port": start_port, "servicename": SERVICE_NAME},
        )
        if res.status_code == 200:
            print("Service unregistered successfully")
        else:
            print("Error unregistering service")
    except Exception as e:
        print(e.args[0])


def register_service():
    try:
        res = requests.post(
            "http://localhost:5000/register",
            json={"port": start_port, "servicename": SERVICE_NAME},
        )
        if res.status_code == 200:
            print("Service registered successfully")
        else:
            raise Exception(
                f"Error registering service, is {SERVICE_NAME} service running?"
            )
    except requests.exceptions.ConnectionError:
        raise Exception(f"Error registering service, is {SERVICE_NAME} running?")

    except Exception as e:
        raise Exception(e.args[0])


def signal_handler(signal, frame):
    print("\nGracefully shutting down...")
    # Perform any cleanup here
    unregister_service()
    sys.exit(0)


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, signal_handler)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Allow address reuse to avoid issues with TIME_WAIT state
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind to port 0 to let the OS select an available port
            s.bind(("127.0.0.1", 0))
            # Get the port number assigned by the OS
            start_port = s.getsockname()[1]
            register_service()
            app.run(host="localhost", port=start_port)
    except Exception as e:
        print(e.args[0])
