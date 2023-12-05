#!/usr/bin/env python3

import datetime
import sqlite3
from canlib import canlib, CanlibException
import time
import struct
import os

from database_functions import create_table_for_pdo, store_to_db
from Frames_database import get_next_trial_number, create_tables
import queue
import threading
import signal

from Frames_database import store_frames_to_database
# Mapping from COB-ID to PDO and its information

# FRAMES_DATABASE = "db/frames_data.db"
FRAMES_DATABASE = "/home/pi/Manned_PEP/db/frames_data.db"


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
        'id': msg.id,
        'data': data_values,
        'dlc': msg.dlc,
        'flags': msg.flags,
        'timestamp': msg.timestamp,
    }


def is_device_connected(channel):
    try:
        with canlib.openChannel(channel, canlib.canOPEN_ACCEPT_VIRTUAL) as ch:
            status = ch.getBusParams()
            return status is not None
    except CanlibException:
        return False


def read_can_messages(trial_number, can_queue):
    # Initialize and open the channel
    global running
    channel = 0

    # Wait for the CAN device to be connected
    device_connected = False
    timeout = time.time() + 60  # 1 minute from now
    while not device_connected and time.time() < timeout:
        device_connected = is_device_connected(channel)
        if not device_connected:
            print("Waiting for CAN device to be connected...")
            time.sleep(5)  # Wait for 5 seconds before checking again

    if not device_connected:
        print("CAN device not detected, exiting.")
        running = False
        return

    # Now that the device is connected, proceed with the rest of the function
    with canlib.openChannel(channel, canlib.canOPEN_ACCEPT_VIRTUAL) as ch:
        ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
        ch.setBusParams(canlib.canBITRATE_500K)
        ch.busOn()
        while running:
            try:
                msg = ch.read()
                pdo_label = pdo_map.get(msg.id, "Unknown_PDO")
                msg_data = format_can_message(msg)
<<<<<<< HEAD

                can_queue.put(msg_data)

=======
                can_queue.put(msg)
>>>>>>> 0d521dbf01713974ac3dfcd478d5860c6fd1a8d9

            except canlib.CanNoMsg:

                pass  # No new message yet
            except KeyboardInterrupt:
                break  # Exit the loop on Ctrl+C
        ch.busOff()


    # Function to create the UI layout for the variable display


def signal_handler(sig, frame):
    global running
    print('Exiting, signal received:', sig)
    running = False


def database_thread_function(db_queue, trial_number):
    while True:
        try:
            # Adjust timeout as needed
            msg_data = db_queue.get(block=True, timeout=1)
            if msg_data is None:
                # Break the loop if a sentinel value (like None) is received
                break
            print(f"msg_data: {msg_data}")
            try:
                store_to_db(trial_number, msg_data)
            except:
                print("error in sending do db: ")
        except queue.Empty:
            continue  # No message received, loop back and wait again


if __name__ == "__main__":
    print("starting new session")

    conn = sqlite3.connect(FRAMES_DATABASE)
    signal.signal(signal.SIGINT, signal_handler)
    trial_num = 0
    try:
        trial_num = get_next_trial_number(conn)
    except Exception as e:
        print(f"Error getting next trial number: {e}")
        trial_num = 0
        create_tables(conn)

    print(f"Running telemetry display for trial number: {trial_num}")

    db_queue = queue.Queue()
    db_thread = threading.Thread(target=database_thread_function,
                       args=(db_queue, trial_num))
    db_thread.start()
    # Set up the queue and start the CAN reading thread
    can_queue = queue.Queue()
    can_thread = threading.Thread(
        target=read_can_messages, args=(trial_num, can_queue))
    can_thread.daemon = True
    can_thread.start()

    # Loop to keep the script running and handle CAN messages
    try:
        while running:
            try:
                msg_data = can_queue.get(timeout=1)  # Adjust timeout as needed
                db_queue.put(msg_data)
                # You can process the formatted data here
                # For example, log it to a file or print to console
            except queue.Empty:
                continue  # No message received, loop back and wait again
    except KeyboardInterrupt:
        print("Interrupted by user, stopping.")
    finally:
        running = False
        db_queue.put(None)
        db_thread.join()
        if can_thread.is_alive():
            can_thread.join()
        print(f"Finished telemetry display for trial number: {trial_num}")
