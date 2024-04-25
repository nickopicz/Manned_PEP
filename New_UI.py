import tkinter as tk
from tkinter import ttk
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# For in depth information regarding libraries being used, follow official documentation for:
# Matplotlib, Tkinter, datetime, etc.


class ThrottleGauge:
    def __init__(self, master):
        # Initialize the gauge with a canvas and set its position
        self.master = master
        self.canvas = tk.Canvas(master, width=50, height=300)
        self.canvas.grid(row=1, column=4, rowspan=2)
        self.min_real_value = 170  # Minimum possible throttle value
        self.max_real_value = 2810  # Maximum possible throttle value
        self.gauge_height = 250  # Total height of the throttle gauge
        self.gauge_width = 20    # Width of the gauge
        self.gauge_x = 25        # X position of the gauge
        self.gauge_y = 25        # Y position of the gauge
        self.current_value = 0   # Current throttle value
        self.draw_gauge_background()  # Draw gauge background
        self.canvas.configure(background='lightblue')
        self.value_label = tk.Label(master, text="0 %", font=('Helvetica', 10))
        self.value_label.grid(row=2, column=4)

    def draw_gauge_background(self):
        # Draw the static parts of the gauge
        self.canvas.create_rectangle(self.gauge_x, self.gauge_y,
                                     self.gauge_x + self.gauge_width,
                                     self.gauge_y + self.gauge_height, outline="black")

    def update_gauge(self, real_value):
        # Update the gauge based on the real throttle value
        self.current_value = max(self.min_real_value, min(
            self.max_real_value, real_value))
        percentage = ((self.current_value - self.min_real_value) /
                      (self.max_real_value - self.min_real_value)) * 100
        self.value_label.config(
            text=f"{round(((self.current_value-165)/2800)*100)} %")
        oval_bottom_y = self.gauge_y + self.gauge_height - \
            ((percentage / 100) * self.gauge_height)
        oval_top_y = oval_bottom_y - self.gauge_width
        self.canvas.delete("fill")
        self.canvas.create_rectangle(self.gauge_x + 1, self.gauge_y + self.gauge_height,
                                     self.gauge_x + self.gauge_width - 1, oval_bottom_y, fill="yellow", tags="fill")


# Steps to adjusting size of the meters (current and speedometer):
# 1) Change the size of the canvas (ie: width and height) to your desired size
# 2) Adjust the radius to be about half of the width or height, no greater.
# 3) If further adjustments are needed, check the values in "createCurrentDial()" method and -
#    adjust the values that are associated with radius.

# The class CurrentMeter represents a current meter in a user interface
class CurrentMeter:
    def __init__(self, master):
        # Initial setup for the current meter display
        self.canvas = tk.Canvas(master, width=300, height=300)
        self.canvas.grid(row=0, column=2, rowspan=2)
        self.center_x, self.center_y = 150, 150  # Center of the dial
        self.max_value = 600  # Maximum value for current meter
        self.needle = self.create_current_dial()  # Create the dial
        self.label = tk.Label(
            master, text="Motor Current (Amps)", font=('Helvetica', 12))
        self.label.grid(row=0, column=2)
        self.canvas.configure(background='lightblue')
        self.value_label = tk.Label(
            master, text="0 amps", font=('Helvetica', 10))
        self.value_label.grid(row=1, column=2)

    def create_current_dial(self):
        # Create the arc for the current meter dial
        radius = 140
        self.canvas.create_arc(self.center_x - radius, self.center_y - radius,
                               self.center_x + radius, self.center_y + radius,
                               start=-30, extent=240, outline="black", style=tk.ARC)
        major_ticks = 10  # Number of major ticks on the dial
        for i in range(major_ticks + 1):
            # Calculate tick angle
            angle = math.radians(150 + (240 * i / major_ticks))
            start_x = self.center_x + ((radius-radius*0.15) * math.cos(angle))
            start_y = self.center_y + ((radius-radius*0.15) * math.sin(angle))
            end_x = self.center_x + (radius * math.cos(angle))
            end_y = self.center_y + (radius * math.sin(angle))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="black")
            label_angle = math.radians(150 + (240 * i / major_ticks))
            label_x = self.center_x + \
                ((radius-radius*0.3) * math.cos(label_angle))
            label_y = self.center_y + \
                ((radius-radius*0.3) * math.sin(label_angle))
            label_value = int((self.max_value / major_ticks) * i)
            self.canvas.create_text(label_x, label_y, text=str(label_value))
        angle = math.radians(150)  # Initial angle pointing at 0
        x1, y1 = self.center_x + (radius-radius*0.3) * \
            math.cos(angle), self.center_y + \
            (radius-radius*0.3) * math.sin(angle)
        return self.canvas.create_line(self.center_x, self.center_y, x1, y1, fill="red", width=2)

    def update_dial(self, current):
        # Update the dial to reflect the current value
        self.canvas.delete(self.needle)
        angle = math.radians(150 + (240 * current / self.max_value))
        x1, y1 = self.center_x + (radius-radius*0.3) * \
            math.cos(angle), self.center_y + \
            (radius-radius*0.3) * math.sin(angle)
        self.value_label.config(text=f"{current} amps")
        self.needle = self.canvas.create_line(
            self.center_x, self.center_y, x1, y1, fill="red", width=2)


