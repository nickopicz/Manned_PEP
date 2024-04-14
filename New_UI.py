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


class CurrentMeter:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=350, height=350)
        self.canvas.grid(row=0, column=1, rowspan=2)
        self.center_x, self.center_y = 175, 175
        self.max_value = 450
        self.needle = self.create_current_dial()
#         self.label = tk.Label(master, text="Motor Current (Amps)",
#                               font=('Helvetica', 12))
#         self.label.grid(row=0, column=1)
        self.canvas.configure(background='lightblue')
        self.value_label = tk.Label(master, text="0 amps", font=('Helvetica', 14))
        self.value_label.grid(row=0, column=1)
#         self.value_label = tk.Label(
#              master, text="0", font=('Helvetica', 10))
#         self.value_label.grid(row=0, column=1)

    def create_current_dial(self):
        radius = 175
        self.canvas.create_arc(
            self.center_x - radius, self.center_y - radius,
            self.center_x + radius, self.center_y + radius,
            start=-30, extent=240, outline="black", style=tk.ARC
        )
        major_ticks = 10
        for i in range(major_ticks + 1):
            angle = math.radians(150 + (240 * i / major_ticks))
            start_x = self.center_x + (135 * math.cos(angle))
            start_y = self.center_y + (135 * math.sin(angle))
            end_x = self.center_x + (147 * math.cos(angle))
            end_y = self.center_y + (147 * math.sin(angle))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="black")

            label_angle = math.radians(150 + (240 * i / major_ticks))
            label_x = self.center_x + (160 * math.cos(label_angle))
            label_y = self.center_y + (160 * math.sin(label_angle))
            label_value = int((self.max_value / major_ticks) * i)
            self.canvas.create_text(label_x, label_y, text=str(label_value), font=("Helvetica", 12))
        angle = math.radians(150)  # Initial angle pointing at 0
        x1, y1 = self.center_x + 120 * \
            math.cos(angle), self.center_y + 120 * math.sin(angle)
        return self.canvas.create_line(self.center_x, self.center_y, x1, y1, fill="red", width=2)

    def update_dial(self, current):
        self.canvas.delete(self.needle)
        angle = math.radians(150 + (240 * current / self.max_value))
        x1, y1 = self.center_x + 80 * \
            math.cos(angle), self.center_y + 80 * math.sin(angle)
        # self.value_label.config(text=f"{current}")

        self.needle = self.canvas.create_line(
            self.center_x, self.center_y, x1, y1, fill="red", width=2)
        self.value_label.config(
            text=f"{current} amps")

class Speedometer:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=350, height=350)
        self.canvas.grid(row=0, column=3, padx=20, rowspan=2)
        self.center_x, self.center_y = 175, 175
        self.max_value = 3500
        self.needle = self.create_speedometer_dial()
#         self.label = tk.Label(master, text="RPM",
#                               font=('Helvetica', 12))
        self.canvas.configure(background='lightblue')
#         self.label.grid(row=1, column=3)
        self.value_label = tk.Label(master, text="0 rpm", font=('Helvetica', 14))
        self.value_label.grid(row=0, column=3)
        # self.value_label = tk.Label(
        #     master, text="0 rpm", font=('Helvetica', 10))
        # self.value_label.grid(row=2, column=3)

    def create_speedometer_dial(self):
        radius = 175
        self.canvas.create_arc(
            self.center_x - radius, self.center_y - radius,
            self.center_x + radius, self.center_y + radius,
            start=-30, extent=240, outline="black", style=tk.ARC
        )
        major_ticks = 10
        for i in range(major_ticks + 1):
            angle = math.radians(150 + (240 * i / major_ticks))
            start_x = self.center_x + (135 * math.cos(angle))
            start_y = self.center_y + (135 * math.sin(angle))
            end_x = self.center_x + (147 * math.cos(angle))
            end_y = self.center_y + (147 * math.sin(angle))
            self.canvas.create_line(
                start_x, start_y, end_x, end_y, fill="black")

            label_angle = math.radians(150 + (240 * i / major_ticks))
            label_x = self.center_x + (160 * math.cos(label_angle))
            label_y = self.center_y + (160 * math.sin(label_angle))
            label_value = int((self.max_value / major_ticks) * i)
            self.canvas.create_text(label_x, label_y, text=str(label_value),font=("Helvetica", 12))

        angle = math.radians(150)  # Initial angle pointing at 0
        x1, y1 = self.center_x + 115 * \
            math.cos(angle), self.center_y + 115 * math.sin(angle)
        return self.canvas.create_line(self.center_x, self.center_y, x1, y1, fill="red", width=2)

    def update_dial(self, speed):
        self.canvas.delete(self.needle)
        angle = math.radians(150+ (240 * speed / self.max_value))
        x1, y1 = self.center_x + 80 * \
            math.cos(angle), self.center_y + 80 * math.sin(angle)
        # self.value_label.config(text=f"{speed}")

        self.needle = self.canvas.create_line(
            self.center_x, self.center_y, x1, y1, fill="red", width=2)
        self.value_label.config(
            text=f"{speed} rpm")

