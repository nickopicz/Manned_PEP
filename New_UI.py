import tkinter as tk
from tkinter import ttk
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime


class CANVariableDisplay:
    def __init__(self, master):
        self.labels = {}
        self.descriptors = [
            'Actual speed', 'RMS motor Current', 'DC Bus Voltage',
            'Actual Torque', 'Motor measurements: DC bus current'
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
                             sticky='e', padx=10)
            self.labels[desc] = value_label

    def update_display(self, frame_data):
        # Extract the nested 'data_values' dictionary, if it exists
        data_values = frame_data.get('data_values', {})

        # Now iterate over the items in the data_values dictionary
        for desc, value_tuple in data_values.items():
            # Extract the first element of the tuple, which is the actual value
            value = value_tuple[0]
            if desc == 'Actual currents: iq':
                value = abs(value)
            if desc in self.labels:
                self.labels[desc].config(text=f"{value}")
            else:
                continue
                # print(f"Label for {desc} not found in UI")


class ThrottleGauge:
    def __init__(self, master):
        # Existing initialization code
        self.master = master
        self.canvas = tk.Canvas(master, width=100, height=300)
        self.canvas.grid(row=4, column=8, padx=20, pady=10)
        self.min_real_value = 170  # Minimum real throttle value
        self.max_real_value = 2810  # Maximum real throttle value
        self.gauge_height = 250
        self.gauge_width = 50
        self.gauge_x = 25
        self.gauge_y = 25
        self.current_value = 0  # This will now store the real value, not the percentage
        self.draw_gauge_background()
        self.value_label = tk.Label(master, text="0", font=('Helvetica', 10))
        self.value_label.grid(row=4, column=8)
        # Draw the initial oval
        # self.temp_oval = self.canvas.create_oval(
        #     5, 5, 5, 5, fill="blue", outline="black")

    def draw_gauge_background(self):
        # Draw the outer rectangle
        self.canvas.create_rectangle(self.gauge_x, self.gauge_y, self.gauge_x +
                                     self.gauge_width, self.gauge_y + self.gauge_height, outline="black")

    def update_gauge(self, real_value):
        # Ensure value is within the real bounds
        self.current_value = max(self.min_real_value, min(
            self.max_real_value, real_value))
        # Convert the real value to a percentage of the gauge scale
        percentage = ((self.current_value - self.min_real_value) /
                      (self.max_real_value - self.min_real_value)) * 100
        # Update the label with the real value
        self.value_label.config(
            text=f"{round(((self.current_value-165)/2800)*100)} %")
        # Calculate the oval's new vertical position based on the percentage
        oval_bottom_y = self.gauge_y + self.gauge_height - \
            ((percentage / 100) * self.gauge_height)
        oval_top_y = oval_bottom_y - self.gauge_width
# Move the oval to the new position
        # Move the oval to the new position
        # self.canvas.coords(self.temp_oval, self.gauge_x, oval_top_y,
        #                    self.gauge_x + self.gauge_width, oval_bottom_y)
        # Ensure the fill rectangle and oval are redrawn to reflect the new value
        self.canvas.delete("fill")
        self.canvas.create_rectangle(self.gauge_x + 1, self.gauge_y + self.gauge_height,
                                     self.gauge_x + self.gauge_width - 1, oval_bottom_y, fill="green", tags="fill")


