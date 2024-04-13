import tkinter as tk
from tkinter import ttk
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.figure import Figure


class ThrottleGauge:
    def __init__(self, master):
        # Existing initialization code
        self.master = master
        self.canvas = tk.Canvas(master, width=50, height=300)
        self.canvas.grid(row=1, column=4, rowspan=2)
        self.min_real_value = 170  # Minimum real throttle value
        self.max_real_value = 2810  # Maximum real throttle value
        self.gauge_height = 250
        self.gauge_width = 20
        self.gauge_x = 25
        self.gauge_y = 25
        self.current_value = 0  # This will now store the real value, not the percentage
        self.draw_gauge_background()
        self.canvas.configure(background='lightblue')
        self.value_label = tk.Label(master, text="0 %", font=('Helvetica', 10))
        self.value_label.grid(row=2, column=4)
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
        # self.canvas.coords(self.temp_oval, self.gauge_x, oval_top_y,
        #                    self.gauge_x + self.gauge_width, oval_bottom_y)
        # Ensure the fill rectangle and oval are redrawn to reflect the new value
        self.canvas.delete("fill")
        self.canvas.create_rectangle(self.gauge_x + 1, self.gauge_y + self.gauge_height,
                                     self.gauge_x + self.gauge_width - 1, oval_bottom_y, fill="yellow", tags="fill")


class CurrentMeter:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=300, height=300)
        self.canvas.grid(row=0, column=2, rowspan=2)
        self.center_x, self.center_y = 150, 150
        self.max_value = 500
        self.needle = self.create_current_dial()
        self.label = tk.Label(master, text="Motor Current (Amps)",
                              font=('Helvetica', 12))
        self.label.grid(row=0, column=2)
        self.canvas.configure(background='lightblue')

        self.value_label = tk.Label(
            master, text=f"{str(0)} amps", font=('Helvetica', 10))
        self.value_label.grid(row=1, column=2)

    def create_current_dial(self):
        radius = 140
        self.canvas.create_arc(
            self.center_x - radius, self.center_y - radius,
            self.center_x + radius, self.center_y + radius,
            start=-30, extent=240, outline="black", style=tk.ARC
        )
        major_ticks = 10
        for i in range(major_ticks + 1):
            angle = math.radians(150 + (240 * i / major_ticks))
            start_x = self.center_x + (125 * math.cos(angle))
            start_y = self.center_y + (125 * math.sin(angle))
            end_x = self.center_x + (140 * math.cos(angle))
            end_y = self.center_y + (140 * math.sin(angle))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="black")

            label_angle = math.radians(150 + (240 * i / major_ticks))
            label_x = self.center_x + (110 * math.cos(label_angle))
            label_y = self.center_y + (110 * math.sin(label_angle))
            label_value = int((self.max_value / major_ticks) * i)
            self.canvas.create_text(
                label_x, label_y, text=str(label_value))

        angle = math.radians(150)  # Initial angle pointing at 0
        x1, y1 = self.center_x + 80 * \
            math.cos(angle), self.center_y + 80 * math.sin(angle)
        return self.canvas.create_line(self.center_x, self.center_y, x1, y1, fill="red", width=2)

    def update_dial(self, current):
        self.canvas.delete(self.needle)
        angle = math.radians(150 + (240 * current / self.max_value))
        x1, y1 = self.center_x + 80 * \
            math.cos(angle), self.center_y + 80 * math.sin(angle)
        self.value_label.config(text=f"{str(current)} amps")

        self.needle = self.canvas.create_line(
            self.center_x, self.center_y, x1, y1, fill="red", width=2)