class ThermometerGauge:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=500, height=100)
        self.canvas.grid(row=3, column=1, padx=20, pady=5, columnspan=3)
        self.value_label = tk.Label(master, text="0 °C", font=('Helvetica', 14))
        self.value_label.grid(row=3, column=1)
        self.min_temp = 0  # Minimum temperature value
        self.max_temp = 100  # Maximum temperature value
        self.gauge_width = 460  # Now represents the width of the horizontal gauge
        self.gauge_height = 25  # Now represents the height of the horizontal gauge
        self.gauge_x = 10  # Starting x position of the gauge
        self.gauge_y = 20  # Starting y position of the gauge
        self.draw_gauge_background()
        self.canvas.configure(background='lightblue')

    def draw_gauge_background(self):
        # Draw the outer rectangle
        self.canvas.create_rectangle(self.gauge_x, self.gauge_y,
                                     self.gauge_x + self.gauge_width, self.gauge_y + self.gauge_height,
                                     outline="black")

        # Draw ticks and labels for horizontal orientation
        for temp in range(self.min_temp, self.max_temp + 1, 10):
            percentage = (temp - self.min_temp) / (self.max_temp - self.min_temp)
            x = self.gauge_x + percentage * self.gauge_width  # x position for ticks and labels

            # Ticks
            self.canvas.create_line(x, self.gauge_y, x, self.gauge_y + 10, fill="black")
            self.canvas.create_line(x, self.gauge_y + self.gauge_height - 10, x, self.gauge_y + self.gauge_height, fill="black")

            # Labels, adjusted for horizontal layout
            self.canvas.create_text(x, self.gauge_y + self.gauge_height + 15, text=f"{temp}°C", anchor="n")

    def update_gauge(self, current_temp):
        # Validate current temperature
        current_temp = max(self.min_temp, min(self.max_temp, current_temp))
        percentage = (current_temp - self.min_temp) / (self.max_temp - self.min_temp)
        fill_width = percentage * self.gauge_width  # Width of the fill reflects the current temperature

        self.value_label.config(text=f"{current_temp} °C")
        # Clear previous fill
        self.canvas.delete("temp_fill")
        # Draw new fill
        color = "red" if current_temp > 60 else "green"
        self.canvas.create_rectangle(self.gauge_x, self.gauge_y + 1,
                                     self.gauge_x + fill_width, self.gauge_y + self.gauge_height - 1,
                                     fill=color, tags="temp_fill")

class Compass:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=200, height=200)
        self.canvas.grid(row=0, column=2, padx=30, pady=20)
        self.center_x, self.center_y = 100, 100
        self.radius = 100
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
                'Helvetica', 10), anchor=tk.CENTER)

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
                                                  fill="red", outline="black", tags="needle")
        # Black triangle (opposite direction)
        black_triangle = self.canvas.create_polygon(self.center_x, self.center_y, x_end, y_end,
                                                    self.center_x + 10 *
                                                    math.sin(
                                                        angle_rad), self.center_y - 10 * math.cos(angle_rad),
                                                    fill="black", outline="black", tags="needle")
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