class Speedometer:
    def __init__(self, master):
        # Initialize the Speedometer with a canvas for visual representation
        self.canvas = tk.Canvas(master, width=300, height=300)
        self.canvas.grid(row=0, column=1, rowspan=2)
        self.center_x, self.center_y = 150, 150  # Center of the dial
        self.max_value = 3500  # Maximum speed value the dial can display
        self.needle = self.create_speedometer_dial()  # Create the dial components
        self.label = tk.Label(master, text="RPM", font=('Helvetica', 12))
        self.canvas.configure(background='lightblue')
        self.label.grid(row=0, column=1)
        self.value_label = tk.Label(
            master, text="0 rpm", font=('Helvetica', 10))
        self.value_label.grid(row=1, column=1)

    def create_speedometer_dial(self):
        # Create the dial with major tick marks and labels
        radius = 140
        self.canvas.create_arc(self.center_x - radius, self.center_y - radius, self.center_x +
                               radius, self.center_y + radius, start=-30, extent=240, outline="black", style=tk.ARC)
        major_ticks = 10  # Number of major ticks on the dial
        for i in range(major_ticks + 1):
            # Calculate tick angle
            angle = math.radians(150 + (240 * i / major_ticks))
            start_x = self.center_x + ((radius-radius*0.15) * math.cos(angle))
            start_y = self.center_y + ((radius-radius*0.15) * math.sin(angle))
            end_x = self.center_x + (radius * math.cos(angle))
            end_y = self.center_y + (radius * math.sin(angle))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="black")
            label_angle = math.radians(150 + (240 * i / major_ticks))
            label_x = self.center_x + \
                ((radius-radius*0.3) * math.cos(label_angle))
            label_y = self.center_y + \
                ((radius-radius*0.3) * math.sin(label_angle))
            label_value = int((self.max_value / major_ticks) * i)
            self.canvas.create_text(label_x, label_y, text=str(label_value))
        angle = math.radians(150)  # Initial angle pointing at 0
        x1, y1 = self.center_x + (radius-radius*0.3) * \
            math.cos(angle), self.center_y + \
            (radius-radius*0.3) * math.sin(angle)
        return self.canvas.create_line(self.center_x, self.center_y, x1, y1, fill="red", width=2)

    def update_dial(self, speed):
        # Update the needle on the dial based on the speed input
        self.canvas.delete(self.needle)
        angle = math.radians(150 + (240 * speed / self.max_value))
        x1, y1 = self.center_x + (radius-radius*0.3) * \
            math.cos(angle), self.center_y + \
            (radius-radius*0.3) * math.sin(angle)
        self.value_label.config(text=f"{speed} rpm")
        self.needle = self.canvas.create_line(
            self.center_x, self.center_y, x1, y1, fill="red", width=2)


class Graph:
    def __init__(self, master):
        # Initialize a matplotlib graph integrated within a Tkinter canvas
        # Define the size of the graph
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=2, column=2, sticky="nsew")
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Actual Torque')
        self.ax.set_title('Time Series of Torque (lb ft)')
        # Initialize data storage for torque
        self.torque_data = {'time': [], 'value': []}

    def update_graph(self, new_data, timestamp):
        # Update the graph with new torque data and timestamp
        # Limit data history to maintain performance
        if len(self.torque_data['time']) > 50:
            self.torque_data['time'].pop(0)
            self.torque_data['value'].pop(0)
        # Adjust timestamp if necessary
        self.torque_data['time'].append(timestamp*0.001)
        self.torque_data['value'].append(new_data)
        self.ax.clear()  # Clear and redraw the graph
        self.ax.plot(self.torque_data['time'], self.torque_data['value'])
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Torque')
        self.canvas.draw()  # Refresh the canvas to display the updated graph


