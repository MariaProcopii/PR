from flask import Blueprint

bp = Blueprint("main", __name__)

from app.controllers.main import routes
