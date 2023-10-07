import json
import sys
import socket
import signal
import logging
import threading 

HOST = "127.0.0.1"
PORT = 8089
RECEIVED_BYTES = 4096 

uuid = None
name = None
room = None

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def signal_handler(sig, frame):
    logging.info("Closing connection...")
    client_socket.close()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def get_name():
    name = input("Enter name: ")
    while not name:
        name = input("Enter name: ")
    return name

def get_room():
    room = input("Enter room: ")
    while not room:
        room = input("Enter room: ")
    return room

def connect_to_server():
    client_socket.connect((HOST, PORT))

    request_string = json.dumps({
        "type": "connect",
        "payload": {
            "name": name,
            "room": room,
        }
    })
    client_socket.send(request_string.encode("utf-8"))

    response_string = client_socket.recv(RECEIVED_BYTES).decode("utf-8")
    if not response_string:
        logging.info("Failed while connecting to the server")
        sys.exit(1)
    
    response_json = json.loads(response_string)
    if response_json.get("type") == "connect_ack":
        if response_json.get("payload").get("message") == "Connected to the room":
            logging.info(f"Connected to {HOST}:{PORT}")
            return response_json.get("payload").get("uuid")

def receive_message():
    while True:
        response_string = client_socket.recv(RECEIVED_BYTES).decode("utf-8")
        if not response_string:
            return

        response_json = json.loads(response_string)
        if response_json.get("type") == "message":
            logging.info(f"{response_json.get('payload').get('sender')}: {response_json.get('payload').get('text')}")
        if response_json.get("type") == "notification":
            logging.info(response_json.get("payload").get("message"))

def send_message(message):
    request_string = json.dumps({
        "type": "message",
        "payload": {
            "uuid": uuid,
            "sender": name,
            "room": room,
            "text": message,
        }
    })
    client_socket.send(request_string.encode("utf-8"))

if __name__=="__main__":
    name = get_name()
    room = get_room()

    uuid = connect_to_server()

    receive_thread = threading.Thread(target=receive_message)
    receive_thread.daemon = True
    receive_thread.start()

    print("Enter a message (or 'exit' to quit):")
    while True:
        message = input()
        if message.lower() == "exit":
            break
        send_message(message)
 