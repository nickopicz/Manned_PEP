import sqlite3
import time
import struct
from canlib import Frame
import os
from check_ch import format_can_message
import tkinter as tk
from collections import namedtuple
from tkinter import ttk  # Make sure to import ttk
import math

# Adjust these constants according to your setup
DATABASE_NAME = "db/can_data.db"
FRAME_DATABASE = "./db/frames_data.db"

frametype = namedtuple(
    'Frame', ['id', 'data', 'dlc', 'flags', 'timestamp'])

# Dictionary to hold the labels for each descriptor
labels = {}

# List to store past RPM values for the moving average filter
past_rpm_values = []


def create_ui(root):
    global labels, speedometer
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
    speedometer = tk.Canvas(root, width=200, height=200)
    speedometer.grid(row=1, column=2, rowspan=4, padx=20, pady=20)

    draw_speedometer_dial(speedometer)
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


def update_speedometer(canvas, speed):
    global rpm_value_label

    canvas.delete("needle")  # Remove the old needle

    # Calculate needle position
    angle = math.radians(-30 + (240 * speed / 35000))
    x0, y0 = 100, 100  # Center of the speedometer
    x1, y1 = x0 + 80 * math.cos(angle), y0 + 80 * math.sin(angle)

    # Draw new needle
    canvas.create_line(x0, y0, x1, y1, fill="red", width=2, tags="needle")

    # Update the RPM value label
    canvas.itemconfigure(rpm_value_label, text=str(int(speed)))


def update_ui(frame_data):
    global past_rpm_values

    for desc, (value, _, _) in frame_data['data_values'].items():
        if desc == "Actual speed":
            value = abs(value)

            # Append the new value to the list of past values
            past_rpm_values.append(value)
            # Define the size of the moving window for the moving average
            window_size = 5

            # Ensure the list size doesn't exceed the window size
            if len(past_rpm_values) > window_size:
                past_rpm_values.pop(0)

            # Calculate the moving average
            avg_rpm = sum(past_rpm_values) / len(past_rpm_values)

            # Update the speedometer with the moving average
            update_speedometer(speedometer, avg_rpm)

        elif desc == "Scaled throttle percent":
            value = value / 32767

        if desc in labels:
            labels[desc].config(text=f"{desc}: {value}")


def draw_speedometer_dial(canvas):
    global rpm_value_label  # Global variable to update RPM value label

    # Draw the arc for the speedometer
    canvas.create_arc(10, 10, 190, 190, start=-30,
                      extent=359, outline="black", style=tk.ARC)

    # Center of the speedometer
    center_x, center_y = 100, 100

    # RPM meter settings (adjust as needed)
    max_rpm = 35000  # Maximum RPM value on your meter
    major_ticks = 10  # Number of major tick intervals

    # Draw major ticks and labels
    for i in range(major_ticks + 1):
        # Angle for each tick
        angle = math.radians(-30 + (240 * i / major_ticks))

        # Start and end points for tick lines
        start_x = center_x + (80 * math.cos(angle))
        start_y = center_y + (80 * math.sin(angle))
        end_x = center_x + (90 * math.cos(angle))
        end_y = center_y + (90 * math.sin(angle))

        # Draw tick lines
        canvas.create_line(start_x, start_y, end_x, end_y, fill="black")

        # Label positions and values
        label_angle = math.radians(-30 + (240 * i / major_ticks))
        label_x = center_x + (70 * math.cos(label_angle))
        label_y = center_y + (70 * math.sin(label_angle))
        label_value = int((max_rpm / major_ticks) * i)

        # Draw labels
        canvas.create_text(label_x, label_y, text=str(label_value))

    # Draw RPM label on top of the meter
    canvas.create_text(center_x, 20, text="RPM",
                       font=("Helvetica", 14, "bold"))

    # Draw the RPM value label below the meter
    rpm_value_label = canvas.create_text(
        center_x, 200, text="0", font=("Helvetica", 12))

    # Initial needle position (pointing at 0)
    update_speedometer(canvas, 0)


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