class Speedometer:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=300, height=300)
        self.canvas.grid(row=0, column=1, rowspan=2)
        self.center_x, self.center_y = 150, 150
        self.max_value = 3500
        self.needle = self.create_speedometer_dial()
        self.label = tk.Label(master, text="RPM",
                              font=('Helvetica', 12))
        self.canvas.configure(background='lightblue')
        self.label.grid(row=0, column=1)
        self.value_label = tk.Label(
            master, text="0 rpm", font=('Helvetica', 10))
        self.value_label.grid(row=1, column=1)

    def create_speedometer_dial(self):
        radius = 140
        self.canvas.create_arc(
            self.center_x - radius, self.center_y - radius,
            self.center_x + radius, self.center_y + radius,
            start=-30, extent=240, outline="black", style=tk.ARC
        )
        major_ticks = 10
        for i in range(major_ticks + 1):
            angle = math.radians(150 + (240 * i / major_ticks))
            start_x = self.center_x + (125 * math.cos(angle))
            start_y = self.center_y + (125 * math.sin(angle))
            end_x = self.center_x + (140 * math.cos(angle))
            end_y = self.center_y + (140 * math.sin(angle))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="black")

            label_angle = math.radians(150 + (240 * i / major_ticks))
            label_x = self.center_x + (110 * math.cos(label_angle))
            label_y = self.center_y + (110 * math.sin(label_angle))
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
        # self.value_label.config(text=f"{speed}")

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
        self.canvas_widget.grid(row=2, column=2, sticky="nsew")
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Actual Torque')
        self.ax.set_title('Time Series of Torque (lb ft)')
        self.torque_data = {'time': [], 'value': []}
        # self.canvas.configure(background='lightblue')

    def update_graph(self, new_data, timestamp):
        if len(self.torque_data['time']) > 100:
            self.torque_data['time'].pop(0)
            self.torque_data['value'].pop(0)
        # current_time = datetime.datetime.now()
        self.torque_data['time'].append(timestamp*0.001)
        self.torque_data['value'].append(new_data)
        self.ax.clear()
        self.ax.plot(self.torque_data['time'], self.torque_data['value'])
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Torque')
        self.canvas.draw()


class VoltageGraph:
    def __init__(self, master):
        self.fig, self.ax = plt.subplots(
            figsize=(5, 4))  # Adjust the figsize here
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        # Adjust the line below to use grid instead of pack
        # Adjust the row, column, and rowspan as needed
        self.canvas_widget.grid(row=2, column=1, sticky="nsew")
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Motor Current')
        self.ax.set_title('Time Series of Motor Current (amps)')
        self.voltage_data = {'time': [], 'value': []}
        # self.canvas.configure(background='lightblue')

    def update_graph(self, new_data, timestamp):
        if len(self.voltage_data['time']) > 100:
            self.voltage_data['time'].pop(0)
            self.voltage_data['value'].pop(0)

        current_time = datetime.datetime.now()
        self.voltage_data['time'].append(timestamp*0.001)
        self.voltage_data['value'].append(new_data)

        self.ax.clear()
        self.ax.plot(self.voltage_data['time'], self.voltage_data['value'])
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Motor Current')
        self.canvas.draw()


class ThermometerGauge:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=90, height=350)
        # Adjust grid placement as needed
        self.canvas.grid(row=1, column=3, rowspan=2)
        self.value_label = tk.Label(
            master, text="0 °C", font=('Helvetica', 10))
        self.value_label.grid(row=2, column=3)
        self.min_temp = 0  # Minimum temperature value
        self.max_temp = 140  # Maximum temperature value
        self.gauge_height = 320
        self.gauge_width = 20
        self.gauge_x = 20
        self.gauge_y = 5
        self.draw_gauge_background()
        self.canvas.configure(background='lightblue')

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


