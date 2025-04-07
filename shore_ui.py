import tkinter as tk
from tkinter import ttk
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import requests
import threading
from New_UI import CANVariableDisplay, ThrottleGauge, Speedometer, Graph, VoltageGraph, CurrentMeter, ThermometerGauge

# Your previously defined classes (CANVariableDisplay, ThrottleGauge, etc.) go here


class Application:
    def __init__(self, root):
        self.root = root
        self.update_interval = 250  # Update interval in milliseconds
        
        # Configure the window size to fit Mac screen better - increased size
        self.root.geometry("1280x900")  # Increased window size
        
        # Apply a consistent padding and configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.init_ui()

    def init_ui(self):
        # Create a main frame with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid for the main frame with more space
        for i in range(12):  # Increased columns
            main_frame.grid_columnconfigure(i, weight=1, minsize=80)  # Minimum column size
        for i in range(8):  # Increased rows
            main_frame.grid_rowconfigure(i, weight=1, minsize=80)  # Minimum row size
        
        # Initialize UI components with larger sizes and more spacing
        
        # Speedometer - left side
        self.speedometer = Speedometer(main_frame)
        self.speedometer.canvas.config(width=250, height=250)  # Increased size
        self.speedometer.canvas.grid(row=0, column=0, rowspan=3, columnspan=3, padx=20, pady=10)
        
        # Current meter - right side
        self.current_meter = CurrentMeter(main_frame)
        self.current_meter.canvas.config(width=250, height=250)  # Increased size
        self.current_meter.canvas.grid(row=0, column=6, rowspan=3, columnspan=3, padx=20, pady=10)
        
        # Throttle gauge - far right
        self.throttle_gauge = ThrottleGauge(main_frame)
        self.throttle_gauge.canvas.config(width=100, height=250)  # Increased size
        self.throttle_gauge.canvas.grid(row=0, column=10, rowspan=3, padx=20, pady=10)
        
        # Thermometer - center top
        self.thermometer = ThermometerGauge(main_frame)
        self.thermometer.canvas.config(width=90, height=250)  # Increased size
        self.thermometer.canvas.grid(row=0, column=4, rowspan=3, padx=20, pady=10)
        
        # Graphs in bottom row with more space
        self.graph = Graph(main_frame)
        self.graph.fig.set_size_inches(5, 4)  # Increased graph size
        self.graph.canvas_widget.grid(row=4, column=0, rowspan=4, columnspan=5, padx=20, pady=20)
        
        self.voltage_graph = VoltageGraph(main_frame)
        self.voltage_graph.fig.set_size_inches(5, 4)  # Increased graph size
        self.voltage_graph.canvas_widget.grid(row=4, column=6, rowspan=4, columnspan=5, padx=20, pady=20)
        
        # Start the data update loop
        self.update_data_loop()

    def fetch_data(self):
        # Replace 'http://yourserver/get_data' with the actual URL of your API
        try:
            response = requests.get(
                'http://bold-privately-koala.ngrok-free.app/get_data')
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
    
    # Set DPI scaling for high resolution displays - adjusted for better display
    root.tk.call('tk', 'scaling', 1.2)  # Slightly increased scaling
    
    app = Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()
