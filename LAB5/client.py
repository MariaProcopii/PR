import os
import json
import sys
import base64
import socket
import signal
import logging
import threading

# Server host
HOST = "127.0.0.1"
# Server port
PORT = 8089
# Byte chunk received from the tcp connecion
RECEIVED_BYTES = 4096 * 1000000

# Client's params
uuid = None
name = None
room = None

# Client IPv4 TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Logger init with formatter config
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Script exiting handler


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

# Connect client to server. Return client's uuid


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

# Message receiver handler


def receive_message():
    while True:
        response_string = client_socket.recv(RECEIVED_BYTES).decode("utf-8")
        if not response_string:
            return

        response_json = json.loads(response_string)
        if response_json.get("type") == "message":
            logging.info(
                f"{response_json.get('payload').get('sender')}: {response_json.get('payload').get('text')}")
        elif response_json.get("type") == "notification":
            logging.info(response_json.get("payload").get("message"))
        elif response_json.get("type") == "download":
            filename = response_json.get("payload").get("filename")
            filebytes = base64.b64decode(response_json.get("payload").get("file"))
            if not filebytes:
                logging.info(f"ERROR: File {filename} doesn't exist")
            else:
                try:
                    with open("client_media/"+filename, "wb") as file:
                        file.write(filebytes)
                        logging.info(f"Successfully saved {filename}")
                except Exception as e:
                    logging.info(f"Error while saving {filename} file")
                    logging.info(f"ERROR: {e}")

# Handler functions


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


def help_message():
    logging.info("\nupload <file path>\ndownload <file name>")


def upload_file(command):
    if len(command.split(" ")) != 2:
        logging.info("Invalid command")
        return

    filepath = command.split(" ")[1]
    filename = os.path.basename(filepath)
    filebytes = None
    try:
        with open(filepath, "rb") as file:
            filebytes = file.read()
    except FileNotFoundError:
        logging.info(f"File {filename} doesn't exist")
        return

    request_string = json.dumps({
        "type": "upload",
        "payload": {
                "uuid": uuid,
                "sender": name,
                "room": room,
                "filename": filename,
                "file": str(base64.b64encode(filebytes), "utf-8"),
        }
    })
    client_socket.send(request_string.encode("utf-8"))


def download_file(command):
    if len(command.split(" ")) != 2:
        logging.info("Invalid command")
        return

    filename = command.split(" ")[1]
    request_string = json.dumps({
        "type": "download",
        "payload": {
            "uuid": uuid,
            "filename": filename,
        }
    })
    client_socket.send(request_string.encode("utf-8"))


# Entry point of the script
if __name__ == "__main__":
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
        elif message.lower() == "help":
            help_message()
        elif "upload" in message.lower():
            upload_file(message)
        elif "download" in message.lower():
            download_file(message)
        else:
            send_message(message)
