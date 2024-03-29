import sqlite3

DATABASE_NAME = "/home/pi/Manned_PEP/frames_data.db"

NAME = "frames_data.db"


def get_next_trial_number():
    with sqlite3.connect(DATABASE_NAME) as conn:
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
    return trial_number


def create_table_for_trial(conn, trial_number):
    # This function now creates a table specifically for a given trial number
    # Each table will store data dictionaries as rows
    cursor = conn.cursor()
    table_name = trial_number
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
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


def store_data_for_trial(data_dicts, trial_number):
    with sqlite3.connect(DATABASE_NAME) as conn:
        # Create a table for this specific trial
        create_table_for_trial(conn, trial_number)
        cursor = conn.cursor()
        table_name = trial_number
        for data_dict in data_dicts:
            placeholders = ', '.join(['?'] * len(data_dict))
            columns = ', '.join(data_dict.keys())
            values = tuple(data_dict.values())
            cursor.execute(
                f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})', values)
        conn.commit()
