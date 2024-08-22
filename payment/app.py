from os import getenv
import signal
import sys
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import requests
import pika
import json
from flask_cors import CORS
import time


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
start_port = 9005

# rabbitmq_host = getenv('RABBITMQ_HOST', 'localhost')
# print("RabbitMQ Host: " + rabbitmq_host)
# connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
# channel = connection.channel()
# channel.queue_declare(queue="payment_queue")


def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ is not available. Retrying...")
            time.sleep(5)

connection = connect_to_rabbitmq()
channel = connection.channel()
channel.queue_declare(queue="payment_queue")

print("Connected to RabbitMQ")

@app.route(f"/{SERVICE_NAME}/")
def home():
    return jsonify({"status": "ok"}), 200


@app.route(f"/{SERVICE_NAME}/makepayment", methods=["POST"])
def make_payment():
    data = request.json
    if "booking_id" not in data or "email" not in data or "cost" not in data:
        return jsonify({"message": "Invalid data"}), 400

    print("Payment request received for booking: " + data["booking_id"] + " with email: " + data["email"] + " and cost: " + data["cost"])

    try:
        json_message = json.dumps(
            {
                "booking_id": data["booking_id"],
                "email": data["email"],
                "cost":  data["cost"],
                "result": "success",
            }
        )

        payment_result = payment_database.insert_one(
            {
                "booking_id": data["booking_id"],
                "email": data["email"],
                "cost":  data["cost"],
                "status": "success",
            }
        )

        channel.basic_publish(
            exchange="", routing_key="payment_queue", body=json_message
        )

        print(f" [x] Sent {json_message}")

        return jsonify({"message": "Payment completed", "payment_id": str(payment_result.inserted_id) }), 200
    except Exception as e:
        print(e.args[0])
        return jsonify({"message": "Error sending message"}), 500


def unregister_service():
    try:
        res = requests.post(
            "http://discovery:9000/unregister",
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
            "http://discovery:9000/register",
            json={"port": start_port, "servicename": SERVICE_NAME},
        )
        if res.status_code == 200:
            print("Service registered successfully")
        else:
            raise Exception(f"Error registering service, is discovery running?")
    except requests.exceptions.ConnectionError:
        raise Exception(f"Error registering service, is discovery running?")

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
        register_service()
        app.run(host="0.0.0.0", port=start_port)
    except Exception as e:
        print(e.args[0])
