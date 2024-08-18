from os import getenv
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import socket
import requests
import signal
from bson import ObjectId
from flask_cors import CORS
import sys


# Initialize Flask app
app = Flask(__name__)

CORS(app)


# Connect to MongoDB
app.config["MONGO_URI"] = (
    f"mongodb+srv://root:{getenv('MONGODB_PASS')}@flight-booking-microser.sjjihwa.mongodb.net/AssignmentDB?retryWrites=true&w=majority&appName=Flight-Booking-Microservice"
)

# Initialize PyMongo to work with MongoDB
mongo = PyMongo(app)

db = mongo.db.booking
flights_db = mongo.db.flights

SERVICE_NAME = "reserveservice"
start_port = 5001


@app.route(f"/{SERVICE_NAME}/")
def home():
    return jsonify({"status": "ok"}), 200


@app.route(f"/{SERVICE_NAME}/makereservation", methods=["POST"])
def make_reservation():
    data = request.json
    if "booking_id" not in data or "count" not in data or "email" not in data:
        return jsonify({"message": "Invalid data"}), 400

    session = mongo.cx.start_session()
    try:
        session.start_transaction()

        flight = flights_db.find_one(
            {"_id": ObjectId(data["booking_id"]), "available_seats": {"$gt": 0}},
            session=session,
        )

        if not flight:
            session.abort_transaction()
            return jsonify({"message": "No seats available or flight not found"}), 400

        # Update the available seats in flights collection
        flights_db.update_one(
            {"_id": flight["_id"]},
            {"$inc": {"available_seats": -data["count"]}},
            session=session,
        )

        # Insert reservation into booking collection
        result = db.insert_one(
            {
                "booking_id": data["booking_id"],
                "email": data["email"],
                "available_seats": flight["available_seats"] - data["count"],
            },
            session=session,
        )

        session.commit_transaction()

        return (
            jsonify(
                {
                    "id": str(result.inserted_id),
                    "booking_id": data["booking_id"],
                    "available_seats": flight["available_seats"] - data["count"],
                    "email": data["email"],
                }
            ),
            200,
        )

    except Exception as e:
        session.abort_transaction()
        return jsonify({"message": "Transaction failed", "error": str(e)}), 500

    finally:
        session.end_session()


# def is_port_in_use(port, host="127.0.0.1"):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         try:
#             s.bind((host, port))
#             return False  # Port is not in use
#         except socket.error:
#             return True  # Port is in use


# START_PORT = 5001

# if __name__ == "__main__":
#     while is_port_in_use(START_PORT):
#         START_PORT += 1
#     app.run(debug=True, port=START_PORT)
#     requests.post(
#         "http://localhost:5000/", json={"action": "register", "port": START_PORT, "servicename": "reserveservice"}
#     )


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
    print(start_port)
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
