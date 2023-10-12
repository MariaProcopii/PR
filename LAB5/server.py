import uuid
import json
import sys
import logging
import signal
import socket
import threading

# Server's host
HOST = "127.0.0.1"
# Server's port
PORT = 8089
# Byte chunk received from the tcp connecion
RECEIVED_BYTES = 4096 * 1000000
# List of all the live connected clients
CLIENTS = []

# Logger init with formatter config
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Server IPv4 TCP socket with additional params set up
# Function: Listen to client connections and handle them
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Server blocking and listening to (host):(port)
server_socket.bind((HOST, PORT))
server_socket.listen()
logging.info(f"Server is listening on {HOST}:{PORT}")

# Server IPv4 TCP socket with additional params set up
# Function: Connect to media server, forwards requests and responses
server_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
# Connect to the media server
server_client_socket.connect((HOST, 12445))
logging.info(f"Server connected to Media Server on {HOST}:{PORT}")

# Script exiting handler


def signal_handler(sig, frame):
    logging.info("Shutting down the server...")
    server_socket.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# Helper functions


def is_client_registred(uuid):
    for client in CLIENTS:
        if client.get("uuid") == uuid:
            return True
    return False


def notify_message(message, client_socket, room):
    for client in CLIENTS:
        if client.get("client_socket") != client_socket and client.get("room") == room:
            client.get("client_socket").send(message.encode("utf-8"))


def notify_all_message(message, room):
    for client in CLIENTS:
        if client.get("room") == room:
            client.get("client_socket").send(message.encode("utf-8"))


def remove_client(client_id):
    name = None
    room = None
    client_socket = None

    for client in CLIENTS:
        if client.get("client_id") == client_id:
            name = client.get("name")
            room = client.get("room")
            client_socket = client.get("client_socket")

            client.get("client_socket").close()
            CLIENTS.remove(client)
            break

    if not name or not room or not client_socket:
        return

    logging.info(f"{name} disconnected")
    notify_message(
        json.dumps({"type": "notification", "payload": {
                   "message": f"{name} left the chat room"}}),
        client_socket,
        room
    )


# Handler functions


def connect_client(client_socket, client_address, request_json):
    # Create client unique identifier
    client_id = str(uuid.uuid4())
    CLIENTS.append({
        "uuid": client_id,
        "client_socket": client_socket,
        "client_address": client_address,
        "name": request_json.get("payload").get("name"),
        "room": request_json.get("payload").get("room"),
    })
    logging.info(
        f"Accepted connection from {request_json.get('payload').get('name')}({client_address})")

    # Inform client about OK connection
    response_string = json.dumps({
        "type": "connect_ack",
        "payload": {
            "uuid": client_id,
            "message": "Connected to the room",
        }
    })
    client_socket.send(response_string.encode("utf-8"))

    # Notify other users about new chatroom user
    message = json.dumps({
        "type": "notification",
        "payload": {
            "message": f"{request_json.get('payload').get('name')} connected to the chat room"
        }
    })
    notify_message(message, client_socket,
                   request_json.get("payload").get("room"))

    return client_id


def broadcast_message(client_socket, client_address, request_json):
    logging.info(
        f"Received message from {request_json.get('payload').get('sender')}")
    # Optimized the search process of the client in the live connection list.
    # If client's socket is closed, no need to search in list.
    if is_client_registred(request_json.get("payload").get("uuid")):
        for client in CLIENTS:
            if client.get("client_socket") != client_socket and client.get("room") == request_json.get("payload").get("room"):
                response_string = json.dumps({
                    "type": "message",
                    "payload": {
                        "sender": request_json.get("payload").get("sender"),
                        "text": request_json.get("payload").get("text"),
                    }
                })
                client.get("client_socket").send(
                    response_string.encode("utf-8"))


def upload_message(client_socket, client_address, request_json):
    sender = request_json.get("payload").get("sender")
    filename = request_json.get("payload").get("filename")
    room = request_json.get("payload").get("room")

    server_client_socket.send(json.dumps(request_json).encode("utf-8"))

    server_media_response_string = server_client_socket.recv(
        RECEIVED_BYTES).decode("utf-8")
    server_media_response_json = json.loads(server_media_response_string)

    if server_media_response_json.get("type") == "upload" and server_media_response_json.get("payload").get("message") == "Successfully uploaded the file":
        notify_all_message(
            json.dumps({"type": "notification", "payload": {
                       "message": f"User {sender} uploaded the {filename} file"}}),
            room
        )


def download_message(client_socket, client_address, request_json):
    server_client_socket.send(json.dumps(request_json).encode("utf-8"))
    server_media_response_string = server_client_socket.recv(RECEIVED_BYTES)
    client_socket.send(server_media_response_string)


# Main handler


def handle_client(client_socket, client_address):
    client_id = None

    while True:
        request_string = client_socket.recv(RECEIVED_BYTES).decode("utf-8")
        if not request_string:
            break

        request_json = json.loads(request_string)
        if request_json.get("type") == "connect":
            client_id = connect_client(
                client_socket, client_address, request_json)

        elif request_json.get("type") == "message":
            broadcast_message(client_socket, client_address, request_json)

        elif request_json.get("type") == "upload":
            upload_message(client_socket, client_address, request_json)

        elif request_json.get("type") == "download":
            download_message(client_socket, client_address, request_json)

    remove_client(client_id)


# Entry point of the script
if __name__ == "__main__":
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(
            target=handle_client, args=(client_socket, client_address,))
        client_thread.start()
