import socket
from bs4 import BeautifulSoup


HOST = "127.0.0.1"
PORT = 8080
RECEIVED_BYTES = 4096 #fuck the bytes aaaaaa, o ora de debuging

scraped_links = []
scraped_data = []


def request(link):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    request_string = f"GET {link.replace('http://'+HOST+':'+str(PORT), '')} HTTP/1.1\nHOST: {HOST}:{PORT}"

    client_socket.send(request_string.encode("utf-8"))

    response = client_socket.recv(RECEIVED_BYTES).decode("utf-8")

    client_socket.close()

    return response

def parse(response):
    response = response.replace("HTTP/1.1 200 OK\nContent-Type: text/html\n", "")
    soup = BeautifulSoup(response, "html.parser")

    for name, author, price, description in zip(soup.select("p.product-name"), soup.select("p.author"), soup.select("p.price"), soup.select("p.description")):
        scraped_data.append({
            "name": name.text,
            "author": author.text,
            "price": price.text,
            "description": description.text,
        })

    internal_links = [link.get("href") for link in soup.find_all("a")]
    for link in internal_links:
        if link not in scraped_links:
            scraped_links.append(link)
            response = request(link)
            parse(response)
    else:
        with open(f"{soup.title.string}.html", "w") as page:
            page.write(soup.prettify())


if __name__ == "__main__":
    link = f"http://{HOST}:{PORT}/"
    scraped_links.append(link)  
    response = request(link)
    parse(response)
    print(scraped_data)
