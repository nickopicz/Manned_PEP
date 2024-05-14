import tkinter as tk
from tkinter import ttk
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import requests
import threading
from Fake_UI import ThrottleGauge, Speedometer, Graph, CurrentGraph, CurrentMeter, ThermometerGauge, AccelerationDisplay


# Like Fake_UI this is just for showing mock data for something like a presentation
class Application:
    def __init__(self, root):
        self.root = root
        self.update_interval = 250  # Update interval in milliseconds

        self.init_ui()
        self.update_ui({})

    def init_ui(self):
        # Initialize your UI components here
        self.throttle_gauge = ThrottleGauge(self.root)
        self.current_meter = CurrentMeter(self.root)
        self.speedometer = Speedometer(self.root)
        self.graph = Graph(self.root)
        self.voltage_graph = CurrentGraph(self.root)
        self.thermometer = ThermometerGauge(self.root)

    def update_ui(self, data):
        if data:
            # Here you would update your individual UI components with the new data
            # For example, updating the throttle gauge:
            self.throttle_gauge.update_gauge(data.get('throttle_mv', 0))
            # Similarly, update other components...

            # Assuming your data includes a timestamp, current, rpm, and voltage, you could do:
            current_time = data['timestamp']
            self.graph.update_graph(1, 1)
            self.voltage_graph.update_graph(1, 1)
            self.current_meter.update_dial(45)
            self.speedometer.update_dial(2100)
            self.thermometer.update_gauge(40)
def main():
    root = tk.Tk()
    root.title("Data Monitoring Application")
    app = Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()
