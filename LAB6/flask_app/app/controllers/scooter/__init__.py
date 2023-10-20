from flask import Blueprint

bp = Blueprint("scooters", __name__)

from app.controllers.scooter import routes
