import sqlite3

DATABASE_NAME = 'db/can_data.db'


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


def store_to_db(pdo_label, trial_number, msg):
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Insert the CAN message into the specified pdo_label's table
    cursor.execute(f'''
    INSERT INTO {pdo_label} (trial_number, timestamp, msg_id, data_bytes)
    VALUES (?, ?, ?, ?)
    ''', (trial_number, msg.timestamp, hex(msg.id), ','.join(map(str, msg.data))))

    # Commit and close the connection
    conn.commit()
    conn.close()
