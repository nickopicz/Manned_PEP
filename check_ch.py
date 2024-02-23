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
# Constants
FRAMES_DATABASE = "frames_data.db"


def get_trial_num():
    trial_num = 0
    conn = sqlite3.connect(FRAMES_DATABASE)
    try:
        trial_num = get_next_trial_number(conn)
    except Exception as e:
        print(f"Error getting next trial number: {e}")
        trial_num = 0
        create_tables(conn)
    return trial_num


class CANApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CAN Bus Monitoring")
        self.geometry('1600x1000')
        self.resizable(False, False)
        self.trial_num = get_trial_num()
        self.can_queue = stac
        self.db_queue = queue.Queue()
        self.running_event = Event()
        self.running_event.set()

        self.init_ui()
        self.init_threads()
        self.after(100, self.update_ui)

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
                        self.can_queue.put(formatted_message)
                        # Also add to DB queue for database storage
                        self.db_queue.put(msg)
                except canlib.CanNoMsg:
                    continue
                except Exception as e:
                    print(f"Error reading CAN message: {e}")
            ch.busOff()

    # investigate if there is a faster way to do this, with csv perhaps, or one single operation instead of many
    def database_thread_function(self):
        batch_size = 100  # Define the size of each batch
        while self.running_event.is_set() or not self.db_queue.empty():
            print("batch running")
            batch = []  # Initialize the batch list
            while len(batch) < batch_size:
                try:
                    # Try to get a message without blocking indefinitely
                    msg_data = self.db_queue.get(timeout=1)
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
                # store_to_db(batch, self.trial_num)

    def on_closing(self):
        self.running_event.clear()  # Signal threads to terminate
        self.can_thread.join()  # Wait for the CAN reading thread to finish
        self.db_thread.join()  # Wait for the database thread to finish
        self.destroy()  # Destroy the tkinter window

    def update_ui(self):
        # Periodic UI update logic goes here
        # Example of updating the CANVariableDisplay with a dummy message
        # This should be called periodically, e.g., using self.after(...)

        # value_range_map = {
        #     # COB-ID, Bytes : (Data Type, Description, Value Range, Units)
        #     (390, (0, 1)): ("U16", "Status word", "0-65535", ""),
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
        # }

        if not self.can_queue.empty():
            frame_data = self.can_queue.get()
            # print("getting can data: ", frame_data)

            self.can_variable_display.update_display(frame_data)
            # Add updates for other UI components as needed
            data_values = frame_data.get('data_values', {})

            speed = data_values.get('Actual Speed', (0,))[0]
            torque = data_values.get('Actual Torque', (0,))[0]  # Ass
            current = data_values.get(
                'Actual currents: iq', (0,))[0]
            print("speed: ", speed)
    # 'Motor measurements: DC bus current'
    # 'RMS motor Current'

            voltage = data_values.get(
                "DC bus voltage", (0,))[0]

            self.speedometer.update_dial(speed)
            self.graph.update_graph(torque)
            self.current_meter.update_dial(current)
            self.voltage_graph.update_graph(speed)

            # this is UI bottleneck
            self.after(1, self.update_ui)  # Adjust the delay as needed


if __name__ == "__main__":
    app = CANApplication()
    app.mainloop()
