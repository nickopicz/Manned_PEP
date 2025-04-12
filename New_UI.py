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


# More information on this file in the shore directory version of this program
# There are some differences, mainly in the sizes
class CurrentMeter:
    def __init__(self, master):
        self.frame = tk.Frame(master, width=350, height=350)
        self.frame.grid(row=0, column=1, rowspan=2)
        self.frame.grid_propagate(False)  # Prevent frame from shrinking
        self.frame.configure(background='white')
        
        self.max_value = 550
        
        # Create a large label for the current value
        self.value_label = tk.Label(
            self.frame, text="0", font=('Helvetica', 128), bg='white')
        self.value_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        
        # Create a smaller label for the unit
        self.unit_label = tk.Label(
            self.frame, text="amps", font=('Helvetica', 48), bg='white')
        self.unit_label.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    def update_dial(self, current):
        # Update the value label with the current value and change colors when max current exceeded
        if current > 400:
            amps_color = 'red'
            text_color = 'white'
        else:
            amps_color = 'white'
            text_color = 'black'
        self.value_label.config(text=current, background=amps_color, foreground=text_color)
        self.unit_label.config(background=amps_color, foreground=text_color)
        self.frame.configure(background=amps_color)


class Speedometer:
    def __init__(self, master):
        self.frame = tk.Frame(master, width=350, height=350)
        self.frame.grid(row=0, column=3, padx=20, rowspan=2)
        self.frame.grid_propagate(False)  # Prevent frame from shrinking
        self.frame.configure(background='white')
        
        self.max_value = 3500
        
        # Create a large label for the speed value
        self.value_label = tk.Label(
            self.frame, text="0", font=('Helvetica', 128), bg='white')
        self.value_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        
        # Create a smaller label for the unit
        self.unit_label = tk.Label(
            self.frame, text="rpm", font=('Helvetica', 48), bg='white')
        self.unit_label.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    def update_dial(self, speed):
        # Update the value label with the current speed
        self.value_label.config(text=f"{speed}")


class ThermometerGauge:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=500, height=100)
        self.canvas.grid(row=3, column=2, padx=20, pady=5, columnspan=2)  # Shifted to column 2 and reduced columnspan
        self.value_label = tk.Label(
            master, text="0 °C", font=('Helvetica', 80), bg='white')
        self.value_label.grid(row=3, column=1)
        self.min_temp = -10  # Minimum temperature value
        self.max_temp = 120  # Maximum temperature value
        self.gauge_width = 460  # Now represents the width of the horizontal gauge
        self.gauge_height = 25  # Now represents the height of the horizontal gauge
        self.gauge_x = 10  # Starting x position of the gauge
        self.gauge_y = 20  # Starting y position of the gauge
        self.draw_gauge_background()
        self.canvas.configure(background='white')

    def draw_gauge_background(self):
        # Draw the outer rectangle
        self.canvas.create_rectangle(self.gauge_x, self.gauge_y,
                                     self.gauge_x + self.gauge_width, self.gauge_y + self.gauge_height,
                                     outline="black")

        # Draw ticks and labels for horizontal orientation
        for temp in range(self.min_temp, self.max_temp + 1, 10):
            percentage = (temp - self.min_temp) / \
                (self.max_temp - self.min_temp)
            # x position for ticks and labels
            x = self.gauge_x + percentage * self.gauge_width

            # Ticks
            self.canvas.create_line(
                x, self.gauge_y, x, self.gauge_y + 10, fill="black")
            self.canvas.create_line(x, self.gauge_y + self.gauge_height -
                                    10, x, self.gauge_y + self.gauge_height, fill="black")

            # Labels, adjusted for horizontal layout
            self.canvas.create_text(
                x, self.gauge_y + self.gauge_height + 15, text=f"{temp}°C", anchor="n")

    def update_gauge(self, current_temp):
        # Validate current temperature
        current_temp = max(self.min_temp, min(self.max_temp, current_temp))
        percentage = (current_temp - self.min_temp) / \
            (self.max_temp - self.min_temp)
        # Width of the fill reflects the current temperature
        fill_width = percentage * self.gauge_width

        self.value_label.config(text=f"{current_temp} °C")
        # Clear previous fill
        self.canvas.delete("temp_fill")
        # Draw new fill
        if current_temp > 95:
            color = "red"
        elif current_temp > 40 and current_temp < 95:
            color = "green"
        else:
            color = 'blue'
        self.canvas.create_rectangle(self.gauge_x, self.gauge_y + 1,
                                     self.gauge_x + fill_width, self.gauge_y + self.gauge_height - 1,
                                     fill=color, tags="temp_fill")


