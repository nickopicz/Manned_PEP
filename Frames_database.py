import sqlite3
import json as JSON

DATABASE_NAME = "/home/pi/Manned_PEP/frames_data.db"


FRAMES_DATABASE = "frames_data.db"


def get_next_trial_number():
    with sqlite3.connect(FRAMES_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value INTEGER
        )
        ''')
        cursor.execute("SELECT value FROM meta WHERE key='trial_number'")
        row = cursor.fetchone()
        trial_number = (row[0] + 1) if row else 1
        cursor.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('trial_number', ?)", (trial_number,))
    print("returning trial number: ", trial_number)
    return trial_number


def create_table_for_trial(conn, trial_number):
    cursor = conn.cursor()
    # Ensure table name is a string and properly formatted
    table_name = trial_number
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        timestamp REAL PRIMARY KEY,
        voltage REAL,
        throttle_mv REAL,
        throttle_percentage INTEGER,
        RPM INTEGER,
        torque REAL,
        motor_temp REAL,
        current REAL
    )
    ''')
    conn.commit()


def store_data_for_trial(data_dicts, trial_number):
    with sqlite3.connect(FRAMES_DATABASE) as conn:
        table_name = trial_number
        create_table_for_trial(conn, trial_number)
        cursor = conn.cursor()
        for data_dict in data_dicts:
            print("storing: ", data_dict)
            placeholders = ', '.join(['?'] * len(data_dict))
            columns = ', '.join([f'"{column}"' for column in data_dict.keys()])
            values = tuple(data_dict.values())
            cursor.execute(
                f'INSERT INTO "{table_name}" ({columns}) VALUES ({placeholders})', values)
        conn.commit()


# def store_frames_to_database(frame_objects):
#     conn = sqlite3.connect(FRAMES_DATABASE)
#     create_tables(conn)

#     # Get the next trial number for this batch of frames
#     trial_number = get_next_trial_number(conn)
#     print("frame objects: ", frame_objects)
#     for frame in frame_objects:
#         store_frame(conn, trial_number, frame)

#     conn.close()
