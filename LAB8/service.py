import requests
import random
import time
import sys

from flask import Flask
from flask import request
from flask import jsonify

from node.util.raft import RAFTFactory
from models.book import Book
from models.database import db


service_info = {
    "host": "127.0.0.1",
    "port": int(sys.argv[1])
}

time.sleep(random.randint(1, 3))
node = RAFTFactory(service_info).create_server()
node.to_string()

cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

db_name = 'books'
if not node.leader:
    db_name += str(random.randint(1, 3))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_name}.db"
db.init_app(app)


@app.route("/api/book", methods=["GET"])
def get_books():
    books = Book.query.all()
    response = {"book": []}

    if len(books) != 0:
        for book in books:
            response["book"].append({
                "id": book.id,
                "name": book.name,
                "author": book.author
            })
        return jsonify(response), 200

    else:
        return jsonify({"error": "No Books in the database"}), 404


@app.route("/api/book/<int:book_id>", methods=["GET"])
def get_book_by_id(book_id):
    book = Book.query.get(book_id)

    if book is not None:
        return jsonify({
            "id": book.id,
            "name": book.name,
            "author": book.author,
        }), 200
    else:
        return jsonify({"error": "Book not found"}), 404


@app.route("/api/book", methods=["POST"])
def create_book():
    headers = dict(request.headers)
    if not node.leader and headers.get("Token") != "Leader":
        return {
            "message": "Access denied!"
        }, 403
    else:
        try:
            data = request.get_json()
            name = data.get("name")
            author = data.get("author")
            book = Book(
                name=name, author=author)

            db.session.add(book)
            db.session.commit()

            if node.leader:
                for follower in node.followers:
                    requests.post(f"http://{follower['host']}:{follower['port']}/api/book",
                                  json=request.json,
                                  headers={"Token": "Leader"})

            return jsonify({"message": "Book created successfully"}), 201
        except KeyError:
            return jsonify({"error": "Invalid request data"}), 400


@app.route("/api/book/<int:book_id>", methods=["PUT"])
def update_book_by_id(book_id):
    headers = dict(request.headers)
    if not node.leader and headers.get("Token") != "Leader":
        return {
            "message": "Access denied!"
        }, 403
    else:
        try:
            book = Book.query.get(book_id)
            if book is not None:
                data = request.get_json()

                book.name = data.get("name", book.name)
                book.author = data.get("author", book.author)

                db.session.commit()

                if node.leader:
                    for follower in node.followers:
                        requests.put(f"http://{follower['host']}:{follower['port']}/api/book/{book_id}",
                                     json=request.json,
                                     headers={"Token": "Leader"})

                return jsonify({"message": "Book updated successfully"}), 200
            else:
                return jsonify({"error": "Book not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/book/<int:book_id>", methods=["DELETE"])
def delete_book_by_id(book_id):
    headers = dict(request.headers)
    if not node.leader and headers.get("Token") != "Leader":
        return {
            "message": "Access denied!"
        }, 403
    else:
        try:
            book = Book.query.get(book_id)
            if book is not None:
                password = request.headers.get("Auth")

                if password == "confirm-deletion":
                    db.session.delete(book)
                    db.session.commit()

                    if node.leader:
                        for follower in node.followers:
                            requests.delete(f"http://{follower['host']}:{follower['port']}/api/book/{book_id}",
                                            headers={"Token": "Leader", "Auth": "confirm-deletion"})

                    return jsonify({"message": "Book deleted successfully"}), 200
                else:
                    return jsonify({"error": "Incorrect password"}), 401
            else:
                return jsonify({"error": "Book not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(
        host=service_info["host"],
        port=service_info["port"]
    )
