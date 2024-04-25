import tkinter as tk
from tkinter import ttk
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import requests
import threading
from New_UI import ThrottleGauge, Speedometer, CurrentMeter, ThermometerGauge, PitchGauge, RollGauge, Compass, PowerGraph, Graph, CurrentGraph


# Run this before or after running "initiate_server.py" script.
# The script will display the UI in fullscreen mode when run, and will GET data via REST from the live server
# data being shown will be most recent that the ship has sent, based on timestamp
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shore Data Feed")
        self.update_interval = 250  # Update interval in milliseconds
        self.state('zoomed')
        self.configure(background='lightblue')
        self.init_ui()

    def init_ui(self):
        # Initialize your UI components here
        self.throttle_gauge = ThrottleGauge(self)
        self.current_meter = CurrentMeter(self)
        self.speedometer = Speedometer(self)
        self.graph = Graph(self)
        self.current_graph = CurrentGraph(self)
        self.thermometer = ThermometerGauge(self)
        self.pitch = PitchGauge(self)
        self.roll = RollGauge(self)
        self.compass = Compass(self)
        self.power = PowerGraph(self)
        # Start the data update loop
        self.update_data_loop()

    def on_closing(self):
        print("Closing application...")

        # Destroy the Tkinter app window
        self.destroy()

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

            rpm = abs(data['RPM'])
            current = abs(data['current'])
            roll = data['roll']
            pitch = data['pitch']
            # converting current with torque constant, from Nm to lbft
            # converting lbft to lbin, then getting HP by multiplying by rpm then
            torque = data['torque']
            power = data['power']
            temp = data['motor_temp']
            print("torque: ", torque)
            # Here you would update your individual UI components with the new data
            # For example, updating the throttle gauge:
            self.throttle_gauge.update_gauge(data.get('throttle_mv', 0))
            # Similarly, update other components...
            # Assuming your data includes a timestamp, current, rpm, and voltage, you could do:
            current_time = data['timestamp']
            self.graph.update_graph(torque, current_time)
            self.current_graph.update_graph(
                current, current_time)
            self.current_meter.update_dial(current)
            self.speedometer.update_dial(rpm)
            self.thermometer.update_gauge(temp)
            self.roll.update_gauge(roll)
            self.pitch.update_gauge(pitch)
            self.compass.update_compass(data['heading'])
            self.power.update_graph(power, current_time)
            # self.accel.update_vectors(data['ax'], data['ay'], data['az'])

            # And so on for other UI components as necessary

    def update_data_loop(self):
        # Fetch new data
        data = self.fetch_data()
        # Update the UI with this new data
        self.update_ui(data)
        # Schedule the next update
        self.after(self.update_interval, self.update_data_loop)


def main():
    app = Application()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.on_closing()


if __name__ == "__main__":
    main()