class PitchGauge:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=330, height=300)
        self.canvas.grid(row=0, column=0, padx=20, pady=20)
        self.center_x, self.center_y = 150, 150
        self.side_length = 280  # Set the side length for the square
        self.half_side = self.side_length / 2  # Half of the side length
        self.max_pitch = 20  # Maximum pitch value in degrees
        self.draw_gauge()
        self.label = tk.Label(self.master, text="Pitch",
                              font=('Helvetica', 12))
        self.label.grid(row=0, column=0)
        self.canvas.configure(background='lightblue')

    def draw_gauge(self):
        # Draw the main square
        self.canvas.create_rectangle(self.center_x - self.half_side, self.center_y - self.half_side,
                                     self.center_x + self.half_side, self.center_y + self.half_side,
                                     outline="black")
        # Initial horizon line (flat)
        self.horizon = self.canvas.create_line(self.center_x - self.half_side, self.center_y,
                                               self.center_x + self.half_side, self.center_y,
                                               fill="red", width=2)
        # Create the blue fill for 'water' below the horizon
        self.blue_fill = self.canvas.create_polygon(self.center_x - self.half_side, self.center_y,
                                                    self.center_x + self.half_side, self.center_y,
                                                    self.center_x + self.half_side, self.center_y + self.half_side,
                                                    self.center_x - self.half_side, self.center_y + self.half_side,
                                                    fill="blue")
        # Degree markers and labels
        for i in range(-4, 5):  # -20 to +20 degrees in 5-degree increments
            # Calculate Y offset based on degree
            line_y = self.center_y - (i * self.half_side / 4)
            self.canvas.create_line(self.center_x + self.half_side, line_y,
                                    self.center_x + self.half_side + 10, line_y,
                                    fill="black")
            self.canvas.create_text(self.center_x + self.half_side + 15, line_y,
                                    text=f"{i*5}°", font=("Helvetica", 8), anchor="w")
        self.update_gauge(0)  # Start with a flat horizon

    def update_gauge(self, pitch):
        y_offset = (pitch / self.max_pitch) * self.half_side
        new_y = self.center_y - y_offset
        self.canvas.coords(self.horizon, self.center_x - self.half_side, new_y,
                           self.center_x + self.half_side, new_y)
        self.canvas.coords(self.blue_fill, self.center_x - self.half_side, new_y,
                           self.center_x + self.half_side, new_y,
                           self.center_x + self.half_side, self.center_y + self.half_side,
                           self.center_x - self.half_side, self.center_y + self.half_side)


class RollGauge:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=330, height=300)
        self.canvas.grid(row=1, column=0)
        self.center_x, self.center_y = 150, 150
        self.radius = 140  # Radius of the gauge
        self.draw_gauge()
        self.label = tk.Label(self.master, text="Roll", font=('Helvetica', 12))
        self.label.grid(row=1, column=0)
        self.canvas.configure(background='lightblue')

    def draw_gauge(self):
        # Draw the main circle
        self.canvas.create_oval(self.center_x - self.radius, self.center_y - self.radius,
                                self.center_x + self.radius, self.center_y + self.radius,
                                outline="black")
        # Degree markers and labels horizontally oriented at the right of the gauge
        for i in range(-4, 5):  # -20 to +20 degrees in 5-degree increments
            angle_deg = i * 5
            # Adjust to make lines horizontal
            angle_rad = math.radians(angle_deg)
            # Calculate positions for lines

            line_end_x = self.center_x + self.radius * math.cos(angle_rad)
            line_end_y = self.center_y + self.radius * math.sin(angle_rad)
            # Draw lines extending horizontally to the right
            self.canvas.create_line(
                line_end_x, line_end_y, line_end_x + 10, line_end_y, fill="black")
            # Draw labels to the right of the lines
            self.canvas.create_text(
                line_end_x + 15, line_end_y, text=f"{angle_deg}°", font=("Helvetica", 10), anchor="w")
        # Initial line (flat at angle 0)

        self.rotate_line = self.canvas.create_line(
            self.center_x, self.center_y,
            self.center_x + self.radius, self.center_y,
            fill="red", width=2)

    def update_gauge(self, roll):
        # Calculate new endpoint based on the roll angle
        # Adjust by -90 degrees to make line horizontal
        angle_rad = math.radians(roll*-1)

        start_x = self.center_x - self.radius*math.cos(angle_rad)
        start_y = self.center_y - self.radius*math.sin(angle_rad)
        end_x = self.center_x + self.radius * math.cos(angle_rad)
        end_y = self.center_y + self.radius * math.sin(angle_rad)
        # Update the line's coordinates to reflect the new roll angle
        self.canvas.coords(self.rotate_line, start_x,
                           start_y, end_x, end_y)


