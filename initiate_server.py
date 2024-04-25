from flask import Flask, request, jsonify
from pyngrok import ngrok
from datetime import time
from models import db, DataEntry
import os
app = Flask(__name__)

# The first thing you must do to get this script/server to run, you must get a new domain to host a server on
# The way this has been done for the original script was using ngrok. It is free and
# sufficient as there is no reason to have better domain since 'having a cool domain name' is useless
# Using ngrok is simple, just login with github, and go to the dashboard. Navigate to the -
# Cloud Edge section on the left tabs, and click domains. Next just do what seems obvious.

# This is the function that is called to start the database,
# will only run once when script is started
# Nothing will happen unless you completely wipe the "live_data.db" file


def create_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'live_data.db')
    db.init_app(app)
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created.")


# POST method
create_app()


# If you add or remove any data being sent or displayed, you must make changes to all of the-
# dependencies associated with the data object. This includes:
# DataEntry class,
# data object sent from raspberrypi,
# data object from GET in shore_ui.py,
# "new_entry" from "put_data()" method below,
# "entry_data" from "get_data()" method below


@app.route('/put_method', methods=['PUT'])
def put_data():
    # Extract data from the incoming request
    data = request.get_json()
    print("data received: ", data)
    # Create a new DataEntry object with the received data
    new_entry = DataEntry(
        timestamp=data['timestamp'],
        voltage=data['voltage'],
        throttle_mv=data['throttle_mv'],
        throttle_percentage=data['throttle_percentage'],
        rpm=data['RPM'],
        torque=data['torque'],
        motor_temp=data['motor_temp'],
        current=data['current'],
        power=data['power'],
        trial_num=data['trial_num'],
        pitch=data['pitch'],
        roll=data['roll'],
        yaw=data['yaw'],
        ax=data['ax'],
        ay=data['ay'],
        az=data['az'],
        heading=data['heading']
    )

    # Insert the new entry into the database
    db.session.add(new_entry)
    db.session.commit()

    return jsonify(message="Data stored successfully."), 201


@app.route('/get_data', methods=['GET'])
def get_data():
    # most recent timestamp value.
    max_trial_number = db.session.query(
        db.func.max(DataEntry.trial_num)).scalar()
    entry = DataEntry.query.filter_by(trial_num=max_trial_number).order_by(
        DataEntry.timestamp.desc()).first()
    if entry:
        print("trial num before sending back: ", entry.trial_num)
        entry_data = {
            # Assuming timestamp is a datetime object
            'trial_num': entry.trial_num,
            'timestamp': entry.timestamp,
            'voltage': entry.voltage,
            'throttle_mv': entry.throttle_mv,
            'throttle_percentage': entry.throttle_percentage,
            'RPM': entry.rpm,
            'torque': entry.torque,
            'motor_temp': entry.motor_temp,
            'current': entry.current,
            'power': entry.power,
            'pitch': entry.pitch,
            'roll': entry.roll,
            'yaw': entry.yaw,
            'ax': entry.ax,
            'ay': entry.ay,
            'az': entry.az,
            'heading': entry.heading
        }
        return jsonify(entry_data)
    else:
        return jsonify(message="No data available."), 404


# def create_tables():


if __name__ == '__main__':
    # Setup ngrok
    ngrok_tunnel = ngrok.connect(
        addr=5000, hostname="hugely-dashing-lemming.ngrok-free.app")
    print('NGROK Tunnel URL:', ngrok_tunnel.public_url)

    # Run Flask app
    app.run(port=5000)
