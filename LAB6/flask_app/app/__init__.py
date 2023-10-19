import os 
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

from config import Config
from app.extensions import db
from app.util.seeder import Seeder


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    db.create_all(app=app)

    seeder_enabled = os.getenv("SEEDER_ENABLED", 0)
    if seeder_enabled and int(seeder_enabled) == 1: 
        Seeder.init(app, silence_mode=True)
        Seeder.seed_electro_scooter(10)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix="/api/v1")

    from app.scooters import bp as scooters_bp
    app.register_blueprint(scooters_bp, url_prefix="/api/v1/scooter")

    swagger_ui_blueprint = get_swaggerui_blueprint(
        app.config.get("SWAGGER_URL"),
        app.config.get("API_URL"),
        config={
            'app_name': 'Access API'
        }
    )
    app.register_blueprint(swagger_ui_blueprint, url_prefix=app.config.get("SWAGGER_URL"))

    return app