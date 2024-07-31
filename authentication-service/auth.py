from os import getenv
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
app.config["MONGO_URI"] = (
    f"mongodb+srv://root:{getenv('MONGODB_PASS')}@flight-booking-microser.sjjihwa.mongodb.net/AssignmentDB?retryWrites=true&w=majority&appName=Flight-Booking-Microservice"
)

# Initialize PyMongo to work with MongoDB
mongo = PyMongo(app)

db = mongo.db.users

@app.route("/signup", methods=["POST"])
def create_item():
    data = request.json
    if "username" not in data or "password" not in data:
        return jsonify({"message": "Invalid data"}), 400

    try:
        result = db.insert_one({
            "username": data["username"],
            "password": data["password"]
        })  # Insert data into collection
        return jsonify(
            {"id": str(result.inserted_id), "name": data["username"]}
        )  # Convert inserted_id to string
    except Exception as e:
        return jsonify({"id": -1, "error": e.args[0]}), 500


@app.route("/login", methods=["GET"])
def get_item():
    pass


if __name__ == "__main__":
    app.run(debug=True)
