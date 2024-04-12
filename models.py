from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class DataEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.BigInteger, nullable=False)  # For tracking time
    trial_num = db.Column(db.Integer)
    voltage = db.Column(db.Float)
    throttle_mv = db.Column(db.Integer)
    throttle_percentage = db.Column(db.Integer)
    rpm = db.Column(db.Integer)
    torque = db.Column(db.Float)
    motor_temp = db.Column(db.Float)
    current = db.Column(db.Float)
    power = db.Column(db.Float)
    pitch = db.Column(db.Float)
    roll = db.Column(db.Float)
    yaw = db.Column(db.Float)
    ax = db.Column(db.Float)
    ay = db.Column(db.Float)
    az = db.Column(db.Float)
    heading = db.Column(db.Float)
