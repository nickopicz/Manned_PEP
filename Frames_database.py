import sqlite3
import json as JSON


def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frame_data (
            trial_number INTEGER,
            frame_id INTEGER,
            data BLOB,
            dlc INTEGER,
            flags INTEGER,
            timestamp INTEGER,
            PRIMARY KEY (trial_number, frame_id, timestamp)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value INTEGER
        )
    ''')
    conn.commit()


def get_next_trial_number(conn):
    cursor = conn.cursor()

    # Query the latest trial number from the meta table
    cursor.execute("SELECT value FROM meta WHERE key='trial_number'")
    row = cursor.fetchone()

    if row:
        # If found, increment the trial number
        trial_number = row[0] + 1
    else:
        # If not found, initialize with trial number 1
        trial_number = 1

    # Update the meta table with the latest trial number
    cursor.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES ('trial_number', ?)", (trial_number,))
    conn.commit()

    return trial_number


def store_frame(conn, trial_number, frame):
    cursor = conn.cursor()
    # Extracting frame attributes
    print("\n frame looked at: ", frame)
    frame_id = frame.id
    frame_data = frame.data  # Already a bytearray
    dlc = frame.dlc
    flags = frame.flags.value  # Assuming flags is an Enum
    timestamp = frame.timestamp

    cursor.execute('''
    INSERT OR IGNORE INTO frame_data (trial_number, frame_id, data, dlc, flags, timestamp) 
    VALUES (?, ?, ?, ?, ?, ?)
''', (trial_number, frame_id, frame_data, dlc, flags, timestamp))
    conn.commit()


DATABASE_NAME = "/home/pi/Manned_PEP/frames_data.db"


FRAMES_DATABASE = "frames_data.db"


def store_frames_to_database(frame_objects):
    conn = sqlite3.connect(FRAMES_DATABASE)
    create_tables(conn)

    # Get the next trial number for this batch of frames
    trial_number = get_next_trial_number(conn)
    print("frame objects: ", frame_objects)
    for frame in frame_objects:
        store_frame(conn, trial_number, frame)

    conn.close()
