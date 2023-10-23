import sqlite3
from canlib import canlib
import time
from database_functions import create_table_for_pdo, store_to_db, get_next_trial_number
# Mapping from COB-ID to PDO and its information
pdo_map = {
    0x186: "TX1",
    0x286: "TX2",
    0x386: "TX3",
    0x486: "TX4",
}

# Dictionary to map COB-ID and bytes to the corresponding description
value_range_map = {
    (0x186, (0, 1)): "U16",
    (0x186, (2, 3)): "S16",
    (0x186, (4, 5)): "U16",
    (0x186, (6, 7)): "S16",
    (0x286, (0, 1)): "S16",
    (0x286, (2, 3)): "S16",
    (0x286, (4, 5)): "S16",
    (0x286, (6, 7)): "S16",
    (0x386, 0): "U8",
    (0x386, 1): "0-15",
    (0x386, (2, 3)): "S16",
    (0x386, (4, 5)): "U16",
    (0x386, (6, 7)): "S16",
    (0x486, (0, 1)): "S16",
    (0x486, (2, 3)): "S16",
    (0x486, (4, 5)): "S16",
    (0x486, (6, 7)): "S16",
}


def decode_data(msg_id, data_bytes):
    data_values = {}
    data_ranges = {}
    for i in range(0, len(data_bytes), 2):
        range_val = value_range_map.get((msg_id, (i, i+1)), "-")
        if range_val:
            value = (data_bytes[i] << 8) + \
                data_bytes[i+1]  # 16-bit big-endian value
            data_values[range_val] = value
            data_ranges[range_val] = range_val

    # For single byte data
    for i in range(len(data_bytes)):
        range_val = value_range_map.get((msg_id, i), "-")
        if range_val:
            value = data_bytes[i]
            data_values[range_val] = value
            data_ranges[range_val] = range_val

    return data_values, data_ranges


def format_can_message(msg):
    pdo_label = pdo_map.get(msg.id, "Unknown PDO")
    data_values, data_ranges = decode_data(msg.id, msg.data)

    return {
        'pdo_label': pdo_label,
        'data_values': data_values,
        'data_ranges': data_ranges,
        'dlc': msg.dlc,
        'flags': msg.flags,
        'timestamp': msg.timestamp,
    }


def read_can_messages(trial_number):
    # Initialize and open the channel
    channel = 0

    with canlib.openChannel(channel, canlib.canOPEN_ACCEPT_VIRTUAL) as ch:
        ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
        ch.setBusParams(canlib.canBITRATE_500K)
        ch.busOn()

        while True:
            try:
                msg = ch.read()
                pdo_label = pdo_map.get(msg.id, "Unknown_PDO")

                # Check if a table for this pdo_label exists, if not, create one
                create_table_for_pdo(pdo_label)

                # Store the CAN message in the appropriate table
                store_to_db(pdo_label, trial_number, msg)
                # Print one parameter per line
                for desc, value in msg_data['data_values'].items():
                    print(f"{desc}={value} ({msg_data['data_ranges'][desc]})")
            except canlib.CanNoMsg:
                pass  # No new message yet
            except KeyboardInterrupt:
                break  # Exit the loop on Ctrl+C

    ch.busOff()


if __name__ == "__main__":
    trial_num = get_next_trial_number()
    read_can_messages(trial_num)
