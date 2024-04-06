import tkinter as tk
from tkinter import ttk
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import requests
import threading
from New_UI import CANVariableDisplay, ThrottleGauge, Speedometer, Graph, VoltageGraph, CurrentMeter, ThermometerGauge, AccelerationDisplay

# Your previously defined classes (CANVariableDisplay, ThrottleGauge, etc.) go here


class Application:
    def __init__(self, root):
        self.root = root
        self.update_interval = 250  # Update interval in milliseconds

        self.init_ui()

    def init_ui(self):
        # Initialize your UI components here
        self.throttle_gauge = ThrottleGauge(self.root)
        self.current_meter = CurrentMeter(self.root)
        self.speedometer = Speedometer(self.root)
        self.graph = Graph(self.root)
        self.voltage_graph = VoltageGraph(self.root)
        self.thermometer = ThermometerGauge(self.root)
        self.accel = AccelerationDisplay(self.root)
        # Start the data update loop
        self.update_data_loop()

    def fetch_data(self):
        # Replace 'http://yourserver/get_data' with the actual URL of your API
        try:
            response = requests.get(
                'https://hugely-dashing-lemming.ngrok-free.app/get_data')
            if response.status_code == 200:
                print("data in fetch() : ", response.json())
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Failed to fetch data: {e}")
            return None

    def update_ui(self, data):
        if data:
            # Here you would update your individual UI components with the new data
            # For example, updating the throttle gauge:
            self.throttle_gauge.update_gauge(data.get('throttle_mv', 0))
            # Similarly, update other components...

            # Assuming your data includes a timestamp, current, rpm, and voltage, you could do:
            current_time = data['timestamp']
            self.graph.update_graph(data['torque'], current_time)
            self.voltage_graph.update_graph(data['voltage'], current_time)
            self.current_meter.update_dial(data['current'])
            self.speedometer.update_dial(data['RPM'])
            self.thermometer.update_gauge(data['motor_temp'])
            self.accel.update_vectors(data['ax'], data['ay'], data['az'])

            # And so on for other UI components as necessary

    def update_data_loop(self):
        # Fetch new data
        data = self.fetch_data()
        # Update the UI with this new data
        self.update_ui(data)
        # Schedule the next update
        self.root.after(self.update_interval, self.update_data_loop)


def main():
    root = tk.Tk()
    root.title("Data Monitoring Application")
    app = Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()
