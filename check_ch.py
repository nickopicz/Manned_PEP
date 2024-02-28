#!/usr/bin/env python3

import tkinter as tk
from threading import Thread, Event
import queue
from canlib import canlib
from Frames_database import get_next_trial_number, create_tables, store_frames_to_database
from maps import format_can_message
# Import the provided module components
from New_UI import CANVariableDisplay, CurrentMeter, Speedometer, Graph, VoltageGraph
from database_functions import store_to_db
import sqlite3
import time
from database_functions import create_table_for_pdo
# Constants

FRAMES_DATABASE = "frames_data.db"


def create_tables(conn):
    # Ensure this function creates all necessary tables, including the 'meta' table
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value INTEGER
    )
    ''')
    # Add creation of other necessary tables here
    # e.g., frame_data, any PDO-specific tables, etc.
    conn.commit()


def get_trial_num():
    with sqlite3.connect(FRAMES_DATABASE) as conn:
        # Ensure all necessary tables are created before fetching the trial number
        create_tables(conn)  # This ensures the 'meta' table exists
        trial_num = 0
        try:
            trial_num = get_next_trial_number(conn)
        except Exception as e:
            print(f"Error getting next trial number: {e}")
            trial_num = 1  # Default to 1 if unable to fetch next trial number
        print("trial number: ", trial_num)
        return trial_num


class CANApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CAN Bus Monitoring")
        self.geometry('1600x1000')
        self.resizable(False, False)
        self.trial_num = get_trial_num()
        self.can_queue = queue.Queue()
        self.last_update_time = 0
        self.last_speed = 0
        self.db_queue = queue.Queue()
        self.running_event = Event()
        self.running_event.set()
        self.init_ui()
        self.init_threads()
        # self.check_queue()

    def init_ui(self):
        # Initialize the provided module components here
        self.can_variable_display = CANVariableDisplay(self)
        self.current_meter = CurrentMeter(self)
        self.speedometer = Speedometer(self)
        self.graph = Graph(self)
        self.voltage_graph = VoltageGraph(self)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def init_threads(self):
        self.can_thread = Thread(target=self.read_can_messages, daemon=True)
        self.db_thread = Thread(
            target=self.database_thread_function, daemon=True)
        self.can_thread.start()
        self.db_thread.start()

    def on_closing(self):
        self.running_event.clear()  # Signal threads to terminate
        self.can_thread.join()  # Wait for the CAN reading thread to finish
        self.db_thread.join()  # Wait for the database thread to finish
        self.destroy()  # Destroy the tkinter window

    def read_can_messages(self):
        channel = 0
        with canlib.openChannel(channel, canlib.canOPEN_ACCEPT_VIRTUAL) as ch:
            ch.setBusOutputControl(canlib.canDRIVER_SILENT)
            ch.setBusParams(canlib.canBITRATE_500K)
            ch.busOn()
            while self.running_event.is_set():
                try:
                    msg = ch.read()
                    if msg.flags & canlib.MessageFlag.ERROR_FRAME:
                        print(
                            f"Error frame detected: Timestamp {msg.timestamp}")
                    else:
                        formatted_message = format_can_message(msg)
                        # Add to CAN queue for UI update
                        self.update_ui(formatted_message)
                        # Also add to DB queue for database storage
                        self.db_queue.put(msg)
                except canlib.CanNoMsg:
                    continue
                except Exception as e:
                    print(f"Error reading CAN message: {e}")
            ch.busOff()

    # investigate if there is a faster way to do this, with csv perhaps, or one single operation instead of many
    def database_thread_function(self):
        batch_size = 1000  # Define the size of each batch
        while self.running_event.is_set() or not self.db_queue.empty():
            print("batch running")
            batch = []  # Initialize the batch list
            while len(batch) < batch_size:
                try:
                    # Try to get a message without blocking indefinitely
                    msg_data = self.db_queue.get(timeout=0.1)
                    batch.append(msg_data)
                except queue.Empty:
                    # If the queue is empty and we have collected some messages, break the loop to process them
                    if batch:
                        break
                    # If the queue is empty and no messages are collected, continue checking
                    continue

            if batch:
                print("storing to db : ", len(batch))
                # If we have messages in the batch, store them to the database
                store_to_db(batch, self.trial_num)

    def update_ui(self, data):
        #     (390, (2, 3)): ("S16", "Actual speed", "-32768 to 32767", "Rpm"),
        #     (390, (4, 5)): ("U16", "RMS motor Current", "0-65535", "Arms"),
        #     (390, (6, 7)): ("S16", "DC Bus Voltage", "-32768 to 32767", "Adc"),
        #     (646, (0, 1)): ("S16", "Internal Speed Reference", "-32768 to 32767", "Rpm"),
        #     (646, (2, 3)): ("S16", "Reference Torque", "-32768 to 32767", "Nm"),
        #     (646, (4, 5)): ("S16", "Actual Torque", "-32768 to 32767", "Nm"),
        #     (646, (6, 7)): ("S16", "Field weakening control: voltage angle", "-32768 to 32767", "Deg"),
        #     (902, 0): ("U8", "Field weakening control: regulator status", "0-255", ""),
        #     (902, 1): ("U8", "Current limit: actual limit type", "0-15", ""),
        #     (902, (2, 3)): ("S16", "Motor voltage control: U peak normalized", "-32768 to 32767", ""),
        #     (902, (4, 5)): ("U16", "Digital status word", "0-65535", ""),
        #     (902, (6, 7)): ("S16", "Scaled throttle percent", "-32768 to 32767", ""),
        #     (1158, (0, 1)): ("S16", "Motor voltage control: idLimit", "-32768 to 32767", ""),
        #     (1158, (2, 3)): ("S16", "Motor voltage control: Idfiltered", "-32768 to 32767", "Arms"),
        #     (1158, (4, 5)): ("S16", "Actual currents: iq", "-32768 to 32767", "Apk"),
        #     (1158, (6, 7)): ("S16", "Motor measurements: DC bus current", "-32768 to 32767", "Adc"),
        current_time = time.time()
        if (current_time - self.last_update_time) >= 0.05:  # Check if 50 ms have passed
            self.last_update_time = current_time  # Update the last update time
            self.can_variable_display.update_display(data)
            # Add updates for other UI components as needed
            data_values = data.get('data_values', {})

            speed = abs(data_values.get('Actual speed', (0,))[0]/10)
            if speed < 10 or speed == 1024 or speed == 256:
                speed = self.last_speed
            else:
                self.last_speed = speed
            torque = data_values.get('Actual Torque', (0,))[0]  # Ass
            current = data_values.get(
                'RMS motor Current', (0,))[0]

            voltage = data_values.get(
                "DC bus voltage", (0,))[0]

            self.speedometer.update_dial(speed)
            # self.graph.update_graph(torque)
            self.current_meter.update_dial(current)
            # self.voltage_graph.update_graph(voltage)

            # this is UI bottleneck


if __name__ == "__main__":
    app = CANApplication()
    app.mainloop()
