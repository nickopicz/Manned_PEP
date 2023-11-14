import sqlite3

DATABASE_NAME = "/home/pi/Manned_PEP/db/frames_data.db"


def get_next_trial_number():
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Create a meta table to store the latest trial number if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value INTEGER
    )
    ''')

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

    # Commit and close the connection
    conn.commit()
    conn.close()

    return trial_number


def create_table_for_pdo(pdo_label):
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Dynamically create a table for the given pdo_label if it doesn't exist
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {pdo_label} (
        trial_number INTEGER,
        timestamp REAL,
        msg_id TEXT,
        data_bytes TEXT
    )
    ''')

    # Commit and close the connection
    conn.commit()
    conn.close()


def store_to_db(trial_number, msg):
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Insert the CAN message into the specified pdo_label's table
    try:
        cursor = conn.cursor()
        # Extracting frame attributes
        frame_id = msg.id
        frame_data = msg.data  # Already a bytearray
        dlc = msg.dlc
        flags = msg.flags.value  # Assuming flags is an Enum
        timestamp = msg.timestamp
        print(f"sending: {timestamp} to db")
        cursor.execute('''
        INSERT OR IGNORE INTO frame_data (trial_number, frame_id, data, dlc, flags, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (trial_number, frame_id, frame_data, dlc, flags, timestamp))
        conn.commit()
         
        
        # Commit and close the connection
        conn.close()
    except:
        print("error sending to database, within db funtions")