class CurrentGraph:
    def __init__(self, master):
        # Initialize a graph for displaying motor current over time
        # Define the size of the graph
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=2, column=1, sticky="nsew")
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Motor Current')
        self.ax.set_title('Time Series of Motor Current (amps)')
        # Data storage for motor current
        self.current_data = {'time': [], 'value': []}

    def update_graph(self, new_data, timestamp):
        # Update the graph with new current data and timestamp
        if len(self.current_data['time']) > 100:  # Limit data history
            self.current_data['time'].pop(0)
            self.current_data['value'].pop(0)
        self.current_data['time'].append(timestamp*0.001)
        self.current_data['value'].append(new_data)
        self.ax.clear()  # Clear the graph for a fresh plot
        self.ax.plot(self.current_data['time'], self.current_data['value'])
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Motor Current')
        self.canvas.draw()  # Update the canvas to show the new data


class ThermometerGauge:
    def __init__(self, master):
        # Setup the thermometer display within a Tkinter canvas
        self.master = master
        self.canvas = tk.Canvas(master, width=90, height=350)
        self.canvas.grid(row=1, column=3, rowspan=2)
        self.value_label = tk.Label(
            master, text="0 °C", font=('Helvetica', 10))
        self.value_label.grid(row=2, column=3)
        self.min_temp = 0  # Define the minimum temperature that the gauge can display
        self.max_temp = 140  # Define the maximum temperature
        self.gauge_height = 320
        self.gauge_width = 20
        self.gauge_x = 20
        self.gauge_y = 5
        self.draw_gauge_background()  # Create the static parts of the gauge
        self.canvas.configure(background='lightblue')

    def draw_gauge_background(self):
        # Draw the temperature gauge background including tick marks and labels
        self.canvas.create_rectangle(self.gauge_x, self.gauge_y,
                                     self.gauge_x + self.gauge_width, self.gauge_y + self.gauge_height,
                                     outline="black")
        for temp in range(self.min_temp, self.max_temp + 1, 25):  # Draw ticks every 25 degrees
            percentage = (temp - self.min_temp) / \
                (self.max_temp - self.min_temp)
            y = self.gauge_y + self.gauge_height - \
                (percentage * self.gauge_height)
            self.canvas.create_line(
                self.gauge_x, y, self.gauge_x + 10, y, fill="black")
            self.canvas.create_line(self.gauge_x + self.gauge_width -
                                    10, y, self.gauge_x + self.gauge_width, y, fill="black")
            self.canvas.create_text(
                self.gauge_x + self.gauge_width + 10, y, text=f"{temp}°C", anchor="w")

    def update_gauge(self, current_temp):
        # Update the displayed temperature and adjust the gauge's filled region accordingly
        current_temp = max(self.min_temp, min(
            self.max_temp, current_temp))  # Validate temperature
        percentage = (current_temp - self.min_temp) / \
            (self.max_temp - self.min_temp)
        fill_height = percentage * self.gauge_height
        self.value_label.config(text=f"{current_temp} °C")
        self.canvas.delete("temp_fill")
        color = "red" if current_temp > 60 else "green"
        self.canvas.create_rectangle(self.gauge_x + 1, self.gauge_y + self.gauge_height - fill_height,
                                     self.gauge_x + self.gauge_width - 1, self.gauge_y + self.gauge_height,
                                     fill=color, tags="temp_fill")


