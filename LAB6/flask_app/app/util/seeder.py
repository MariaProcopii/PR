import string
import random

from app.extensions import db
from app.models.electro_scooter import ElectroScooter


class Seeder:

    _app = None
    _context = None

    _silence_mode = False

    @staticmethod
    def init(app, **kwargs):
        if not app:
            raise Exception("Application not provided for the Seeder")

        Seeder.set_application(app)
        Seeder.set_context(app)
        for key, value in kwargs.items():
            Seeder.set_optional(key, value)

    @staticmethod
    def set_application(app):
        Seeder._app = app

    @staticmethod
    def get_application():
        return Seeder._app

    @staticmethod
    def set_context(app):
        Seeder._context = app.app_context

    @staticmethod
    def get_context():
        return Seeder._context

    @staticmethod
    def set_optional(key, value):
        if key == "silence_mode":
            Seeder._silence_mode = value

    @staticmethod
    def get_silence_mode():
        return Seeder._silence_mode

    @staticmethod
    def seed_electro_scooter(number_of_records):
        context = Seeder.get_context()
        with context():
            for _ in range(number_of_records):
                name = "".join(random.choice(string.ascii_letters)
                               for _ in range(1, random.randint(5, 50)))
                battery_level = random.randint(1, 100)
                electro_scooter = ElectroScooter(name, battery_level)
                db.session.add(electro_scooter)
                if not Seeder.get_silence_mode():
                    print(electro_scooter)
                    print("---")
                db.session.commit()