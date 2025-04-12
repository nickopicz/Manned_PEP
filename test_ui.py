#!/usr/bin/env python3
import tkinter as tk
from New_UI import CurrentMeter, Speedometer, ThermometerGauge
import platform

class TestApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CAN Bus Monitoring - Test Mode")
        
        # Set the background color of the main window
        self.configure(bg='white')
        
        # Handle window state based on platform
        if platform.system() == 'Windows':
            self.state('zoomed')
        else:
            # For Linux/Unix systems, maximize window using geometry
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        self.init_ui()
        
    def init_ui(self):
        # Initialize all UI components with default values
        self.current_meter = CurrentMeter(self)
        self.speedometer = Speedometer(self)
        self.thermometer = ThermometerGauge(self)
        # self.compass = Compass(self)
        
        # Initialize components with zero/default values
        self.current_meter.update_dial(390)
        self.speedometer.update_dial(999)
        self.thermometer.update_gauge(100)
        # self.compass.update_compass(0)  # Pointing North

if __name__ == "__main__":
    app = TestApplication()
    app.mainloop() 