import re
import socket
import signal
import sys
import threading

from Product import Product

products = [
    Product(1, "Product1", "Luciano Ramalho", 39.95, "Description 1"),
    Product(2, "Product2", "Lesenco Maria", 100.98, "Description 2"),
    Product(3, "Product3", "Procopii Maria", 100, "Description 3")
]


HOST = '127.0.0.1'
PORT = 8080
RECEIVED_BYTES = 4096
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))

server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}")

def handle_request(client_socket):
    request_data = client_socket.recv(RECEIVED_BYTES).decode('utf-8')
    print(f"Received Request:\n{request_data}")

    request_lines = request_data.split('\n')
    request_line = request_lines[0].strip().split()
    method = request_line[0]
    path = request_line[1]

    response_content = ''
    status_code = 200

    if path == '/':
        response_content = f'''
                                        <!DOCTYPE html>
                                        <html lang="en">
                                        <head>
                                            <meta charset="UTF-8">
                                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                            <title>Home Page</title>
                                        </head>
                                        <body>
                                            <div class="product">
                                                <p>Home Page<p>
                                                <a href="http://{HOST}:{PORT}/about"> About Us</a>
                                                <br>
                                                <a href="http://{HOST}:{PORT}/contacts"> Contacts</a>
                                                <br>
                                                <a href="http://{HOST}:{PORT}/products"> Products</a>
                                                <br>
                                            </div>
                                        </body>
                                        </html>
        '''

    elif path == "/about":
        response_content = f'''
                                        <!DOCTYPE html>
                                        <html lang="en">
                                        <head>
                                            <meta charset="UTF-8">
                                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                            <title>About Page</title>
                                        </head>
                                        <body>
                                            <div class="about">
                                                <p>About Us :3<p>
                                            </div>
                                        </body>
                                        </html>
        '''
    elif path == "/contacts":
        response_content = f'''
                                        <!DOCTYPE html>
                                        <html lang="en">
                                        <head>
                                            <meta charset="UTF-8">
                                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                            <title>Contacts Page</title>
                                        </head>
                                        <body>
                                            <div class="contact">
                                                <p>Contact: 069889092<p>
                                            </div>
                                        </body>
                                        </html>
        '''
    elif path == '/products':
        response_content = f'''
                                        <!DOCTYPE html>
                                        <html lang="en">
                                        <head>
                                            <meta charset="UTF-8">
                                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                            <title>Products Page</title>
                                        </head>
                                        <body>
        '''
        for product in products:
            response_content += f'''
                                        
                                        <div class="product-description">
                                            <a href="http://{HOST}:{PORT}/products/{product.id}">{product.name}</a>
                                            <p>{product.author}<p>
                                        </div>
                                    
            '''

        response_content += "</body>" \
                            "</html>"

    elif re.match(r'^/products/(\d+)$', path):
        for product in products:
            if product.id == int(path[-1]):
                print(product)
                response_content = f'''
                                <!DOCTYPE html>
                                <html lang="en">
                                <head>
                                    <meta charset="UTF-8">
                                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                    <title>Product Description</title>
                                </head>
                                <body>
                                    <div class="product">
                                        <p class="product-name">Product Name: {product.name}</p>
                                        <p class="author">Author: {product.author}</p>
                                        <p class="price">Price: {product.price}</p>
                                        <p class="description">Description: {product.description}</p>
                                    </div>
                                </body>
                                </html>
'''
                break
            else:
                response_content = f'''
                                                <!DOCTYPE html>
                                                <html lang="en">
                                                <head>
                                                    <meta charset="UTF-8">
                                                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                                    <title>File not found</title>
                                                </head>
                                                <body>
                                                    <div class="not found">
                                                        <p>File Not Found<p>
                                                    </div>
                                                </body>
                                                </html>
                '''
                status_code = 404

    else:
        response_content = f'''
                                        <!DOCTYPE html>
                                        <html lang="en">
                                        <head>
                                            <meta charset="UTF-8">
                                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                            <title>File not found</title>
                                        </head>
                                        <body>
                                            <div class="not found">
                                                <p>File Not Found<p>
                                            </div>
                                        </body>
                                        </html>
        '''
        status_code = 404

    response = f'HTTP/1.1 {status_code} OK\nContent-Type: text/html\n\n{response_content}'
    print("THIS IS THE:", response)
    client_socket.send(response.encode('utf-8'))

    client_socket.close()

def signal_handler(sig, frame):
    print("\nShutting down the server...")
    server_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

    client_handler = threading.Thread(target=handle_request, args=(client_socket,))

    client_handler.start()