class CurrentMeter:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=300, height=300)
        self.canvas.grid(row=0, column=6, rowspan=2, padx=20)
        self.center_x, self.center_y = 150, 150
        self.max_value = 500
        self.needle = self.create_current_dial()
        self.label = tk.Label(master, text="DC Current Supply (Amps)",
                              font=('Helvetica', 12))
        self.label.grid(row=0, column=6)
        self.value_label = tk.Label(
            master, text="0", font=('Helvetica', 10))
        self.value_label.grid(row=2, column=6)

    def create_current_dial(self):
        radius = 90
        self.canvas.create_arc(
            self.center_x - radius, self.center_y - radius,
            self.center_x + radius, self.center_y + radius,
            start=-30, extent=240, outline="black", style=tk.ARC
        )
        major_ticks = 10
        for i in range(major_ticks + 1):
            angle = math.radians(150 + (240 * i / major_ticks))
            start_x = self.center_x + (80 * math.cos(angle))
            start_y = self.center_y + (80 * math.sin(angle))
            end_x = self.center_x + (90 * math.cos(angle))
            end_y = self.center_y + (90 * math.sin(angle))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="black")

            label_angle = math.radians(150 + (240 * i / major_ticks))
            label_x = self.center_x + (70 * math.cos(label_angle))
            label_y = self.center_y + (70 * math.sin(label_angle))
            label_value = int((self.max_value / major_ticks) * i)
            self.canvas.create_text(label_x, label_y, text=str(label_value))

        angle = math.radians(150)  # Initial angle pointing at 0
        x1, y1 = self.center_x + 80 * \
            math.cos(angle), self.center_y + 80 * math.sin(angle)
        return self.canvas.create_line(self.center_x, self.center_y, x1, y1, fill="red", width=2)

    def update_dial(self, current):
        self.canvas.delete(self.needle)
        angle = math.radians(150 + (240 * current / self.max_value))
        x1, y1 = self.center_x + 80 * \
            math.cos(angle), self.center_y + 80 * math.sin(angle)
        self.value_label.config(text=f"{current}")

        self.needle = self.canvas.create_line(
            self.center_x, self.center_y, x1, y1, fill="red", width=2)


class Speedometer:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=300, height=300)
        self.canvas.grid(row=0, column=3, rowspan=2, padx=20)
        self.center_x, self.center_y = 150, 150
        self.max_value = 3500
        self.needle = self.create_speedometer_dial()
        self.label = tk.Label(master, text="RPM",
                              font=('Helvetica', 12))
        self.label.grid(row=0, column=3)
        self.value_label = tk.Label(
            master, text="0 rpm", font=('Helvetica', 10))
        self.value_label.grid(row=2, column=3)

    def create_speedometer_dial(self):
        radius = 90
        self.canvas.create_arc(
            self.center_x - radius, self.center_y - radius,
            self.center_x + radius, self.center_y + radius,
            start=-30, extent=240, outline="black", style=tk.ARC
        )
        major_ticks = 10
        for i in range(major_ticks + 1):
            angle = math.radians(150 + (240 * i / major_ticks))
            start_x = self.center_x + (80 * math.cos(angle))
            start_y = self.center_y + (80 * math.sin(angle))
            end_x = self.center_x + (90 * math.cos(angle))
            end_y = self.center_y + (90 * math.sin(angle))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="black")

            label_angle = math.radians(150 + (240 * i / major_ticks))
            label_x = self.center_x + (70 * math.cos(label_angle))
            label_y = self.center_y + (70 * math.sin(label_angle))
            label_value = int((self.max_value / major_ticks) * i)
            self.canvas.create_text(label_x, label_y, text=str(label_value))

        angle = math.radians(150)  # Initial angle pointing at 0
        x1, y1 = self.center_x + 80 * \
            math.cos(angle), self.center_y + 80 * math.sin(angle)
        return self.canvas.create_line(self.center_x, self.center_y, x1, y1, fill="red", width=2)

    def update_dial(self, speed):
        self.canvas.delete(self.needle)
        angle = math.radians(150 + (240 * speed / self.max_value))
        x1, y1 = self.center_x + 80 * \
            math.cos(angle), self.center_y + 80 * math.sin(angle)
        self.value_label.config(text=f"{speed}")

        self.needle = self.canvas.create_line(
            self.center_x, self.center_y, x1, y1, fill="red", width=2)