class PitchGauge:
    def __init__(self, master):
        # Initialize a pitch gauge with a graphical representation of pitch angle
        self.master = master
        self.canvas = tk.Canvas(master, width=330, height=300)
        self.canvas.grid(row=0, column=0, padx=20, pady=20)
        self.center_x, self.center_y = 150, 150
        self.side_length = 280  # Define the dimensions of the gauge
        self.half_side = self.side_length / 2
        self.max_pitch = 20  # Maximum displayable pitch angle in degrees
        self.draw_gauge()
        self.label = tk.Label(master, text="Pitch", font=('Helvetica', 12))
        self.label.grid(row=0, column=0)
        self.canvas.configure(background='lightblue')

    def draw_gauge(self):
        # Draw the pitch gauge, including the horizon line and angle markers
        self.canvas.create_rectangle(self.center_x - self.half_side, self.center_y - self.half_side,
                                     self.center_x + self.half_side, self.center_y + self.half_side, outline="black")
        self.horizon = self.canvas.create_line(self.center_x - self.half_side, self.center_y,
                                               self.center_x + self.half_side, self.center_y, fill="red", width=2)
        self.blue_fill = self.canvas.create_polygon(self.center_x - self.half_side, self.center_y,
                                                    self.center_x + self.half_side, self.center_y,
                                                    self.center_x + self.half_side, self.center_y + self.half_side,
                                                    self.center_x - self.half_side, self.center_y + self.half_side, fill="blue")
        for i in range(-4, 5):
            line_y = self.center_y - (i * self.half_side / 4)
            self.canvas.create_line(self.center_x + self.half_side, line_y,
                                    self.center_x + self.half_side + 10, line_y, fill="black")
            self.canvas.create_text(self.center_x + self.half_side + 15,
                                    line_y, text=f"{i*5}°", font=("Helvetica", 8), anchor="w")
        self.update_gauge(0)  # Initialize with a flat horizon

    def update_gauge(self, pitch):
        # Adjust the horizon line based on the current pitch angle
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
        # Initialize a roll gauge to display aircraft roll angle
        self.master = master
        self.canvas = tk.Canvas(master, width=330, height=300)
        self.canvas.grid(row=1, column=0)
        self.center_x, self.center_y = 150, 150
        self.radius = 140
        self.draw_gauge()
        self.label = tk.Label(master, text="Roll", font=('Helvetica', 12))
        self.label.grid(row=1, column=0)
        self.canvas.configure(background='lightblue')

    def draw_gauge(self):
        # Create the gauge's graphical representation including degree markers
        self.canvas.create_oval(self.center_x - self.radius, self.center_y - self.radius,
                                self.center_x + self.radius, self.center_y + self.radius, outline="black")
        for i in range(-4, 5):
            angle_deg = i * 5
            angle_rad = math.radians(angle_deg)
            line_end_x = self.center_x + self.radius * math.cos(angle_rad)
            line_end_y = self.center_y + self.radius * math.sin(angle_rad)
            self.canvas.create_line(
                line_end_x, line_end_y, line_end_x + 10, line_end_y, fill="black")
            self.canvas.create_text(
                line_end_x + 15, line_end_y, text=f"{angle_deg}°", font=("Helvetica", 10), anchor="w")
        self.rotate_line = self.canvas.create_line(self.center_x, self.center_y,
                                                   self.center_x + self.radius, self.center_y, fill="red", width=2)

    def update_gauge(self, roll):
        # Update the graphical display based on the roll angle
        angle_rad = math.radians(roll*-1)
        start_x = self.center_x - self.radius * math.cos(angle_rad)
        start_y = self.center_y - self.radius * math.sin(angle_rad)
        end_x = self.center_x + self.radius * math.cos(angle_rad)
        end_y = self.center_y + self.radius * math.sin(angle_rad)
        self.canvas.coords(self.rotate_line, start_x, start_y, end_x, end_y)


