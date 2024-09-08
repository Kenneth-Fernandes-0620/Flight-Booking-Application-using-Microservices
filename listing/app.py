# - id (autogen)
# - source (from)
# - destination (to)
# - date (Departure)
# - Class
# - available_seats

from os import getenv
import signal
import sys
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import requests
from flask_cors import CORS


# Initialize Flask app
app = Flask(__name__)

# Allow CORS
CORS(app)

# Connect to MongoDB
app.config["MONGO_URI"] = getenv("MONGODB")

# Initialize PyMongo to work with MongoDB
mongo = PyMongo(app)
db = mongo.db.flights

SERVICE_NAME = "listing"
start_port = 9002


@app.route(f"/")
def ok():
    return jsonify({"status": "ok"}), 200


@app.route(f"/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route(f"/{SERVICE_NAME}/")
def home():
    return jsonify({"status": "ok"}), 200


# This function will be invoked by Vendors/Admin
# This function adds new flights to the database
@app.route(f"/{SERVICE_NAME}/addflight", methods=["POST"])
def add_flight():
    data = request.json
    if (
        "source" not in data
        or "destination" not in data
        or "date" not in data
        or "class" not in data
        or "available_seats" not in data
    ):
        return jsonify({"message": "Invalid data"}), 400

    # TODO: Check if user is admin by calling the authentication service
    # get current url
    url = request.url
    # append /isadmin to the url and make a network request as to the admin status
    print(url)
    # response = requests.get(url + "/isadmin")

    try:
        result = db.insert_one(
            {
                "source": data["source"],
                "destination": data["destination"],
                "date": data["date"],
                "class": data["class"],
                "available_seats": data["available_seats"],
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


# This function will be invoked by the front end trying to get the available flights
# here require the booking ID of the flight as this binds the flight booking to the flight details
@app.route(f"/{SERVICE_NAME}/getbookings", methods=["GET"])
def show_booking():
    try:
        source = request.args.get("source")
        destination = request.args.get("destination")
        date = request.args.get("date")

        query = {}
        if source:
            query["source"] = source
        if destination:
            query["destination"] = destination
        if date:
            query["date"] = date

        flights = db.find(query)
        if flights:
            flight_list = []
            for flight in flights:
                flight_data = {
                    "id": str(flight["_id"]),
                    "source": flight["source"],
                    "destination": flight["destination"],
                    "date": flight["date"],
                    "class": flight["class"],
                    "cost": flight["cost"],
                    "available_seats": flight["available_seats"],
                }
                flight_list.append(flight_data)
            return jsonify(flight_list), 200
        else:
            return jsonify({"message": "No flights found"}), 404
    except Exception as e:
        print(e.args[0])
        return jsonify({"id": -1, "error": e.args[0]}), 500


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
            raise Exception(
                f"Error registering service {SERVICE_NAME}, is discovery service running?"
            )
    except requests.exceptions.ConnectionError:
        pass
        # raise Exception(f"Error registering service, is discovery running?")

    except Exception as e:
        raise Exception(e.args[0])


def signal_handler(signal, frame):
    print(f"\nGracefully shutting down... service {SERVICE_NAME} on port {start_port}")
    unregister_service()
    sys.exit(0)


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, signal_handler)
        register_service()
        app.run(host="0.0.0.0", port=start_port)
    except Exception as e:
        print(e.args[0])
