from flask import Blueprint

bp = Blueprint("scooters", __name__)

from app.scooters import routes