class Graph:
    def __init__(self, master):
        self.fig, self.ax = plt.subplots(
            figsize=(5, 4))  # Adjust the figsize here
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        # Adjust the line below to use grid instead of pack
        # Adjust the row, column, and rowspan as needed
        self.canvas_widget.grid(row=3, column=3, rowspan=4, sticky="nsew")
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Actual Torque')
        self.ax.set_title('Time Series of Actual Torque')
        self.torque_data = {'time': [], 'value': []}

    def update_graph(self, new_data, timestamp):
        # current_time = datetime.datetime.now()
        self.torque_data['time'].append(timestamp)
        self.torque_data['value'].append(new_data)
        self.ax.clear()
        self.ax.plot(self.torque_data['time'], self.torque_data['value'])
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Actual Torque')
        self.canvas.draw()


class VoltageGraph:
    def __init__(self, master):
        self.fig, self.ax = plt.subplots(
            figsize=(5, 4))  # Adjust the figsize here
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        # Adjust the line below to use grid instead of pack
        # Adjust the row, column, and rowspan as needed
        self.canvas_widget.grid(row=3, column=6, rowspan=4, sticky="nsew")
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Motor Voltage')
        self.ax.set_title('Time Series of Motor Voltage')
        self.voltage_data = {'time': [], 'value': []}

    def update_graph(self, new_data, timestamp):
        current_time = datetime.datetime.now()
        self.voltage_data['time'].append(timestamp)
        self.voltage_data['value'].append(new_data)

        self.ax.clear()
        self.ax.plot(self.voltage_data['time'], self.voltage_data['value'])
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Motor Voltage')
        self.canvas.draw()


class ThermometerGauge:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=90, height=310)
        # Adjust grid placement as needed
        self.canvas.grid(row=1, column=8, padx=20, pady=5)
        self.value_label = tk.Label(
            master, text="0 °C", font=('Helvetica', 10))
        self.value_label.grid(row=2, column=8)
        self.min_temp = 0  # Minimum temperature value
        self.max_temp = 140  # Maximum temperature value
        self.gauge_height = 320
        self.gauge_width = 20
        self.gauge_x = 20
        self.gauge_y = 5
        self.draw_gauge_background()

    def draw_gauge_background(self):
        # Draw the outer rectangle

        self.canvas.create_rectangle(self.gauge_x, self.gauge_y,
                                     self.gauge_x + self.gauge_width, self.gauge_y + self.gauge_height,
                                     outline="black")

        # Draw ticks and labels
        # Adjust step for fewer or more ticks
        for temp in range(self.min_temp, self.max_temp + 1, 25):
            percentage = (temp - self.min_temp) / \
                (self.max_temp - self.min_temp)
            y = self.gauge_y + self.gauge_height - \
                (percentage * self.gauge_height)

            # Ticks
            self.canvas.create_line(
                self.gauge_x, y, self.gauge_x + 10, y, fill="black")
            self.canvas.create_line(self.gauge_x + self.gauge_width -
                                    10, y, self.gauge_x + self.gauge_width, y, fill="black")

            # Labels
            self.canvas.create_text(
                self.gauge_x + self.gauge_width + 10, y, text=f"{temp}°C", anchor="w")

    def update_gauge(self, current_temp):
        # Validate current temperature
        current_temp = max(self.min_temp, min(self.max_temp, current_temp))
        percentage = (current_temp - self.min_temp) / \
            (self.max_temp - self.min_temp)
        fill_height = percentage * self.gauge_height

        self.value_label.config(text=f"{current_temp} °C")
        # Clear previous fill
        self.canvas.delete("temp_fill")
        # Draw new fill
        if current_temp > 60:
            self.canvas.create_rectangle(self.gauge_x + 1, self.gauge_y + self.gauge_height - fill_height,
                                         self.gauge_x + self.gauge_width - 1, self.gauge_y + self.gauge_height,
                                         fill="red", tags="temp_fill")
        else:
            self.canvas.create_rectangle(self.gauge_x + 1, self.gauge_y + self.gauge_height - fill_height,
                                         self.gauge_x + self.gauge_width - 1, self.gauge_y + self.gauge_height,
                                         fill="green", tags="temp_fill")
