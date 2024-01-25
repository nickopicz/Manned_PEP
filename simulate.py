import sqlite3
import time
import struct
from canlib import Frame
import threading
import os
from check_ch import format_can_message
import tkinter as tk
from collections import namedtuple
from tkinter import ttk  # Make sure to import ttk
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
# Adjust these constants according to your setup
DATABASE_NAME = "db/can_data.db"
FRAME_DATABASE = "./db/frames_data.db"

frametype = namedtuple(
    'Frame', ['id', 'data', 'dlc', 'flags', 'timestamp'])


def fetch_next_frame(simulator, root, ax, canvas):
    try:
        frame = next(simulator)
        formatted_msg = format_can_message(frame)
        update_ui(formatted_msg, ax, canvas)
        root.after(10, fetch_next_frame, simulator, root,
                   ax, canvas)  # Schedule the next update
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


def sim_frames(root, ax, canvas):
    trial_number = 17  # Update this to the correct trial number from your database
    simulator = simulate_live_feed(trial_number=trial_number, delay=0.01)
    fetch_next_frame(simulator, root, ax, canvas)


if __name__ == "__main__":
    print("====================== \n \n simulation starting \n \n======================")
    root = tk.Tk()
    ui, ax, canvas = create_ui(root)
    sim_frames(root, ax, canvas)
    root.mainloop()
