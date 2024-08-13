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


@app.route("/login", methods=["POST"])
def login_user():
    data = request.json
    if "username" not in data or "password" not in data:
        return jsonify({"message": "Invalid data"}), 400
    
    try:
        user = db.find_one({"username": data["username"], "password": data["password"]})
        if user:
            return jsonify({"id": str(user["_id"]), "name": user["username"]}), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"id": -1, "error": e.args[0]}), 500

@app.route("/isadmin", methods=["GET"])
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


@app.route("/addadmin", methods=["POST"])
def add_admin():
    data = request.json
    if "username" not in data:
        return jsonify({"message": "Invalid data"}), 400

    try:
        result = db.update_one({"username": data["username"]}, {"$set": {"isAdmin": True}})
        return jsonify({"id": str(result.inserted_id), "name": data["username"]}), 200
    except Exception as e:
        return jsonify({"id": -1, "error": e.args[0]}), 500

if __name__ == "__main__":
    app.run(debug=True,port=5000)
    