# - id (autogen)
# - source (from)
# - destination (to)
# - date (Departure)
# - Class
# - available_seats

from os import getenv
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import requests

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
app.config["MONGO_URI"] = (
    f"mongodb+srv://root:{getenv('MONGODB_PASS')}@flight-booking-microser.sjjihwa.mongodb.net/AssignmentDB?retryWrites=true&w=majority&appName=Flight-Booking-Microservice"
)

# Initialize PyMongo to work with MongoDB
mongo = PyMongo(app)

db = mongo.db.flights


# This function will be invoked by Vendors/Admin
# This function adds new flights to the database
@app.route("/addflight", methods=["POST"])
def create_item():
    data = request.json
    if "source" not in data or "destination" not in data or "date" not in data or "class" not in data or "available_seats" not in data:
        return jsonify({"message": "Invalid data"}), 400


    # TODO: Check if user is admin by calling the authentication service
    # get current url
    url = request.url
    # append /isadmin to the url and make a network request as to the admin status
    print(url)


    # try:
    #     result = db.insert_one({
    #         "source": data["source"],
    #         "destination": data["destination"],
    #         "date": data["date"],
    #         "class": data["class"],
    #         "available_seats": data["available_seats"]
    #     })  # Insert data into collection
    #     return jsonify(
    #         {"id": str(result.inserted_id), "source": data["source"], "destination": data["destination"], "date": data["date"], "class": data["class"], "available_seats": data["available_seats"]}
    #     )  # Convert inserted_id to string
    # except Exception as e:
    #     return jsonify({"id": -1, "error": e.args[0]}), 500
    

    # if "username" not in data or "password" not in data:
    #     return jsonify({"message": "Invalid data"}), 400

    # try:
    #     result = db.insert_one({
    #         "username": data["username"],
    #         "password": data["password"]
    #     })  # Insert data into collection
    #     return jsonify(
    #         {"id": str(result.inserted_id), "name": data["username"]}
    #     )  # Convert inserted_id to string
    # except Exception as e:
    #     return jsonify({"id": -1, "error": e.args[0]}), 500


# This function will be invoked by the front end trying to get the available flights
# here require the booking ID of the flight as this binds the flight booking to the flight details
@app.route("/getBookings", methods=["GET"])
def login_user():
    data = request.json
    # if "username" not in data or "password" not in data:
    #     return jsonify({"message": "Invalid data"}), 400
    
    try:
        user = db.find({"username": data["username"], "password": data["password"]})
        if user:
            return jsonify({"id": str(user["_id"]), "name": user["username"]}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"id": -1, "error": e.args[0]}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
