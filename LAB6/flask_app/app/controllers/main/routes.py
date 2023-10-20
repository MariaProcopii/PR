from flask import jsonify 
from app.controllers.main import bp


@bp.route("/")
def index():
    return jsonify({"message": "Electric Scooters API"}), 200 
