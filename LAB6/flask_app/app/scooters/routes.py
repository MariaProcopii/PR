import os

from flask import request, jsonify
from app.extensions import db
from app.scooters import bp
from app.models.electro_scooter import ElectroScooter


@bp.route("/", methods=["GET"])
def index():
    electro_scooters = ElectroScooter.query.all()
    return jsonify({"electro_scooters_list": [{"name": e.name, "battery_level": e.battery_level} for e in electro_scooters]}), 200


@bp.route("/", methods=["POST"])
def create_scooter():
    data = request.get_json()
    electro_scooter = ElectroScooter(
        data.get("name"), data.get("battery_level"))

    db.session.add(electro_scooter)
    db.session.commit()

    return jsonify({"message": "Successfully created resource"}), 201


@bp.route("/<int:id>", methods=["GET"])
def get_scooter_by_id(id):
    electro_scooter = ElectroScooter.query.get(id)
    if not electro_scooter:
        return jsonify({"error": f"No such record with {id}"}), 404
    return jsonify({"electro_scooter": {"name": electro_scooter.name, "battery_level": electro_scooter.battery_level}}), 200


@bp.route("/<int:id>", methods=["PUT"])
def update_scooter_by_id(id):
    electro_scooter = ElectroScooter.query.get(id)
    if not electro_scooter:
        return jsonify({"error": f"No such record with {id}"}), 404

    data = request.get_json()

    electro_scooter.name = data.get("name", electro_scooter.name)
    electro_scooter.battery_level = data.get(
        "battery_level", electro_scooter.battery_level)
    db.session.commit()

    return jsonify({"message": "Successfully updated resource"}), 200


@bp.route("/<int:id>", methods=["DELETE"])
def delete_scooter_by_id(id):
    electro_scooter = ElectroScooter.query.get(id)
    if not electro_scooter:
        return jsonify({"error": f"No such recored with {id}"}), 404

    auth = request.headers.get("Authorization")
    if auth == os.getenv("AUTHORIZATION_KEY"):
        db.session.delete(electro_scooter)
        db.session.commit()
        return jsonify({"message": "Successfully deleted resource"}), 200

    return jsonify({"error": "Not authorized request"}), 401