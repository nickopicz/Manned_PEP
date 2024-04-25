import sqlite3
import csv

DATABASE_NAME = "frames_data.db"  # Make sure this path is correctly set

# This essentially just turns a trial from the database into a csv file for post processing
# If there is any new data being read, you must adjust the sql_query and heaters list to accomodate

def export_trial_data_to_csv(trial_number):
    CSV_FILE_PATH = f"./csv_data/data_trial_{trial_number}.csv"
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    table_name = f"{trial_number}"  # Ensure table name is treated as a string

    # Check if the table exists before querying
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if cursor.fetchone() is None:
        print(f"No data table found for trial {trial_number}.")
        return  # Exit the function if no table is found

    sql_query = f"""
        SELECT timestamp, voltage, throttle_mv, throttle_percentage, RPM, torque, motor_temp,
        current, pitch, roll, yaw, ax, ay, az, heading, power 
        FROM "{table_name}"
        ORDER BY timestamp ASC
    """

    cursor.execute(sql_query)
    messages = cursor.fetchall()
    conn.close()

    headers = [
        'Timestamp', 'Voltage', 'Throttle mV', 'Throttle %', 'RPM', 'Torque', 'Motor Temp', 'Current',
        'Pitch', 'Roll', 'Yaw', 'Ax', 'Ay', 'Az', 'Heading', 'Power'
    ]

    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in messages:
            writer.writerow(row)


export_trial_data_to_csv("trial_2")
