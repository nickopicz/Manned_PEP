#!/usr/bin/env python3

import sqlite3
from canlib import canlib
import time
import struct
import os
import tkinter as tk
from database_functions import create_table_for_pdo, store_to_db
from Frames_database import get_next_trial_number, create_tables
import queue
import threading
import signal
from New_UI import Graph, CANVariableDisplay, Speedometer, CurrentMeter, VoltageGraph
from Frames_database import store_frames_to_database
from maps import format_can_message
# Mapping from COB-ID to PDO and its information

# FRAMES_DATABASE = "db/frames_data.db"
FRAMES_DATABASE = "./db/frames_data.db"

db_queue = queue.Queue()
can_queue = queue.Queue()
running = True

value_range_map = {
    # COB-ID, Bytes : (Data Type, Description, Value Range, Units)
    (390, (0, 1)): ("U16", "Status word", "0-65535", ""),
    (390, (2, 3)): ("S16", "Actual speed", "-32768 to 32767", "Rpm"),
    (390, (4, 5)): ("U16", "RMS motor Current", "0-65535", "Arms"),
    (390, (6, 7)): ("S16", "DC Bus Voltage", "-32768 to 32767", "Adc"),
    (646, (0, 1)): ("S16", "Internal Speed Reference", "-32768 to 32767", "Rpm"),
    (646, (2, 3)): ("S16", "Reference Torque", "-32768 to 32767", "Nm"),
    (646, (4, 5)): ("S16", "Actual Torque", "-32768 to 32767", "Nm"),
    (646, (6, 7)): ("S16", "Field weakening control: voltage angle", "-32768 to 32767", "Deg"),
    (902, 0): ("U8", "Field weakening control: regulator status", "0-255", ""),
    (902, 1): ("U8", "Current limit: actual limit type", "0-15", ""),
    (902, (2, 3)): ("S16", "Motor voltage control: U peak normalized", "-32768 to 32767", ""),
    (902, (4, 5)): ("U16", "Digital status word", "0-65535", ""),
    (902, (6, 7)): ("S16", "Scaled throttle percent", "-32768 to 32767", ""),
    (1158, (0, 1)): ("S16", "Motor voltage control: idLimit", "-32768 to 32767", ""),
    (1158, (2, 3)): ("S16", "Motor voltage control: Idfiltered", "-32768 to 32767", "Arms"),
    (1158, (4, 5)): ("S16", "Actual currents: iq", "-32768 to 32767", "Apk"),
    (1158, (6, 7)): ("S16", "Motor measurements: DC bus current", "-32768 to 32767", "Adc"),
}

actual_values = {
    # COB-ID, Bytes : (Data Type, Description, Value Range, Units)
    (390, (0, 1)): 0,
    (390, (2, 3)): 0,
    (390, (4, 5)): 0,
    (390, (6, 7)): 0,
    (646, (0, 1)): 0,
    (646, (2, 3)): 0,
    (646, (4, 5)): 0,
    (646, (6, 7)): 0,
    (902, 0): 0,
    (902, 1): 0,
    (902, (2, 3)): 0,
    (902, (4, 5)): 0,
    (902, (6, 7)): 0,
    (1158, (0, 1)): 0,
    (1158, (2, 3)): 0,
    (1158, (4, 5)): 0,
    (1158, (6, 7)): 0,
}
pdo_map = {
    390: "PDO1",
    646: "PDO2",
    390: "PDO3",
    646: "PDO4",
}

root = tk.Tk()
root.title("CAN Bus Monitoring")
root.geometry('1600x1000')
root.resizable(False, False)

can_display = CANVariableDisplay(root)
speedometer = Speedometer(root)
currentmeter = CurrentMeter(root)
graph = Graph(root)
voltagegraph = VoltageGraph(root)


def update_values():
    # Process all messages currently in the queue
    while not can_queue.empty():
        msg_data = can_queue.get()
        can_display.update_display(msg_data)  # Update CANVariableDisplay
        data_values = msg_data.get('data_values', {})

        speed = data_values.get('Actual speed', (0,))[0]
        current = data_values.get('RMS motor Current', (0,))[0]
        torque = data_values.get('Actual Torque', (0,))[0]
        voltage = data_values.get('DC Bus Voltage', (0,))[0]

        # Update the UI components
        speedometer.update_dial(speed)
        currentmeter.update_dial(current)
        graph.update_graph(torque)
        voltagegraph.update_graph(voltage)

    root.after(100, update_values)


def create_ui():
    root.title("CAN Variable Display")

    # Create the table headers
    headers = ["COB-ID", "Bytes", "Data Type", "Description",
               "Value Range", "Units", "Actual Value"]
    for i, header in enumerate(headers):
        tk.Label(root, text=header, font=(
            'Helvetica', 10, 'bold')).grid(row=0, column=i)

    # Fill the grid with the variables and placeholders for actual values
    for row_index, ((cob_id, bytes_), (data_type, desc, value_range, units)) in enumerate(value_range_map.items(), start=1):
        tk.Label(root, text=str(cob_id)).grid(row=row_index, column=0)
        tk.Label(root, text=str(bytes_)).grid(row=row_index, column=1)
        tk.Label(root, text=data_type).grid(row=row_index, column=2)
        tk.Label(root, text=desc).grid(row=row_index, column=3)
        tk.Label(root, text=value_range).grid(row=row_index, column=4)
        tk.Label(root, text=units).grid(row=row_index, column=5)
        value_label = tk.Label(root, text=str(actual_values[(cob_id, bytes_)]))
        value_label.grid(row=row_index, column=6)

    # To handle window 'X' button click
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.bind('<q>', lambda event: on_closing())
    update_values()


