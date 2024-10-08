from flask import Flask, jsonify, request, redirect, send_from_directory
from typing import List, Tuple, Dict
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

services: Dict[str, Tuple[List[str], int]] = {}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "UP"}), 200

@app.route("/health", methods=["GET"])
def index():
    return jsonify({"status": "UP"}), 200

@app.route("/register", methods=["POST"])
def register_service():
    global services
    data = request.json
    if "port" not in data or "servicename" not in data:
        return jsonify({"message": "Invalid data"}), 400

    service_name = data["servicename"]
    service_port = data["port"]

    print(
        f"Recieved Register Request for service {service_name} and port {service_port}"
    )

    try:
        services_tuple: Tuple[list[str], int] = services.get(service_name, ([], 0))
        services_list = services_tuple[0]
        services_list.append(service_port)
        services[service_name] = (services_list, services_tuple[1])
        return jsonify({"message": "Service registered successfully"}), 200
    except Exception as e:
        print(e)
        return jsonify({"id": -1, "error": e.args[0]}), 500


@app.route("/unregister", methods=["POST"])
def unregister_service():
    global services
    data = request.json
    if "port" not in data or "servicename" not in data:
        return jsonify({"message": "Invalid data"}), 400

    service_name = data["servicename"]
    service_port = data["port"]

    print(
        f"Recieved Unregister Request for service {service_name} and port {service_port}"
    )

    try:
        services_tuple: Tuple[list[str], int] = services.get(service_name, ([], 0))
        services_list = services_tuple[0]
        services_list.remove(service_port)
        services[service_name] = (services_list, services_tuple[1])
        return jsonify({"message": "Service unregistered successfully"}), 200
    except Exception as e:
        return jsonify({"id": -1, "error": e.args[0]}), 500

@app.route("/route/<path:redirect_route>", methods=["GET", "POST"])
def redirect_to_port(redirect_route):
    global services
    print(f"Recieved Redirect Request for service {redirect_route}")

    if redirect_route[-1] == "/":
        redirect_route = redirect_route[:-1]

    original_redirect_route = redirect_route
    redirect_route = redirect_route.split("/")[0]

    services_tuple: Tuple[list[str], int] = services.get(redirect_route, ([], 0))
    services_list = services_tuple[0]
    services_port_last_accessed = services_tuple[1]
    services_ports = len(services_list)

    print(f"Redirecting to {redirect_route}")
    print(f"Ports Available: {services_ports}")
    print(f"Last Accessed Port: {services_port_last_accessed}")

    if services_ports == 0:
        return jsonify({"error": "service unavailable"}), 400

    services_new_port = int((services_port_last_accessed + 1) % services_ports)
    services[redirect_route] = (services_list, services_new_port)

    print(f"New Port: {services_new_port}")

    # Construct the new URL
    new_url = (
        f"http://localhost:{services_list[services_new_port]}/{original_redirect_route}"
    )

    print(f"Redirecting to {new_url}")

    # Redirect the user to the new URL
    return redirect(new_url, code=307)
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
