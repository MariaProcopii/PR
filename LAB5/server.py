import uuid
import json
import sys
import logging
import signal
import socket 
import threading

HOST = "127.0.0.1"
PORT = 8089
RECEIVED_BYTES = 4096 
CLIENTS = []

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((HOST, PORT))
server_socket.listen()
logging.info(f"Server is listening on {HOST}:{PORT}")

def signal_handler(sig, frame):
    logging.info("Shutting down the server...")
    server_socket.close()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def is_client_registred(uuid):
    for client in CLIENTS:
        if client.get("uuid") == uuid:
            return True
    return False
def notify_message(message, client_socket, room):
    for client in CLIENTS:
        if client.get("client_socket") != client_socket and client.get("room") == room:
            client.get("client_socket").send(message.encode("utf-8"))

def handle_client(client_socket, client_address):
    client_id = None

    while True:
        request_string = client_socket.recv(RECEIVED_BYTES).decode("utf-8")
        if not request_string:
            break

        request_json = json.loads(request_string)
        if request_json.get("type") == "connect":
            client_id = str(uuid.uuid4())
            CLIENTS.append({
                "uuid": client_id, 
                "client_socket": client_socket, 
                "client_address": client_address,
                "name": request_json.get("payload").get("name"),
                "room": request_json.get("payload").get("room"),
            })
            logging.info(f"Accepted connection from {request_json.get('payload').get('name')}({client_address})")

            response_string = json.dumps({
                "type": "connect_ack",
                "payload": {
                    "uuid": client_id,
                    "message": "Connected to the room",
                }
            })
            client_socket.send(response_string.encode("utf-8"))

            message = json.dumps({
                "type": "notification",
                "payload": {
                    "message": f"{request_json.get('payload').get('name')} connected to the chat room"
                }
            }) 
            notify_message(message, client_socket, request_json.get("payload").get("room"))

        elif request_json.get("type") == "message":
            logging.info(f"Received message from {request_json.get('payload').get('sender')}")
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
                        client.get("client_socket").send(response_string.encode("utf-8"))

    for client in CLIENTS:
        if client.get("client_id") == client_id:
            client.get("client_socket").close()
            CLIENTS.remove(client)
            return

if __name__=="__main__":
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address,))
        client_thread.start()

