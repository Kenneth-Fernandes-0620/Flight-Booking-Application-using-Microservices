from os import getenv
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import requests
import signal
from bson import ObjectId
from flask_cors import CORS
import sys


# Initialize Flask app
app = Flask(__name__)

CORS(app)

# Connect to MongoDB
app.config["MONGO_URI"] = getenv("MONGODB")

# Initialize PyMongo to work with MongoDB
mongo = PyMongo(app)

db = mongo.db.booking
flights_db = mongo.db.flights

SERVICE_NAME = "reservation"
start_port = 9003


@app.route(f"/")
def ok():
    return jsonify({"status": "ok"}), 200


@app.route(f"/health")
def health():
    return jsonify({"status": "ok"}), 200


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

        flight: dict = flights_db.find_one(
            {"_id": ObjectId(data["booking_id"]), "available_seats": {"$gt": 0}},
            session=session,
        )

        if not flight:
            session.abort_transaction()
            return jsonify({"message": "No seats available or flight not found"}), 400

        if int(flight.get("available_seats")) < int(data["count"]):
            session.abort_transaction()
            return jsonify({"message": "Not enough seats available"}), 400

        print("Available Seats: ", int(flight.get("available_seats")))

        # Update the available seats in flights collection
        flights_db.update_one(
            {"_id": flight["_id"]},
            {"$inc": {"available_seats": -int(data["count"])}},
            session=session,
        )

        # Insert reservation into booking collection
        result = db.insert_one(
            {
                "booking_id": data["booking_id"],
                "email": data["email"],
                "booked_seats": data["count"],
            },
            session=session,
        )

        session.commit_transaction()

        return (
            jsonify(
                {
                    "id": str(result.inserted_id),
                    "booking_id": data["booking_id"],
                    "available_seats": int(flight["available_seats"])
                    - int(data["count"]),
                    "email": data["email"],
                }
            ),
            200,
        )

    except Exception as e:
        print(e)
        session.abort_transaction()
        return jsonify({"message": "Transaction failed", "error": str(e)}), 500

    finally:
        session.end_session()


@app.route(f"/{SERVICE_NAME}/cancelreservation", methods=["POST"])
def cancel_reservation():
    data = request.json
    if "booking_id" not in data or "payment_id" not in data or "count" not in data:
        return jsonify({"message": "Invalid data"}), 400

    print(data)

    session = mongo.cx.start_session()
    try:
        session.start_transaction()

        flight: dict = flights_db.find_one(
            {"_id": ObjectId(data["booking_id"])},
            session=session,
        )

        if not flight:
            session.abort_transaction()
            return jsonify({"message": "No seats available or flight not found"}), 400

        if int(flight.get("available_seats")) < int(data["count"]):
            session.abort_transaction()
            return jsonify({"message": "Not enough seats available"}), 400

        # Update the available seats in flights collection
        flights_db.update_one(
            {"_id": flight["_id"]},
            {"$inc": {"available_seats": int(data["count"])}},
            session=session,
        )

        # Delete reservation from booking collection
        result = db.delete_one(
            {
                "_id": ObjectId(data["payment_id"]),
                "booking_id": data["booking_id"],
            },
            session=session,
        )

        session.commit_transaction()

        return (
            jsonify(
                {"ack": str(result.acknowledged), "booking_id": data["booking_id"]}
            ),
            200,
        )

    except Exception as e:
        print(e)
        session.abort_transaction()
        return jsonify({"message": "Transaction failed", "error": str(e)}), 500

    finally:
        session.end_session()


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
            raise Exception(f"Error registering service, is discovery service running?")
    except requests.exceptions.ConnectionError:
        raise Exception(f"Error registering service, is discovery running?")

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
        register_service()
        app.run(host="0.0.0.0", port=start_port)
    except Exception as e:
        print(e.args[0])
