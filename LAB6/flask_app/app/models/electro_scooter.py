from app.extensions import db


class ElectroScooter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    battery_level = db.Column(db.Float, nullable=False)

    def __init__(self, name, battery_level):
        self.name = name
        self.battery_level = battery_level

    def __repr__(self):
        return f"<ElectroScooter({self.name}, {self.battery_level})>"