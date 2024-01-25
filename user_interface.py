import tkinter as tk
from collections import namedtuple
from tkinter import ttk  # Make sure to import ttk
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from check_ch import format_can_message

labels = {}
past_rpm_values = []


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


def create_ui(root):
    global labels, speedometer_needle, speedometer
    root.title("CAN Variable Display")

    # Set a constant window size
    root.geometry('1600x800')  # Set the window to 800x600 pixels
    root.resizable(False, False)  # Prevent resizing

    # Define your column headers
    headers = ['Description', 'Value']
    for index, header in enumerate(headers):
        label = tk.Label(root, text=header, font=('Helvetica', 10, 'bold'))
        label.grid(row=0, column=index, sticky='ew', padx=10, pady=10)

    # Configure the grid columns to distribute space evenly
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    speedometer = tk.Canvas(root, width=300, height=300)
    speedometer.grid(row=1, column=2, rowspan=4, padx=20, pady=20)
    graph_frame = tk.Frame(root)
    graph_frame.grid(row=0, column=3, rowspan=10, padx=10, pady=10)
    ax, canvas = create_graph(graph_frame)
    # Define your descriptors (or get them from your data source)
    speedometer_needle = create_speedometer_dial(
        speedometer, 150, 150, 3500, label="RPM")
    # speedometer_needle = create_speedometer_dial(
    #     speedometer, 350, 350, 3500, label="Speed")

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

    return root, ax, canvas


def create_graph(canvas_frame):
    # Create a figure and an axis for the plot
    fig, ax = plt.subplots()

    # Initialize a list to store data points
    global torque_data
    torque_data = {'time': [], 'value': []}

    # Basic plot setup
    ax.set_xlabel('Time')
    ax.set_ylabel('Actual Torque')
    ax.set_title('Time Series of Actual Torque')

    # Creating a Tkinter canvas containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

    return ax, canvas


def update_ui(frame_data, ax, canvas):
    global past_rpm_values, torque_data

    for desc, (value, _, _) in frame_data['data_values'].items():
        if desc == "Actual speed":
            value = abs(value)/10

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
            update_speedometer_dial(
                speedometer, speedometer_needle, 150, 150, avg_rpm, 3500)

        if desc == "Actual Torque":
            value = abs(value)/1000

            # Append new data to the torque_data list
            current_time = datetime.datetime.now()
            torque_data['time'].append(current_time)
            torque_data['value'].append(value)

            # Update the graph
            ax.clear()
            ax.plot(torque_data['time'], torque_data['value'])
            ax.set_xlabel('Time')
            ax.set_ylabel('Actual Torque')
            ax.set_title('Time Series of Actual Torque')

            # Redraw the canvas
            canvas.draw()

        elif desc == "Scaled throttle percent":
            value = value / 32767

        if desc in labels:
            labels[desc].config(text=f"{desc}: {value}")


def create_speedometer_dial(canvas, center_x, center_y, max_value, label=""):
    # Draw the arc for the speedometer
    radius = 90
    canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius,
                      start=-30, extent=240, outline="black", style=tk.ARC)

    # Number of major tick intervals
    major_ticks = 10

    # Draw major ticks and labels
    for i in range(major_ticks + 1):
        angle = math.radians(-30 + (240 * i / major_ticks))
        start_x = center_x + (80 * math.cos(angle))
        start_y = center_y + (80 * math.sin(angle))
        end_x = center_x + (90 * math.cos(angle))
        end_y = center_y + (90 * math.sin(angle))

        canvas.create_line(start_x, start_y, end_x, end_y, fill="black")

        label_angle = math.radians(-30 + (240 * i / major_ticks))
        label_x = center_x + (70 * math.cos(label_angle))
        label_y = center_y + (70 * math.sin(label_angle))
        label_value = int((max_value / major_ticks) * i)

        canvas.create_text(label_x, label_y, text=str(label_value))

    if label:
        # Draw label on top of the meter
        canvas.create_text(center_x, center_y - radius - 20,
                           text=label, font=("Helvetica", 14, "bold"))

    # Initial needle (pointing at 0)
    angle = math.radians(-30)  # Initial angle pointing at 0
    x1, y1 = center_x + 80 * math.cos(angle), center_y + 80 * math.sin(angle)
    needle = canvas.create_line(
        center_x, center_y, x1, y1, fill="red", width=2, tags="needle")

    return needle

# Function to update a speedometer dial


def update_speedometer_dial(canvas, needle, center_x, center_y, speed, max_value):
    canvas.delete(speedometer_needle)

    # Calculate needle position
    angle = math.radians(-30 + (240 * speed / max_value))
    x1, y1 = center_x + 80 * math.cos(angle), center_y + 80 * math.sin(angle)

    # Draw new needle
    needle = canvas.create_line(
        center_x, center_y, x1, y1, fill="red", width=2, tags="needle")
