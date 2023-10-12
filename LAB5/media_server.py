import json
import sys
import base64
import logging
import signal
import socket
import threading

# Server's host
HOST = "127.0.0.1"
# Server's port
PORT = 12445
# Byte chunk received from the tcp connecion
RECEIVED_BYTES = 4096 * 1000000

# Logger init with formatter config
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Server IPv4 TCP socket with additional params set up
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Server blocking and listening to (host):(port)
server_socket.bind((HOST, PORT))
server_socket.listen()
logging.info(f"Media Server is listening on {HOST}:{PORT}")

# Script exiting handler


def signal_handler(sig, frame):
    logging.info("Shutting down the server...")
    server_socket.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# Handler functions


def upload(client_socket, client_address, request_json):
    logging.info(request_json)
    sender = request_json.get("payload").get("sender")
    filename = request_json.get("payload").get("filename")
    filebytes = base64.b64decode(request_json.get("payload").get("file"))
    if not filebytes:
        logging.info(f"Received no file bytes")
        client_socket.send(json.dumps({
            "type": "upload",
            "payload": {
                "message": "Received no file bytes.",
            }
        }).encode("utf-8"))
        return

    try:
        with open("server_media/"+filename, "wb") as file:
            file.write(filebytes)
            logging.info(f"Successfully saved {filename} from {sender}")
    except Exception as e:
        logging.info(f"Error while saving {filename} from {sender}")
        logging.info(f"ERROR: {e}")
        client_socket.send(json.dumps({
            "type": "upload",
            "payload": {
                "message": f"{e}",
            }
        }).encode("utf-8"))
        return

    client_socket.send(json.dumps({
        "type": "upload",
        "payload": {
            "message": "Successfully uploaded the file",
        }
    }).encode("utf-8"))


def download(client_socket, client_address, request_json):
    uuid = request_json.get("payload").get("uuid")
    filename = request_json.get("payload").get("filename")
    filebytes = b""

    try:
        with open("server_media/"+filename, "rb") as file:
            filebytes = file.read()
    except FileNotFoundError:
        logging.info(f"File {filename} doesn't exist")
        return
    
    request_string = json.dumps({
        "type": "download",
        "payload": {
                "uuid": uuid,
                "filename": filename,
                "file": str(base64.b64encode(filebytes), "utf-8"),
        }
    })
    client_socket.send(request_string.encode("utf-8"))



# Main handler


def handle_client(client_socket, client_address):
    while True:
        request_string = client_socket.recv(RECEIVED_BYTES).decode("utf-8")
        if not request_string:
            break

        request_json = json.loads(request_string)
        if request_json.get("type") == "upload":
            upload(client_socket, client_address, request_json)
        elif request_json.get("type") == "download":
            download(client_socket, client_address, request_json)


# Entry point of the script
if __name__ == "__main__":
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(
            target=handle_client, args=(client_socket, client_address,))
        client_thread.start()
