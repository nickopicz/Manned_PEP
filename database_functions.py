import sqlite3

DATABASE_NAME = "/home/pi/Manned_PEP/frames_data.db"

NAME = "frames_data.db"


def get_next_trial_number():
    # Connect to the SQLite database
    conn = sqlite3.connect(NAME)
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
    conn = sqlite3.connect(NAME)
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


def create_frame_data_table():
    # Connect to the SQLite database
    conn = sqlite3.connect(NAME)
    cursor = conn.cursor()

    # Create the frame_data table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS frame_data (
        trial_number INTEGER,
        timestamp REAL,
        frame_id TEXT,
        data TEXT,
        dlc INTEGER,
        flags TEXT
    )
    ''')

    # Commit and close the connection
    conn.commit()
    conn.close()


def store_to_db(msgs, trial_num):
    # create_frame_data_table()
    tuples_list = []
    for msg in msgs:
        # Example of extracting data from a canlib Frame object, adjust according to actual Frame structure
        frame_id = msg.id
        timestamp = msg.timestamp
        data = msg.data  # This might need conversion from bytes to a desired format
        dlc = len(msg.data)  # DLC could be the length of the data field
        flags = msg.flags  # Assuming there's a flags attribute or similar

        # Construct the tuple for this message, adjust based on actual requirements
        msg_tuple = (trial_num, timestamp, frame_id, data, dlc, flags)
        tuples_list.append(msg_tuple)

    # Continue with database insertion as before
    with sqlite3.connect(NAME) as conn:
        cursor = conn.cursor()
        insert_query = '''
        INSERT INTO frame_data (trial_number, timestamp, frame_id, data, dlc, flags) 
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        try:
            cursor.executemany(insert_query, tuples_list)
            conn.commit()
        except Exception as e:
            print(f"Error sending to database: {e}")
