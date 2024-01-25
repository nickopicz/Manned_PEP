import tkinter as tk
from tkinter import ttk
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

# Assuming format_can_message is a function you have defined elsewhere
from check_ch import format_can_message


class CANVariableDisplay:
    def __init__(self, master):
        self.labels = {}
        self.descriptors = [
            'Actual speed', 'RMS motor Current', 'DC Bus Voltage',
            'Reference Torque', 'Actual Torque', 'Motor voltage control: idLimit',
            'Internal Speed Reference', 'Scaled throttle percent', ''
        ]
        self.create_labels(master)

    def create_labels(self, master):
        for row_index, desc in enumerate(self.descriptors, start=1):
            ttk.Separator(master, orient='horizontal').grid(
                row=row_index * 2 - 1, columnspan=2, sticky='ew')
            tk.Label(master, text=desc).grid(row=row_index *
                                             2, column=0, sticky='w', padx=10, pady=5)
            value_label = tk.Label(master, text="N/A", font=('Helvetica', 10))
            value_label.grid(row=row_index * 2, column=1,
                             sticky='e', padx=10, pady=5)
            self.labels[desc] = value_label

    def update_display(self, frame_data):
        # Extract the nested 'data_values' dictionary, if it exists
        data_values = frame_data.get('data_values', {})

        # Now iterate over the items in the data_values dictionary
        for desc, value_tuple in data_values.items():
            # Extract the first element of the tuple, which is the actual value
            value = value_tuple[0]
            if desc in self.labels:
                self.labels[desc].config(text=f"{value}")
            else:
                print(f"Label for {desc} not found in UI")


class Speedometer:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=300, height=300)
        self.canvas.grid(row=1, column=2, rowspan=4, padx=20, pady=20)
        self.center_x, self.center_y = 150, 150
        self.max_value = 3500
        self.needle = self.create_speedometer_dial()

    def create_speedometer_dial(self):
        radius = 90
        self.canvas.create_arc(
            self.center_x - radius, self.center_y - radius,
            self.center_x + radius, self.center_y + radius,
            start=-30, extent=240, outline="black", style=tk.ARC
        )
        major_ticks = 10
        for i in range(major_ticks + 1):
            angle = math.radians(-30 + (240 * i / major_ticks))
            start_x = self.center_x + (80 * math.cos(angle))
            start_y = self.center_y + (80 * math.sin(angle))
            end_x = self.center_x + (90 * math.cos(angle))
            end_y = self.center_y + (90 * math.sin(angle))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="black")

            label_angle = math.radians(-30 + (240 * i / major_ticks))
            label_x = self.center_x + (70 * math.cos(label_angle))
            label_y = self.center_y + (70 * math.sin(label_angle))
            label_value = int((self.max_value / major_ticks) * i)
            self.canvas.create_text(label_x, label_y, text=str(label_value))

        angle = math.radians(-30)  # Initial angle pointing at 0
        x1, y1 = self.center_x + 80 * \
            math.cos(angle), self.center_y + 80 * math.sin(angle)
        return self.canvas.create_line(self.center_x, self.center_y, x1, y1, fill="red", width=2)

    def update_dial(self, speed):
        self.canvas.delete(self.needle)
        angle = math.radians(-30 + (240 * speed / self.max_value))
        x1, y1 = self.center_x + 80 * \
            math.cos(angle), self.center_y + 80 * math.sin(angle)
        self.needle = self.canvas.create_line(
            self.center_x, self.center_y, x1, y1, fill="red", width=2)


class Graph:
    def __init__(self, master):
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        # Adjust the line below to use grid instead of pack
        # Adjust the row, column, and rowspan as needed
        self.canvas_widget.grid(row=0, column=3, rowspan=10, sticky="nsew")
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Actual Torque')
        self.ax.set_title('Time Series of Actual Torque')
        self.torque_data = {'time': [], 'value': []}

    def update_graph(self, new_data):
        current_time = datetime.datetime.now()
        self.torque_data['time'].append(current_time)
        self.torque_data['value'].append(new_data)
        self.ax.clear()
        self.ax.plot(self.torque_data['time'], self.torque_data['value'])
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Actual Torque')
        self.canvas.draw()


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack()
        self.master.title("CAN Variable Display")
        self.master.geometry('1600x800')
        self.master.resizable(False, False)

        self.can_display = CANVariableDisplay(self)
        self.speedometer = Speedometer(self)
        self.graph = Graph(self)

        # Add the simulator logic and update loop here
        # self.simulator = YourSimulator()  # Assuming you have a simulator class
        # self.update_ui()

    def update_ui(self):
        try:
            frame_data = next(self.simulator)  # Get data from your simulator
            formatted_msg = format_can_message(frame_data)

            # Update components
            self.can_display.update_display(formatted_msg)
            speed = formatted_msg.get('Actual speed', 0)
            self.speedometer.update_dial(speed)
            torque = formatted_msg.get('Actual Torque', 0)
            self.graph.update_graph(torque)

            # Schedule next update
            self.master.after(10, self.update_ui)
        except StopIteration:
            print("No more frames to display")
            # Handle end of data stream
