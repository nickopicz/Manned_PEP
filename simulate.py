import sqlite3
import time
import struct
from canlib import Frame
import os
from check_ch import format_can_message
# Adjust these constants according to your setup
DATABASE_NAME = "db/can_data.db"
FRAME_DATABASE = "./db/frames_data.db"


# def fetch_can_data(trial_number, pdo_label):
#     conn = sqlite3.connect(DATABASE_NAME)
#     cursor = conn.cursor()
#     table_name = f"{pdo_label}_data"
#     cursor.execute(
#         f"SELECT pdo_label, timestamp, msg_id, data_bytes FROM {table_name} WHERE trial_number = ? ORDER BY timestamp ASC", (trial_number,))
#     data = cursor.fetchall()
#     conn.close()
#     return data


# def simulate_can_message(data):
#     pdo_label, timestamp, msg_id, data_bytes = data
#     data_bytes = [int(byte) for byte in data_bytes.split(',')]
#     msg = Frame(id=int(msg_id, 16), data=data_bytes, timestamp=timestamp)
#     return pdo_label, msg


# def main():
#     trial_number = 1  # Change to the trial number you want to simulate
#     pdo_label = "PDO1"  # Set this to the PDO label you want to simulate
#     previous_timestamp = None

#     for data in fetch_can_data(trial_number, pdo_label):
#         pdo_label, simulated_msg = simulate_can_message(data)

#         if previous_timestamp is not None:
#             # Introduce delay to simulate real timing
#             time.sleep(simulated_msg.timestamp - previous_timestamp)

#         # Process the simulated CAN message here
#         # For example, you can print it out:
#         formatted_data = format_can_message(simulated_msg)
#         os.system("cls")
#         for desc, (value, value_range, units) in formatted_data['data_values'].items():
#             print(f"{desc}: {value} {units} (Range: {value_range})")

#         previous_timestamp = simulated_msg.timestamp


def simulate_live_feed(trial_number, delay=0.01):
    conn = sqlite3.connect(FRAME_DATABASE)
    cursor = conn.cursor()

    query = '''
        SELECT frame_id, data, dlc, flags, timestamp
        FROM frame_data
        WHERE trial_number = ?
        ORDER BY timestamp ASC
    '''
    # cursor.execute(query, (trial_number,))

    # while True:
    #     row = cursor.fetchone()
    #     if row is None:
    #         break  # No more frames, stop the simulation
    #     frame = Frame(row[0], bytearray(row[1]), row[2],
    #                   MessageFlag(row[3]), row[4])
    #     print(f"Yielding frame: {frame}")  # Debug print
    #     yield frame
    #     time.sleep(delay)

    # conn.close()
    cursor.execute(query, (trial_number,))
    # Debug print to check if the query fetched any data
    all_rows = cursor.fetchall()
    print(f"Fetched {len(all_rows)} rows for trial number {trial_number}")
    for row in all_rows:
        # Recreate the original loop logic with fetched rows for debugging
        frame = Frame(row[0], bytearray(row[1]), row[2],
                      "", row[4])
        yield frame
        time.sleep(delay)


def sim_frames():

    trial_number = 0  # This needs to be the correct trial number from your database
    print("simulating trial : ", trial_number,
          "\n----------------------")
    for frame in simulate_live_feed(trial_number=trial_number, delay=0.01):
        # print(f"Simulated frame: {frame}")  # Debug print
        formatted_msg = format_can_message(frame)
        for desc, (value, value_range, units) in formatted_msg['data_values'].items():
            # os.system("cls")
            # if (desc == "Scaled throttle percent"):
            #     print("Actual throttle percent: ", value/32767)
            if (desc == "Actual speed"):
                print("Real speed scaled: ", value/10)
            # if (desc == "DC Bus Voltage"):
            #     print("Actual Voltage: ", value*0.01)
            # if (desc == "Actual Torque"):
            #     print("Actual Torque: ", value*0.1, " nm")
            # if (desc == "Internal Speed Reference"):
            #     print("Speed Reference: ", value)
            # print(f"{desc}: {value} {units} (Range: {value_range})")
            print("description: ", desc, "value: ", value)


if __name__ == "__main__":
    print("====================== \n \n simulation starting \n \n======================")
    sim_frames()