def decode_data(msg_id, data_bytes):
    # print(f"Decoding data for msg_id: {msg_id} with data_bytes: {data_bytes}")
    data_values = {}

    for key, (data_type, description, value_range, units) in value_range_map.items():
        cob_id, byte_indices = key

        # Check if the msg_id matches the cob_id. If not, skip this iteration
        if msg_id != cob_id:
            continue

        if isinstance(byte_indices, tuple):
            start, end = key[1]
            # print(f"For msg_id {msg_id}, data_bytes length: {len(data_bytes)}")
            if end is None and start >= len(data_bytes):
                # print("Index out of range for single-byte key:", key)
                continue
            elif end is not None and (start >= len(data_bytes) or end >= len(data_bytes)):
                # print("Index out of range for multi-byte key:", key)
                continue
        else:
            start = key[1]
            if start >= len(data_bytes):
                continue  # Skip this iteration if index is out of range
            end = start  # Use start index as end index for single-byte data

        if data_type == "U16":
            value = (data_bytes[start] << 8) + data_bytes[end]
            # print("value U16: ", value)

        elif data_type == "S16":
            value = struct.unpack('>h', bytes(data_bytes[start:end+1]))[0]
            # print("value S16: ", value)

        elif data_type == "U8":
            value = data_bytes[start]
            # print("value U8: ", value)

        elif data_type == "0-15":
            value = data_bytes[start] & 0x0F
            # print("value 0-15: ", value)

        else:
            value = "Unsupported data type"
            # print("unsupported: ", value)

        data_values[description] = (value, value_range, units)
        # print("data values: ", data_values)

    return data_values


def format_can_message(msg):
    pdo_label = pdo_map.get(msg.id, "Unknown PDO")
    data_values = decode_data(msg.id, msg.data)

    return {
        'pdo_label': pdo_label,
        'data_values': data_values,
        'dlc': msg.dlc,
        'flags': msg.flags,
        'timestamp': msg.timestamp,
    }


def read_can_messages(trial_number, can_queue):
    # Initialize and open the channel
    global running
    channel = 0
    in_memory_data = []  # Step 1: Initialize in-memory data storage

    with canlib.openChannel(channel, canlib.canOPEN_ACCEPT_VIRTUAL) as ch:
        ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
        ch.setBusParams(canlib.canBITRATE_100K)
        ch.busOn()
        while running:
            try:
                msg = ch.read()
                pdo_label = pdo_map.get(msg.id, "Unknown_PDO")
                msg_data = format_can_message(msg)

                can_queue.put(msg_data)

                in_memory_data.append(msg)

            except canlib.CanNoMsg:

                pass  # No new message yet
            except KeyboardInterrupt:
                break  # Exit the loop on Ctrl+C
        ch.busOff()

    store_frames_to_database(in_memory_data)

    # Function to create the UI layout for the variable display


def on_closing():
    global running
    """ Handle the window closing event. """
    running = False
    root.destroy()


def check_for_exit():
    global running
    """ Check for a flag to exit the application. """
    if not running:
        if can_thread.is_alive():
            can_thread.join()  # Ensure the thread has finished
        root.destroy()
    else:
        root.after(100, check_for_exit)


def signal_handler(sig, frame):
    global running
    print('You pressed Ctrl+C!')
    running = False
    root.after(1, check_for_exit)


def is_device_connected(channel):
    try:
        with canlib.openChannel(channel, canlib.canOPEN_ACCEPT_VIRTUAL) as ch:
            status = ch.getBusParams()
            return status is not None
    except CanlibException:
        return False


def database_thread_function(db_queue, trial_number):
    conn = sqlite3.connect(FRAMES_DATABASE)
    while True:
        try:
            msg_data = db_queue.get(block=True, timeout=1)
            if msg_data is None:
                break
            store_to_db(msg_data['pdo_label'], trial_number, msg_data, conn)
        except queue.Empty:
            continue


def signal_handler(sig, frame):
    global running
    print('Exiting, signal received:', sig)
    running = False


if __name__ == "__main__":
    print("starting new session")

    conn = sqlite3.connect(FRAMES_DATABASE)
    try:
        create_tables(conn)
    except Exception as e:
        print(f"Error setting up database tables: {e}")

    signal.signal(signal.SIGINT, signal_handler)
    trial_num = get_next_trial_number(conn)

    print(f"Running telemetry display for trial number: {trial_num + 1}")

    db_thread = threading.Thread(
        target=database_thread_function, args=(db_queue, trial_num))
    db_thread.start()

    can_thread = threading.Thread(
        target=read_can_messages, args=(trial_num, can_queue))
    can_thread.daemon = True
    can_thread.start()

    create_ui()
    root.after(100, check_for_exit)
    root.mainloop()

    running = False
    db_queue.put(None)
    db_thread.join()
    if can_thread.is_alive():
        can_thread.join()
    print(f"Finished telemetry display for trial number: {trial_num + 1}")
