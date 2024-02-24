import sqlite3
import time
import tkinter as tk
from collections import namedtuple
from New_UI import Graph, CANVariableDisplay, Speedometer, CurrentMeter, VoltageGraph
import threading
import sys
from maps import format_can_message
print("Script started")
# Constants for database access
FRAME_DATABASE = "frames_data.db"
frametype = namedtuple('Frame', ['id', 'data', 'dlc', 'flags', 'timestamp'])

# Meters: RPM, Speed, Current
# Torque
# Pitch/Yaw/Roll
# G-Force/Accel
# Voltage


def simulate_live_feed(trial_number):
    conn = sqlite3.connect(FRAME_DATABASE)
    cursor = conn.cursor()
    query = '''
        SELECT frame_id, data, dlc, flags, timestamp
        FROM frame_data
        WHERE trial_number = ?
        ORDER BY timestamp ASC
    '''
    try:
        cursor.execute(query, (trial_number,))
        all_rows = cursor.fetchall()
        print(f"Fetched {len(all_rows)} rows for trial number {trial_number}")
    except Exception as e:
        print("Database error:", e)
        all_rows = []
    finally:
        cursor.close()
        conn.close()

    messages = [format_can_message(frametype._make(row)) for row in all_rows]
    return messages


def on_closing():
    # Add any cleanup here
    root.destroy()
    sys.exit()


class App(tk.Frame):
    def __init__(self, master, trial_number):
        super().__init__(master)
        self.master = master
        self.pack()
        # Maximizes the window keeping taskbar accessible

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        # self.master.geometry(f'{screen_width}x{screen_height}')
        self.master.state('zoomed')

        self.master.title("CAN Variable Display")
        self.master.resizable(False, False)
        self.data = simulate_live_feed(trial_number=trial_number)
        self.can_display = CANVariableDisplay(self)
        self.speedometer = Speedometer(self)
        self.currentmeter = CurrentMeter(self)
        self.graph = Graph(self)
        self.voltagegraph = VoltageGraph(self)

        self.simulation_thread = threading.Thread(
            target=self.run_simulation, args=(trial_number,))
        self.simulation_thread.daemon = True  # Daemonize thread
        self.simulation_thread.start()

    def run_simulation(self, trial_number):
        for formatted_msg in self.data:
            self.master.after_idle(
                lambda msg=formatted_msg: self.update_ui(msg))
            time.sleep(0.01)

    def update_ui(self, formatted_msg):
        try:
            # print("Formatted message received in update_ui:",
            #       formatted_msg)  # Debugging print

            self.can_display.update_display(formatted_msg)
            data_values = formatted_msg.get('data_values', {})
            print("message: ", formatted_msg)

            speed = data_values.get('Actual speed', (0,))[0]
            torque = data_values.get('Actual Torque', (0,))[0]  # Ass
            current = data_values.get(
                'Motor measurements: DC bus current', (0,))[0]*0.1

    # 'Motor measurements: DC bus current'
    # 'RMS motor Current'

            voltage = data_values.get(
                'Motor voltage control: Idfiltered', (0,))[0]

            # print("\n ============= \n obj: ", formatted_msg)
            # print("Speed:", speed, "Torque:", torque)  # Debugging print
            speed = abs(speed*0.1)
            torque = abs(torque*0.01)
            self.speedometer.update_dial(speed)
            self.graph.update_graph(torque)
            self.currentmeter.update_dial(current)
            self.voltagegraph.update_graph(voltage)
            print("current is: ", current)
            if speed > 3500:
                print("speed very big: ", speed)
        except Exception as e:
            print("Error in update_ui:", e)


if __name__ == "__main__":
    print("====================== \n \n simulation starting \n \n======================")
    try:
        root = tk.Tk()
        root.protocol("WM_DELETE_WINDOW", on_closing)
        trial_number = 8  # Update this to the correct trial number from your database
        myapp = App(root, trial_number)
        root.mainloop()
    except Exception as e:
        print("Error Occurred: ", e)
