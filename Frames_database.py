import sqlite3
import csv

DATABASE_NAME = "/home/pi/Manned_PEP/frames_data.db"


def export_trial_data_to_csv(trial_number):
    # CSV file path setup
    CSV_FILE_PATH = f"/home/pi/Manned_PEP/csv_data/trial_{trial_number}_data.csv"

    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Dynamically set the table name based on trial_number
    table_name = str(trial_number)

    # SQL query to fetch all data from the specified table
    sql_query = f"""
        SELECT timestamp, voltage, throttle_mv, throttle_percentage, RPM, torque, motor_temp, current,
        pitch, roll, yaw, ax, ay, az, power, heading
        FROM "{table_name}"
        ORDER BY timestamp ASC
    """

    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        print("It seems the table does not exist or there is a typo in the table name.")
        conn.close()
        return  # Exit function early if there is an error

    conn.close()

    # Column headers for the CSV based on the database schema
    headers = [
        'Timestamp', 'Voltage', 'Throttle mV', 'Throttle %', 'RPM', 'Torque', 'Motor Temp', 'Current',
        'Pitch', 'Roll', 'Yaw', 'Ax', 'Ay', 'Az', 'Power', 'Heading'
    ]

    # Writing to CSV
    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)

    print(f"Data exported successfully to {CSV_FILE_PATH}")


# Example usage
trial_number = 17  # Set the trial number you want to export
export_trial_data_to_csv(trial_number)
