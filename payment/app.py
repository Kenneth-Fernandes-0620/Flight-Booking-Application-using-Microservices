from os import getenv
import signal
import sys
from threading import Thread
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import requests
import pika
import json
from flask_cors import CORS
import time
import socket

# Initialize Flask app
app = Flask(__name__)

# Allow CORS
CORS(app)

# Connect to MongoDB
app.config["MONGO_URI"] = getenv("MONGODB")

mongo = PyMongo(app)
payment_database = mongo.db.payments

SERVICE_NAME = "payment"
start_port = 9005

# rabbitmq_host = getenv('RABBITMQ_HOST', 'localhost')
# print("RabbitMQ Host: " + rabbitmq_host)
# connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
# channel = connection.channel()
# channel.queue_declare(queue="payment_queue")


def ping_rabbitmq():
    """Sends a ping message to RabbitMQ every 30 seconds."""
    while True:
        try:
            message = json.dumps({"type": "ping"})
            channel.basic_publish(
                exchange="", routing_key="payment_queue", body=message
            )
            print(f"Sent ping message to RabbitMQ")
            time.sleep(30)
        except Exception as e:
            print(f"Error sending ping message: {e}")
            time.sleep(5)  # Retry after error with a longer delay


def connect_to_rabbitmq():
    while True:
        try:
            connection_params = pika.ConnectionParameters(
                host="rabbitmq",
                heartbeat=60,
                virtual_host="/",
                credentials=pika.PlainCredentials("guest", "guest"),
            )

            def on_connection_open(connection):
                connection.connection.socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1
                )
                connection.connection.socket.setsockopt(
                    socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60
                )  # Time before keepalive starts (in seconds)
                connection.connection.socket.setsockopt(
                    socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10
                )  # Interval between keepalives (in seconds)
                connection.connection.socket.setsockopt(
                    socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5
                )  # Number of keepalives before dropping the connection

            connection = pika.BlockingConnection(parameters=connection_params)
            # on_connection_open(connection)
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ is not available. Retrying...")
            time.sleep(5)


connection = connect_to_rabbitmq()
channel = connection.channel()
channel.queue_declare(queue="payment_queue", durable=True)
channel.queue_declare(queue="ping", durable=True)

print("Connected to RabbitMQ")


@app.route(f"/")
def ok():
    return jsonify({"status": "ok"}), 200


@app.route(f"/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route(f"/{SERVICE_NAME}/")
def home():
    return jsonify({"status": "ok"}), 200


@app.route(f"/{SERVICE_NAME}/makepayment", methods=["POST"])
def make_payment():
    data = request.json
    if "booking_id" not in data or "email" not in data or "cost" not in data:
        return jsonify({"message": "Invalid data"}), 400

    print(
        "Payment request received for booking: "
        + data["booking_id"]
        + " with email: "
        + data["email"]
        + " and cost: "
        + str(data["cost"])
    )

    try:
        json_message = json.dumps(
            {
                "booking_id": data["booking_id"],
                "email": data["email"],
                "cost": data["cost"],
                "result": "success",
            }
        )
        print("got details" + json_message)

        payment_result = payment_database.insert_one(
            {
                "booking_id": data["booking_id"],
                "email": data["email"],
                "cost": data["cost"],
                "status": "success",
            }
        )
        print("payment result" + str(payment_result.inserted_id))

        channel.basic_publish(
            exchange="", routing_key="payment_queue", body=json_message
        )

        print(f" [x] Sent {json_message}")

        return (
            jsonify(
                {
                    "message": "Payment completed",
                    "payment_id": str(payment_result.inserted_id),
                }
            ),
            200,
        )
    except Exception as e:
        print(e.args[0])
        return jsonify({"message": "Error sending message", "reason": e.args[0]}), 500


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

        ping_thread = Thread(target=ping_rabbitmq)
        # Start the ping thread
        ping_thread.start()

        app.run(host="0.0.0.0", port=start_port)
    except Exception as e:
        print(e.args[0])
    connection.close()