class Compass:
    def __init__(self, master):
        # Initialize the compass on a Tkinter canvas to display directional heading
        self.canvas = tk.Canvas(master, width=300, height=300)
        # Position the compass within the grid layout
        self.canvas.grid(row=0, column=3, padx=20, pady=20)
        self.center_x, self.center_y = 150, 150  # Set the center point for the compass
        self.radius = 140  # Define the radius for the compass circle
        self.draw_compass_dial()  # Call method to draw the compass dial
        self.needle = self.create_compass_needle()  # Create the compass needle
        # Set the background color for aesthetics
        self.canvas.configure(background='lightblue')

    def draw_compass_dial(self):
        # This method draws the outer circle and directional markers on the compass
        self.canvas.create_oval(self.center_x - self.radius, self.center_y - self.radius,
                                self.center_x + self.radius, self.center_y + self.radius, outline="black")
        # Add cardinal direction labels (N, E, S, W) adjusted to the correct positions based on circle geometry
        directions = [("N", 0), ("E", 90), ("S", 180), ("W", 270)]
        for label, angle in directions:
            # Convert angle for correct placement
            angle_rad = math.radians(angle - 90)
            text_x = self.center_x + self.radius * 0.85 * math.cos(angle_rad)
            text_y = self.center_y + self.radius * 0.85 * math.sin(angle_rad)
            self.canvas.create_text(text_x, text_y, text=label, font=(
                'Helvetica', 14), anchor=tk.CENTER)

        # Draw degree marks around the compass every 20 degrees
        for i in range(0, 360, 20):
            angle_rad = math.radians(i - 90)
            text_x = self.center_x + self.radius * 0.75 * math.cos(angle_rad)
            text_y = self.center_y + self.radius * 0.75 * math.sin(angle_rad)
            if i % 90 != 0:  # Avoid overwriting cardinal direction labels
                self.canvas.create_text(text_x, text_y, text=f"{i}°", font=(
                    'Helvetica', 10), anchor=tk.CENTER)

    def create_compass_needle(self):
        # Method to create the compass needle consisting of two colored triangles indicating direction
        angle_rad = math.radians(-90)  # Needle pointing North (upwards)
        x_end = self.center_x + self.radius * 0.8 * math.cos(angle_rad)
        y_end = self.center_y + self.radius * 0.8 * math.sin(angle_rad)
        # Red triangle part of the needle pointing North
        red_triangle = self.canvas.create_polygon(
            self.center_x, self.center_y, x_end, y_end,
            self.center_x - 10 *
            math.sin(angle_rad), self.center_y + 10 * math.cos(angle_rad),
            fill="red", outline="black")
        # Black triangle part of the needle, opposite direction to the red
        black_triangle = self.canvas.create_polygon(
            self.center_x, self.center_y, x_end, y_end,
            self.center_x + 10 *
            math.sin(angle_rad), self.center_y - 10 * math.cos(angle_rad),
            fill="black", outline="black")
        return red_triangle, black_triangle

    def update_compass(self, heading_degrees):
        # Update the needle direction based on the new heading degree input
        self.canvas.delete("needle")  # Remove the old needle from the canvas
        # Adjust heading to be relative to North
        angle_rad = math.radians(heading_degrees - 90)
        x_end = self.center_x + self.radius * 0.8 * math.cos(angle_rad)
        y_end = self.center_y + self.radius * 0.8 * math.sin(angle_rad)
        # Recreate the needle with the new heading
        red_triangle = self.canvas.create_polygon(
            self.center_x, self.center_y, x_end, y_end,
            self.center_x - 10 *
            math.sin(angle_rad), self.center_y + 10 * math.cos(angle_rad),
            fill="red", outline="black", tags="needle")
        black_triangle = self.canvas.create_polygon(
            self.center_x, self.center_y, x_end, y_end,
            self.center_x + 10 *
            math.sin(angle_rad), self.center_y - 10 * math.cos(angle_rad),
            fill="black", outline="black", tags="needle")


class PowerGraph:
    def __init__(self, master):
        # Setup the PowerGraph in a Tkinter interface using Matplotlib for plotting
        # Create a subplot for graphical display
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        # Integrate Matplotlib figure with Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        # Position the graph within the grid layout
        self.canvas_widget.grid(row=2, column=0, sticky="nsew")
        self.ax.set_xlabel('Time')  # Set the x-axis label
        self.ax.set_ylabel('Motor Power')  # Set the y-axis label
        # Title of the graph
        self.ax.set_title('Time Series of Motor Power (hp)')
        # Initialize data storage for power measurements
        self.power_data = {'time': [], 'value': []}

    def update_graph(self, new_data, timestamp):
        # Method to update the graph with new power data and timestamps
        # Limit data history to 100 points for performance
        if len(self.power_data['time']) > 100:
            self.power_data['time'].pop(0)  # Remove the oldest data point
            self.power_data['value'].pop(0)
        # Append new timestamp (convert if needed)
        self.power_data['time'].append(timestamp * 0.001)
        self.power_data['value'].append(new_data)  # Append new power data
        self.ax.clear()  # Clear the graph for redrawing
        # Plot the updated data
        self.ax.plot(self.power_data['time'], self.power_data['value'])
        self.ax.set_xlabel('Time')  # Confirm x-axis label
        self.ax.set_ylabel('Motor Power')  # Confirm y-axis label
        self.canvas.draw()  # Redraw the canvas with the updated graph
