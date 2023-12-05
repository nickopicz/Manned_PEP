import sqlite3
import time
import struct
from canlib import Frame
import os
from check_ch import format_can_message
import tkinter as tk
from collections import namedtuple
from tkinter import ttk  # Make sure to import ttk

# Adjust these constants according to your setup
DATABASE_NAME = "db/can_data.db"
FRAME_DATABASE = "./db/frames_data.db"

frametype = namedtuple(
    'Frame', ['id', 'data', 'dlc', 'flags', 'timestamp'])

# Dictionary to hold the labels for each descriptor
labels = {}


def create_ui(root):
    global labels
    root.title("CAN Variable Display")

    # Set a constant window size
    root.geometry('800x600')  # Set the window to 800x600 pixels
    root.resizable(False, False)  # Prevent resizing

    # Define your column headers
    headers = ['Description', 'Value']
    for index, header in enumerate(headers):
        label = tk.Label(root, text=header, font=('Helvetica', 10, 'bold'))
        label.grid(row=0, column=index, sticky='ew', padx=10, pady=10)

    # Configure the grid columns to distribute space evenly
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    # Define your descriptors (or get them from your data source)
    descriptors = ['Actual speed', 'RMS motor Current', 'DC Bus Voltage', 'Reference Torque', 'Actual Torque',
                   'Motor voltage control: idLimit', 'Internal Speed Reference', 'Scaled throttle percent', '']

    # Create rows for data and separators
    for row_index, desc in enumerate(descriptors, start=1):
        # Separator widget from the ttk module
        separator = ttk.Separator(root, orient='horizontal')
        separator.grid(row=row_index*2-1, columnspan=2, sticky='ew')

        # Description label
        desc_label = tk.Label(root, text=desc)
        desc_label.grid(row=row_index*2, column=0, sticky='w', padx=10, pady=5)

        # Value label, initially set to 'N/A'
        value_label = tk.Label(root, text="N/A", font=('Helvetica', 10))
        value_label.grid(row=row_index*2, column=1,
                         sticky='e', padx=10, pady=5)

        # Store the value labels in a dictionary for updating later
        labels[desc] = value_label

    return root


def update_ui(frame_data):
    for desc, (value, _, _) in frame_data['data_values'].items():
        if (desc == "Actual speed"):
            value = value/10
        if (desc == "Scaled throttle percent"):
            value = value/32767
        if desc in labels:
            labels[desc].config(text=f"{desc}: {value}")


def fetch_next_frame(simulator, root):
    try:
        frame = next(simulator)
        formatted_msg = format_can_message(frame)
        update_ui(formatted_msg)
        root.after(10, fetch_next_frame, simulator,
                   root)  # Schedule the next update
    except StopIteration:
        print("No more frames to display")
        # Optionally reset the simulator here if you want to loop the simulate


def simulate_live_feed(trial_number, delay=0.01):
    conn = sqlite3.connect(FRAME_DATABASE)
    cursor = conn.cursor()

    query = '''
        SELECT frame_id, data, dlc, flags, timestamp
        FROM frame_data
        WHERE trial_number = ?
        ORDER BY timestamp ASC
    '''
    cursor.execute(query, (trial_number,))
    all_rows = cursor.fetchall()
    print(f"Fetched {len(all_rows)} rows for trial number {trial_number}")
    for row in all_rows:
        frame = frametype._make(row)
        yield frame
        time.sleep(delay)


def sim_frames(root):
    trial_number = 17  # Update this to the correct trial number from your database32767
    simulator = simulate_live_feed(trial_number=trial_number, delay=0.01)
    fetch_next_frame(simulator, root)


if __name__ == "__main__":
    print("====================== \n \n simulation starting \n \n======================")
    root = tk.Tk()
    create_ui(root)
    sim_frames(root)
    root.mainloop()
