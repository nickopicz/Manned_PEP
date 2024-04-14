#!/usr/bin/env python3
import tkinter as tk
from threading import Thread, Event
import queue
from Frames_database import get_next_trial_number, create_table_for_trial, store_data_for_trial
# Import the provided module components
from New_UI import CurrentMeter, Speedometer, ThermometerGauge, Compass
from Gather_Data import read_serial
# from database_functions import store_data_for_trial
import sqlite3
import time
import signal
import sys
import canopen
import logging
import time
from requests import put
import json
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


def read_and_log_sdo(node, index, subindex):

    try:
        value = node.sdo[index][subindex].raw
        return value
    except Exception as e:
        print(f"Error reading SDO [{hex(index)}:{subindex}]: {e}")
        return 0


def get_sdo_obj() -> {}:
    voltage = read_and_log_sdo(node, 0x2A06, 1)
    throttle_mv = read_and_log_sdo(node, 0x2013, 1)
    # print("throttle value: ", throttle_mv)
    throttle_percent = throttle_mv/2800

    rpm = read_and_log_sdo(node, 0x2001, 2)
    # print("rpm: ", rpm)
    # torque
    torque = read_and_log_sdo(node, 0x2076, 2)
    # current
    current = read_and_log_sdo(node, 0x2073, 1)
    
    power = current*rpm*1.4
    # temperature
    temperature = read_and_log_sdo(node, 0x2040, 2)
    
    serial_data = read_serial()
    # timestamp = read_and_log_sdo(node, 0x2002, 1)
    # print("timestamp: ", timestamp)
    #
    sdo_data = {
        'voltage': voltage,
        'throttle_mv': throttle_mv,
        'throttle_percentage': throttle_percent,
        'RPM': rpm,
        'torque': torque,
        'motor_temp': temperature,
        'current': current,
        'power':power
    } 
    full_data = {**serial_data, **sdo_data}
    return full_data


FRAMES_DATABASE = "frames_data.db"


def get_trial_num():
    # Ensure all necessary tables are created before fetching the trial number
    trial_num = 1
    try:
        trial_num = get_next_trial_number()
    except Exception as e:
        print(f"Error getting next trial number: {e}")
        trial_num = 1  # Default to 1 if unable to fetch next trial number
    print("trial number: ", trial_num)
    return trial_num


class CANApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CAN Bus Monitoring")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        #self.attributes("-fullscreen", True)
        self.configure(background="lightblue")
        # screenWidth = self.winfo_screenwidth()
        # screenHeight = self.winfo_screenheight()
        # # Set window size to screen dimensions
        # self.geometry(f"{screenWidth}x{screenHeight}+0+0")
        # self.geometry('1600x1280')
        # self.resizable(False, False)
        self.trial_num_initialized = Event()
        self.trial_num = 0
        self.init_trial_num()
        self.last_update_time = 0
        self.last_speed = 0
        self.db_queue = queue.Queue()
        self.running_event = Event()
        self.running_event.set()
        self.start_time = 0
        self.timestamp = self
        self.current_data = {}
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.init_ui()
        self.init_threads()

        self.update_queue = queue.Queue()
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
        #self.voltage_graph = VoltageGraph(self)
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

        # Clean up other resources
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
                # Add to CAN queue for UI update
                self.current_data = msg
                self.update_queue.put(msg)
                self.db_queue.put(msg)
                time.sleep(0.25)
            except Exception as e:
                time.sleep(1)
                # print(f"Error reading CAN message: {e}")

    def database_thread_function(self):
        batch_size = 50  # Define the size of each batch
        while self.running_event.is_set() and not self.db_queue.empty():
            print("batch running")
            batch = []  # Initialize the batch list
            while len(batch) < batch_size:
                try:
                    msg_data = self.db_queue.get(timeout=1)
                    batch.append(msg_data)
                except queue.Empty:
                    # If the queue is empty and we have collected some messages, break the loop to process them
                    if batch:
                        break
                    # If the queue is empty and no messages are collected, continue checking
                    continue

            if len(batch) == 50:
                print("storing to db : ", len(batch))
                # If we have messages in the batch, store them to the database
                store_data_for_trial(batch, self.trial_num)

    def send_to_shore(self):
        # Replace with your actual URL
        url = 'https://hugely-dashing-lemming.ngrok-free.app/put_method'
        while self.running_event.is_set():
            if self.current_data:  # Check if there is data to send
                try:
                    # Directly pass the dictionary to the json parameter of the post method
                    
#                     print("current data: ", self.current_data)
                    response = put(url, json=self.current_data)
                    if response.ok:
                        print("Data sent successfully!")
                    else:
                        print(
                            f"Failed to send data. Status code: {response.status_code}")
                except Exception as e:
                    print(f"Failed to send data: {e}")
            time.sleep(0.25)  # Adjust the sleep time as needed


# Check response from the server
        if response.ok:
            print("Data sent successfully!")
        else:
            print("Failed to send data.")

        self.after(250, self.send_to_shore)

    def update_ui(self, data):
       
        try:
            speed = data['RPM']
            torque = data['torque']
            motor_temp = data['motor_temp']
            current = data['current']
            throttle_prct = data['throttle_percentage']
            throttle_mv = data['throttle_mv']
            # print("data: ", throttle_mv)

            timestamp = data['timestamp']

            voltage = data['voltage']
            heading = data['heading']

            # self.can_variable_display.update_display(data)
            # Add updates for other UI components as needed
            if motor_temp:
                self.thermometer.update_gauge(motor_temp)
           # if throttle_mv:
               # self.throttle_gauge.update_gauge(throttle_mv)
            if speed:
                self.speedometer.update_dial(speed)
#             if torque:
#                 self.graph.update_graph(torque, timestamp)
            if current:
                self.current_meter.update_dial(current)
#             if voltage:
#                 self.voltage_graph.update_graph(current, timestamp)
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
