import sqlite3

DATABASE_NAME = "/home/pi/Manned_PEP/frames_data.db"

NAME = "frames_data.db"


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


def store_to_db(msgs, trial_num):
    # Connect to the SQLite database
    with sqlite3.connect(NAME) as conn:
        cursor = conn.cursor()
        # Prepare batch insert query

        keys_order = ['timestamp', 'frame_id', 'data', 'dlc', 'flags']

        # Convert list of dictionaries to list of tuples
        tuples_list = []
        for msg in msgs:
            print("message: ", msg)
            # Start the tuple with 'trial_num', then extract other values in the correct order
            tuple_values = (trial_num,) + tuple(msg[key] for key in keys_order)
            tuples_list.append(tuple_values)

        insert_query = '''
        INSERT INTO frame_data (trial_number, timestamp, frame_id, data, dlc, flags) 
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        try:
            cursor.executemany(insert_query, msgs)
            conn.commit()
        except Exception as e:
            print(f"Error sending to database, within db functions: {e}")