class Compass:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=300, height=300)
        self.canvas.grid(row=0, column=3, padx=20, pady=20)
        self.center_x, self.center_y = 150, 150
        self.radius = 140
        self.draw_compass_dial()
        self.needle = self.create_compass_needle()
        self.canvas.configure(background='lightblue')

    def draw_compass_dial(self):
        # Create the outer circle
        self.canvas.create_oval(
            self.center_x - self.radius, self.center_y - self.radius,
            self.center_x + self.radius, self.center_y + self.radius,
            outline="black"
        )
        # Adding cardinal directions and degree marks
        directions = [("N", 0), ("E", 90), ("S", 180), ("W", 270)]
        for label, angle in directions:
            # Adjust to start from the top
            angle_rad = math.radians(angle - 90)
            text_x = self.center_x + self.radius * 0.85 * math.cos(angle_rad)
            text_y = self.center_y + self.radius * 0.85 * math.sin(angle_rad)
            self.canvas.create_text(text_x, text_y, text=label, font=(
                'Helvetica', 14), anchor=tk.CENTER)

        # Adding degree values every 20 degrees
        for i in range(0, 360, 20):
            angle_rad = math.radians(i - 90)  # Adjust to start from the top
            # Calculate positions for text
            text_x = self.center_x + self.radius * 0.75 * math.cos(angle_rad)
            text_y = self.center_y + self.radius * 0.75 * math.sin(angle_rad)
            # Only draw degree marks for non-cardinal directions
            if i % 90 != 0:
                self.canvas.create_text(text_x, text_y, text=f"{i}°", font=(
                    'Helvetica', 10), anchor=tk.CENTER)

    def create_compass_needle(self):
        # Create a triangular needle with a red and black part
        angle_rad = math.radians(-90)  # Pointing North
        x_end = self.center_x + self.radius * 0.8 * math.cos(angle_rad)
        y_end = self.center_y + self.radius * 0.8 * math.sin(angle_rad)
        # Red triangle
        red_triangle = self.canvas.create_polygon(self.center_x, self.center_y, x_end, y_end,
                                                  self.center_x - 10 *
                                                  math.sin(
                                                      angle_rad), self.center_y + 10 * math.cos(angle_rad),
                                                  fill="red", outline="black")
        # Black triangle (opposite direction)
        black_triangle = self.canvas.create_polygon(self.center_x, self.center_y, x_end, y_end,
                                                    self.center_x + 10 *
                                                    math.sin(
                                                        angle_rad), self.center_y - 10 * math.cos(angle_rad),
                                                    fill="black", outline="black")
        return red_triangle, black_triangle

    def update_compass(self, heading_degrees):
        self.canvas.delete("needle")
        angle_rad = math.radians(heading_degrees-90)  # Adjusted by 90 degrees
        x_end = self.center_x + self.radius * 0.8 * math.cos(angle_rad)
        y_end = self.center_y + self.radius * 0.8 * math.sin(angle_rad)
        # Red triangle
        red_triangle = self.canvas.create_polygon(self.center_x, self.center_y, x_end, y_end,
                                                  self.center_x - 10 *
                                                  math.sin(
                                                      angle_rad), self.center_y + 10 * math.cos(angle_rad),
                                                  fill="red", outline="black", tags="needle")
        # Black triangle (opposite direction)
        black_triangle = self.canvas.create_polygon(self.center_x, self.center_y, x_end, y_end,
                                                    self.center_x + 10 *
                                                    math.sin(
                                                        angle_rad), self.center_y - 10 * math.cos(angle_rad),
                                                    fill="black", outline="black", tags="needle")


class PowerGraph:
    def __init__(self, master):
        self.fig, self.ax = plt.subplots(
            figsize=(5, 4))  # Adjust the figsize here
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        # Adjust the line below to use grid instead of pack
        # Adjust the row, column, and rowspan as needed
        self.canvas_widget.grid(row=2, column=0, sticky="nsew")
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Motor Power')
        self.ax.set_title('Time Series of Motor Power (hp)')
        self.power_data = {'time': [], 'value': []}
        # self.canvas.configure(background='lightblue')

    def update_graph(self, new_data, timestamp):
        if len(self.power_data['time']) > 100:
            self.power_data['time'].pop(0)
            self.power_data['value'].pop(0)
        # current_time = datetime.datetime.now()
        self.power_data['time'].append(timestamp*0.001)
        self.power_data['value'].append(new_data)
        self.ax.clear()
        self.ax.plot(self.power_data['time'], self.power_data['value'])
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Motor Power')
        self.canvas.draw()
