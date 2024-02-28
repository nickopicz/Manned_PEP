from maps import format_can_message_csv
import struct
import sqlite3
import csv

DATABASE_NAME = "frames_data.db"


value_range_map = {
    # COB-ID, Bytes : (Data Type, Description, Value Range, Units)
    (390, (0, 1)): ("U16", "Status word", "0-65535", ""),
    (390, (2, 3)): ("S16", "Actual speed", "-32768 to 32767", "Rpm"),
    (390, (4, 5)): ("U16", "RMS motor Current", "0-65535", "Arms"),
    (390, (6, 7)): ("S16", "DC Bus Voltage", "-32768 to 32767", "Adc"),
    (646, (0, 1)): ("S16", "Internal Speed Reference", "-32768 to 32767", "Rpm"),
    (646, (2, 3)): ("S16", "Reference Torque", "-32768 to 32767", "Nm"),
    (646, (4, 5)): ("S16", "Actual Torque", "-32768 to 32767", "Nm"),
    (646, (6, 7)): ("S16", "Field weakening control: voltage angle", "-32768 to 32767", "Deg"),
    (902, 0): ("U8", "Field weakening control: regulator status", "0-255", ""),
    (902, 1): ("U8", "Current limit: actual limit type", "0-15", ""),
    (902, (2, 3)): ("S16", "Motor voltage control: U peak normalized", "-32768 to 32767", ""),
    (902, (4, 5)): ("U16", "Digital status word", "0-65535", ""),
    (902, (6, 7)): ("S16", "Scaled throttle percent", "-32768 to 32767", ""),
    (1158, (0, 1)): ("S16", "Motor voltage control: idLimit", "-32768 to 32767", ""),
    (1158, (2, 3)): ("S16", "Motor voltage control: Idfiltered", "-32768 to 32767", "Arms"),
    (1158, (4, 5)): ("S16", "Actual currents: iq", "-32768 to 32767", "Apk"),
    (1158, (6, 7)): ("S16", "Motor measurements: DC bus current", "-32768 to 32767", "Adc"),
}


def export_trial_data_to_csv(trial_number):
    # Connect to the SQLite database

    CSV_FILE_PATH = "./csv_data/_data_" + str(trial_number) + ".csv"
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT trial_number, timestamp, frame_id, data FROM frame_data WHERE trial_number=?", (trial_number,))
    messages = cursor.fetchall()

    conn.close()

    headers = ['Trial Number', 'Timestamp',
               'Message ID', 'PDO Label', 'DLC', 'Flags']
    descriptions = [desc for _, desc, _, _ in value_range_map.values()]

    headers.extend(descriptions)

    # Open the CSV file and start writing
    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for trial_num, timestamp, frame_id, data in messages:
            # Decode the message

            message = {
                'id': frame_id,
                'data': data,
                'dlc': len(data),
                'flags': 0,
                'timestamp': timestamp
            }

            print("message: ", message)
            decoded_message = format_can_message_csv(message)

            # Prepare the row for the CSV
            row = {
                'Trial Number': trial_num,
                'Timestamp': timestamp,
                'Message ID': decoded_message['frame_id'],
                'PDO Label': decoded_message['pdo_label'],
                'DLC': decoded_message['dlc'],
                'Flags': decoded_message['flags']
            }

            # Add decoded data values to the row
            for desc in descriptions:
                row[desc] = decoded_message['data_values'].get(
                    desc, ('', '', ''))[0]

            writer.writerow(row)


# Example usage
export_trial_data_to_csv(15)