# class Compass:
#     def __init__(self, master):
#         self.canvas = tk.Canvas(master, width=200, height=200)
#         self.canvas.grid(row=0, column=2, padx=30, pady=20)
#         self.center_x, self.center_y = 100, 100
#         self.radius = 100
#         self.draw_compass_dial()
#         self.needle = self.create_compass_needle()
#         self.canvas.configure(background='white')

#     def draw_compass_dial(self):
#         # Create the outer circle
#         self.canvas.create_oval(
#             self.center_x - self.radius, self.center_y - self.radius,
#             self.center_x + self.radius, self.center_y + self.radius,
#             outline="black"
#         )
#         # Adding cardinal directions and degree marks
#         directions = [("N", 0), ("E", 90), ("S", 180), ("W", 270)]
#         for label, angle in directions:
#             # Adjust to start from the top
#             angle_rad = math.radians(angle - 90)
#             text_x = self.center_x + self.radius * 0.85 * math.cos(angle_rad)
#             text_y = self.center_y + self.radius * 0.85 * math.sin(angle_rad)
#             self.canvas.create_text(text_x, text_y, text=label, font=(
#                 'Helvetica', 10), anchor=tk.CENTER)

#         # Adding degree values every 20 degrees
#         for i in range(0, 360, 20):
#             angle_rad = math.radians(i - 90)  # Adjust to start from the top
#             # Calculate positions for text
#             text_x = self.center_x + self.radius * 0.75 * math.cos(angle_rad)
#             text_y = self.center_y + self.radius * 0.75 * math.sin(angle_rad)
#             # Only draw degree marks for non-cardinal directions
#             if i % 90 != 0:
#                 self.canvas.create_text(text_x, text_y, text=f"{i}°", font=(
#                     'Helvetica', 10), anchor=tk.CENTER)

#     def create_compass_needle(self):
#         # Create a triangular needle with a red and black part
#         angle_rad = math.radians(-90)  # Pointing North
#         x_end = self.center_x + self.radius * 0.8 * math.cos(angle_rad)
#         y_end = self.center_y + self.radius * 0.8 * math.sin(angle_rad)
#         # Red triangle
#         red_triangle = self.canvas.create_polygon(self.center_x, self.center_y, x_end, y_end,
#                                                   self.center_x - 10 *
#                                                   math.sin(
#                                                       angle_rad), self.center_y + 10 * math.cos(angle_rad),
#                                                   fill="red", outline="black", tags="needle")
#         # Black triangle (opposite direction)
#         black_triangle = self.canvas.create_polygon(self.center_x, self.center_y, x_end, y_end,
#                                                     self.center_x + 10 *
#                                                     math.sin(
#                                                         angle_rad), self.center_y - 10 * math.cos(angle_rad),
#                                                     fill="black", outline="black", tags="needle")
#         return red_triangle, black_triangle

#     def update_compass(self, heading_degrees):
#         self.canvas.delete("needle")
#         angle_rad = math.radians(heading_degrees-90)  # Adjusted by 90 degrees
#         x_end = self.center_x + self.radius * 0.8 * math.cos(angle_rad)
#         y_end = self.center_y + self.radius * 0.8 * math.sin(angle_rad)
#         # Red triangle
#         red_triangle = self.canvas.create_polygon(self.center_x, self.center_y, x_end, y_end,
#                                                   self.center_x - 10 *
#                                                   math.sin(
#                                                       angle_rad), self.center_y + 10 * math.cos(angle_rad),
#                                                   fill="red", outline="black", tags="needle")
#         # Black triangle (opposite direction)
#         black_triangle = self.canvas.create_polygon(self.center_x, self.center_y, x_end, y_end,
#                                                     self.center_x + 10 *
#                                                     math.sin(
#                                                         angle_rad), self.center_y - 10 * math.cos(angle_rad),
#                                                     fill="black", outline="black", tags="needle")