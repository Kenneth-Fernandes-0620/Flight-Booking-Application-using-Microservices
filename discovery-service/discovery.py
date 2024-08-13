from os import getenv
from flask import Flask, jsonify, request, redirect
from flask_pymongo import PyMongo

# Initialize Flask app
app = Flask(__name__)

services: dict = {}


@app.route("/register", methods=["POST"])
def register_service():
    data = request.json
    if "port" not in data or "servicename" not in data:
        return jsonify({"message": "Invalid data"}), 400


    service_name = data["servicename"]
    service_port = data["port"]

    print(f"Recieved Register Request for service {service_name} and port {service_port}")

    try:
        services_list: list = services.get(service_name, [])
        services_list.append(service_port)
        services[service_name] = services_list
        return jsonify({"message": "Service registered successfully"}), 200
    except Exception as e:
        print(e)
        return jsonify({"id": -1, "error": e.args[0]}), 500


@app.route("/unregister", methods=["POST"])
def unregister_service():
    data = request.json
    if "port" not in data or "servicename" not in data:
        return jsonify({"message": "Invalid data"}), 400

    service_name = data["servicename"]
    service_port = data["port"]

    print(f"Recieved Unregister Request for service {service_name} and port {service_port}")

    try:
        services_list: list = services.get(service_name, [])
        services_list.remove(service_port)
        services[service_name] = services_list
        return jsonify({"message": "Service unregistered successfully"}), 200
    except Exception as e:
        return jsonify({"id": -1, "error": e.args[0]}), 500


@app.route("/<path:redirect_route>")
def redirect_to_port(redirect_route):
    services_list = services.get(redirect_route, [])

    if len(services_list) == 0:
        return jsonify({"error": "service unavailable"}), 400

    # Construct the new URL
    new_url = f"http://localhost:{services_list[-1]}/{redirect_route}"

    # Redirect the user to the new URL
    return redirect(new_url)


if __name__ == "__main__":
    app.run(debug=True, port=5000)