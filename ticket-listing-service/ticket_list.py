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
import socket
from flask_cors import CORS


# Initialize Flask app
app = Flask(__name__)

# Allow CORS
CORS(app)

# Connect to MongoDB
app.config["MONGO_URI"] = (
    f"mongodb+srv://root:{getenv('MONGODB_PASS')}@flight-booking-microser.sjjihwa.mongodb.net/AssignmentDB?retryWrites=true&w=majority&appName=Flight-Booking-Microservice"
)

# Initialize PyMongo to work with MongoDB
mongo = PyMongo(app)
db = mongo.db.flights

SERVICE_NAME = "listingservice"
start_port = 5001


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
            raise Exception("Error registering service, is discovery service running?")
    except requests.exceptions.ConnectionError:
        raise Exception("Error registering service, is discovery service running?")

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

