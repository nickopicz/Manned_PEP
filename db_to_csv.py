import sqlite3
import csv

DATABASE_NAME = "frames_data.db"  # Make sure this path is correctly set


def export_trial_data_to_csv(trial_number):
    CSV_FILE_PATH = f"./csv_data/data_{trial_number}.csv"
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Table name dynamically based on the trial number
    table_name = trial_number

    # Prepare the SQL query to fetch all data from the specified table, ordered by timestamp
    sql_query = f"""
        SELECT timestamp, voltage, throttle_mv, throttle_percentage, RPM, torque, motor_temp,
        current, pitch, roll, yaw, ax, ay, az, heading, power 
        FROM "{table_name}"
        ORDER BY timestamp ASC
    """

    cursor.execute(sql_query)
    messages = cursor.fetchall()

    conn.close()

    # Define headers for CSV file based on the columns in the database
    headers = [
        'Timestamp', 'Voltage', 'Throttle mV', 'Throttle %', 'RPM', 'Torque', 'Motor Temp', 'Current',
        'Pitch', 'Roll', 'Yaw', 'Ax', 'Ay', 'Az', 'Heading', 'Power'
    ]

    # Open the CSV file and start writing
    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        for row in messages:
            writer.writerow(row)


# Example usage
export_trial_data_to_csv(22)
