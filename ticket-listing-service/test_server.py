import socket
from flask import Flask
from werkzeug.serving import make_server

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

def create_reserved_socket(host='localhost', port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
        s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1) 
    s.bind((host, port))
    return s

def run_flask_with_socket(socket):
    server = make_server('localhost', 5000, app)
    server.socket = socket
    server.serve_forever()

if __name__ == '__main__':
    reserved_socket = create_reserved_socket()
    print(f"Starting Flask on port {reserved_socket.getsockname()[1]}")
    run_flask_with_socket(reserved_socket)
