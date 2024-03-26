from flask import Flask, request, jsonify
from pyngrok import ngrok
from datetime import time
from models import db, DataEntry
import os
app = Flask(__name__)


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
        trial_num=data['trial_num']
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
            'current': entry.current
        }
        return jsonify(entry_data)
    else:
        return jsonify(message="No data available."), 404


# @app.before_first_request
# def create_tables():


if __name__ == '__main__':
    # Setup ngrok
    ngrok_tunnel = ngrok.connect(
        addr=5000, hostname="hugely-dashing-lemming.ngrok-free.app")
    print('NGROK Tunnel URL:', ngrok_tunnel.public_url)

    # Run Flask app
    app.run(port=5000)
