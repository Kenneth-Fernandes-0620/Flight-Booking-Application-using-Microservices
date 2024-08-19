from os import getenv
import signal
import sys
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import requests
import socket
import pika
import json
from bson.objectid import ObjectId as object_id
from flask_cors import CORS


# Initialize Flask app
app = Flask(__name__)

# Allow CORS
CORS(app)

# Connect to MongoDB
app.config["MONGO_URI"] = (
    f"mongodb+srv://root:{getenv('MONGODB_PASS')}@flight-booking-microser.sjjihwa.mongodb.net/AssignmentDB?retryWrites=true&w=majority&appName=Flight-Booking-Microservice"
)

mongo = PyMongo(app)
payment_database = mongo.db.payments

SERVICE_NAME = "payment"
start_port = 5001
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", heartbeat=600)
)
channel = connection.channel()
channel.queue_declare(queue="payment_queue")


@app.route(f"/{SERVICE_NAME}/")
def home():
    return jsonify({"status": "ok"}), 200


@app.route(f"/{SERVICE_NAME}/makepayment", methods=["POST"])
def make_payment():
    data = request.json
    if "booking_id" not in data or "email" not in data or "cost" not in data:
        return jsonify({"message": "Invalid data"}), 400

    try:
        json_message = json.dumps(
            {
                "booking_id": data["booking_id"],
                "email": data["email"],
                "cost": data["cost"],
                "result": "success",
            }
        )

        payment_database.insert_one(
            {
                "booking_id": data["booking_id"],
                "email": data["email"],
                "cost": data["cost"],
                "status": "success",
            }
        )

        channel.basic_publish(
            exchange="", routing_key="payment_queue", body=json_message
        )

        print(f" [x] Sent {json_message}")

        return jsonify({"message": "Payment completed"}), 200
    except Exception as e:
        print(e.args[0])
        return jsonify({"message": "Error sending message"}), 500


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
            raise Exception(f"Error registering service, is {SERVICE_NAME} running?")
    except requests.exceptions.ConnectionError:
        raise Exception(f"Error registering service, is {SERVICE_NAME} running?")

    except Exception as e:
        raise Exception(e.args[0])


def signal_handler(signal, frame):
    print("\nGracefully shutting down...")
    connection.close()
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
