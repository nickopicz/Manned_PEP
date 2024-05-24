#!/usr/bin/env python3


# This is the main script that is run on reboot. Setting up reboot on a new raspberry pi is simple. use crontab,
# look it up or use chatGPT to help setup, in depth documentation will be in the user manual

import tkinter as tk
from threading import Thread, Event
import queue
from Frames_database import get_next_trial_number, create_table_for_trial, store_data_for_trial
# Import the provided module components
from New_UI import CurrentMeter, Speedometer, ThermometerGauge, Compass
from Gather_Data import read_serial
# from database_functions import store_data_for_trial
import sqlite3
import signal
import sys
import canopen
import logging
import time
from requests import put
import json
import math
# Set up logging
logging.basicConfig(level=logging.INFO, filename='canbus_log.txt', filemode='w',
                    format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to log messages


def log_message(message):
    logger.info(f"Message: {message}")


# Start with creating a new network representing one CAN bus
network = canopen.Network()

# Connect to the CAN bus
network.connect(channel='0', bustype='kvaser')

# Subscribe to messages
network.subscribe(0, log_message)

# You can create a node with a known node-ID
node_id = 6  # Replace with your node ID
node = canopen.BaseNode402(node_id, canopen.import_od('/home/pi/Manned_PEP/testing/69GUS222C00x05.epf')
                           )  # Use a dummy EDS here
network.add_node(node)


# The SDO index (or address) is found in the parameters.csv file.
def read_and_log_sdo(node, index, subindex):

    try:
        value = node.sdo[index][subindex].raw
        return value
    except Exception as e:
        print(f"Error reading SDO [{hex(index)}:{subindex}]: {e}")
        return 0


# These are SDOs retrieved from the controller via CANbus using above function
# There is a wide list of sensor data that can be read, but these are the useful ones.
# Feel free to browse the parameter list which is in testing/parameters.csv
def get_sdo_obj() -> {}:
    voltage = read_and_log_sdo(node, 0x2A06, 1)  # Volts
    throttle_mv = read_and_log_sdo(node, 0x2013, 1)  # mV
    rpm = read_and_log_sdo(node, 0x2001, 2)  # rpm
    current = read_and_log_sdo(node, 0x2073, 1)  # Arms
    temperature = read_and_log_sdo(node, 0x2040, 2)  # deg C

    serial_data = read_serial()  # data from Arduino

    throttle_percent = throttle_mv/2800  # %

    # this torque must be converted to lb*ft, because it is preferred
    torque = current*0.15  # Nm

    power = (torque*rpm)*math.pi/30000  # kW

    sdo_data = {
        'voltage': voltage,
        'throttle_mv': throttle_mv,
        'throttle_percentage': throttle_percent,
        'RPM': rpm,
        'torque': torque,
        'motor_temp': temperature,
        'current': current,
        'power': power
    }
    full_data = {**serial_data, **sdo_data}
    return full_data


class CANApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CAN Bus Monitoring")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.configure(background="lightblue")
        self.trial_num_initialized = Event()

        # trial num is unique to each time the program
        # successfully launches and collects data
        # if you clear the database, the trial num obviously sets back to 1
        self.trial_num = 0
        self.init_trial_num()
        # Queues are used because for other threads to access the latest data
        # (UI queue is cleared when data gets displayed to remove latency)
        self.db_queue = queue.Queue()
        self.update_queue = queue.Queue()
        # starting an event so that the functions in the threads know when to start and stop
        self.running_event = Event()
        self.running_event.set()
        self.start_time = 0
        self.timestamp = self
        self.current_data = {}
        # if you close the window somehow, it ends the program, including all threads
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # launching ui
        self.init_ui()
        # starting the threads
        self.init_threads()

        self.after(100, self.process_ui_updates)
        # self.check_queue()

    def init_trial_num(self):
        self.trial_num = get_next_trial_number()
        print(f"Initialized trial number: {self.trial_num}")
        self.trial_num_initialized.set()

    def init_ui(self):
        # Initialize the provided module components here
        # self.can_variable_display = CANVariableDisplay(self)
        self.current_meter = CurrentMeter(self)
        self.speedometer = Speedometer(self)
        self.thermometer = ThermometerGauge(self)
       # self.graph = Graph(self)
        # self.voltage_graph = VoltageGraph(self)
#         self.throttle_gauge = ThrottleGauge(self)
        self.compass = Compass(self)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def process_ui_updates(self):
        try:
            while not self.update_queue.empty():
                data = self.update_queue.get_nowait()
                # Update the UI with data
                self.update_ui(data)
        finally:
            self.after(100, self.process_ui_updates)

    def init_threads(self):
        self.running_event = Event()
        self.running_event.set()
        self.trial_num_initialized.wait()
        self.can_thread = Thread(
            target=self.read_can_messages, daemon=True)
        self.db_thread = Thread(
            target=self.database_thread_function, daemon=True
        )
        self.server_thread = Thread(
            target=self.send_to_shore, daemon=True
        )
        self.can_thread.start()
        self.db_thread.start()
        self.server_thread.start()

    def on_closing(self):
        print("Closing application...")
        self.running_event.clear()

    # Wait for the threads to finish if you have non-daemon threads or if they need to do cleanup
        self.can_thread.join(timeout=1)
        self.db_thread.join(timeout=1)
        self.server_thread.join(timeout=1)

        # Disconnect the CAN network
        network.disconnect()

        # Destroy the Tkinter app window
        self.destroy()

    def read_can_messages(self):
        # Start with creating a new network representing one CAN bus
        self.start_time = round(time.time() * 1000)
        print("finished waiting: ", self.trial_num)
        while self.running_event.is_set():
            try:
                current_time = round(time.time()*1000 - self.start_time)
                msg = get_sdo_obj()

                msg['timestamp'] = current_time
                msg['trial_num'] = self.trial_num
                # Add to "update_queue" for UI update and "db_queue" for database operations
                self.current_data = msg

                # maybe remove this if getting any the error, experimental feature
                if self.update_queue.qsize() > 1:
                    try:
                        self.update_queue.get_nowait()
                    except Exception as e:
                        print("error dequeing: ", e)

                self.update_queue.put(msg)

                self.db_queue.put(msg)
                time.sleep(0.1)
            except Exception as e:
                time.sleep(0.25)
                print(f"Error reading CAN message: {e}")

    # This function uses batch calls to reduce the amount of latency while doing database operations
    # batches of 50 should be enough depending on the frequency of data reading (see "read_can_messages()" delays in the loop to change sample rate)
    def database_thread_function(self):
        batch_size = 50  # Define the size of each batch

        while self.running_event.is_set():
            # Initialize the batch list outside of the while loop
            batch = []
            while len(batch) < batch_size:
                try:

                    msg_data = self.db_queue.get_nowait()
                    batch.append(msg_data)
                except queue.Empty:
                    # If the queue is empty and we have collected some messages, break the loop to process them
                    if batch:
                        break
                    # If the queue is empty and no messages are collected, continue checking
                    continue

            # If we have messages in the batch, store them to the database
            if batch:
                store_data_for_trial(batch, self.trial_num)
                batch.clear()

    def send_to_shore(self):
        # Replace with your URL generated on ngrok (more info found in "initiate_server.py"  in the shore directory)
        url = 'https://hugely-dashing-lemming.ngrok-free.app/put_method'
        while self.running_event.is_set():
            if self.current_data:  # Check if there is data to send
                try:
                    # Directly pass the dictionary to the json parameter of the post method

                    response = put(url, json=self.current_data)
                    if response.ok:
                        print("Data sent successfully!")
                    else:
                        print(
                            f"Failed to send data. Status code: {response.status_code}")
                except Exception as e:
                    print(f"Failed to send data: {e}")
            time.sleep(0.25)  # Adjust the sleep time as needed

        # this is to call recursively, after 250 milliseconds, so the data can send forever (until script ends or pi shuts down)
        self.after(250, self.send_to_shore)

    def update_ui(self, data):

        try:
            speed = data['RPM']
            torque = data['torque']
            motor_temp = data['motor_temp']
            current = data['current']
            throttle_prct = data['throttle_percentage']
            throttle_mv = data['throttle_mv']
            timestamp = data['timestamp']
            voltage = data['voltage']
            heading = data['heading']

            # Add updates for any aditional UI components as needed
            if motor_temp:
                self.thermometer.update_gauge(motor_temp)
            if speed:
                self.speedometer.update_dial(abs(speed))
            if current:
                self.current_meter.update_dial(abs(current))
            if heading:
                self.compass.update_compass(heading)
        except Exception as e:
            print("error updating UI: ", e)


if __name__ == "__main__":
    app = CANApplication()

    def handle_sigint(signal, frame):
        print("CTRL+C detected. Closing application...")
        app.on_closing()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.on_closing()
