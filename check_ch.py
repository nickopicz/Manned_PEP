import sqlite3
from canlib import canlib
import time
import struct
import os

from database_functions import create_table_for_pdo, store_to_db, get_next_trial_number
# Mapping from COB-ID to PDO and its information

value_range_map = {
    # COB-ID, Bytes : (Data Type, Description, Value Range, Units)
    # (902, (0, 1)): ("U16", "Status word", "0-65535", ""),
    (902, (2, 3)): ("S16", "Actual speed", "-32768 to 32767", "Rpm"),
    # (902, (4, 5)): ("U16", "RMS motor Current", "0-65535", "Arms"),
    # (902, (6, 7)): ("S16", "DC Bus Voltage", "-32768 to 32767", "Adc"),
    # (1158, (0, 1)): ("S16", "Internal Speed Reference", "-32768 to 32767", "Rpm"),
    # (1158, (2, 3)): ("S16", "Reference Torque", "-32768 to 32767", "Nm"),
    # (1158, (4, 5)): ("S16", "Actual Torque", "-32768 to 32767", "Nm"),
    # (1158, (6, 7)): ("S16", "Field weakening control: voltage angle", "-32768 to 32767", "Deg"),
    # (390, 0): ("U8", "Field weakening control: regulator status", "0-255", ""),
    # (390, 1): ("U8", "Current limit: actual limit type", "0-15", ""),
    # (390, (2, 3)): ("S16", "Motor voltage control: U peak normalized", "-32768 to 32767", ""),
    # (390, (4, 5)): ("U16", "Digital status word", "0-65535", ""),
    # (390, (6, 7)): ("S16", "Scaled throttle percent", "-32768 to 32767", ""),
    # (646, (0, 1)): ("S16", "Motor voltage control: idLimit", "-32768 to 32767", ""),
    # (646, (2, 3)): ("S16", "Motor voltage control: Idfiltered", "-32768 to 32767", "Arms"),
    # (646, (4, 5)): ("S16", "Actual currents: iq", "-32768 to 32767", "Apk"),
    # (646, (6, 7)): ("S16", "Motor measurements: DC bus current", "-32768 to 32767", "Adc"),
}
pdo_map = {
    902: "PDO1",
    1158: "PDO2",
    390: "PDO3",
    646: "PDO4",
}
# pdo_map = {
#     0x186: "PDO1",
#     0x286: "PDO2",
#     0x386: "PDO3",
#     0x486: "PDO4",
# }


def decode_data(msg_id, data_bytes):
    # print(f"Decoding data for msg_id: {msg_id} with data_bytes: {data_bytes}")
    data_values = {}

    for key, (data_type, description, value_range, units) in value_range_map.items():
        cob_id, byte_indices = key

        # Check if the msg_id matches the cob_id. If not, skip this iteration
        if msg_id != cob_id:
            continue

        if isinstance(byte_indices, tuple):
            start, end = key[1]
            # print(f"For msg_id {msg_id}, data_bytes length: {len(data_bytes)}")
            if end is None and start >= len(data_bytes):
                # print("Index out of range for single-byte key:", key)
                continue
            elif end is not None and (start >= len(data_bytes) or end >= len(data_bytes)):
                # print("Index out of range for multi-byte key:", key)
                continue
        else:
            start = key[1]
            if start >= len(data_bytes):
                continue  # Skip this iteration if index is out of range
            end = start  # Use start index as end index for single-byte data

        if data_type == "U16":
            value = (data_bytes[start] << 8) + data_bytes[end]
            # print("value U16: ", value)

        elif data_type == "S16":
            value = struct.unpack('>h', bytes(data_bytes[start:end+1]))[0]
            # print("value S16: ", value)

        elif data_type == "U8":
            value = data_bytes[start]
            # print("value U8: ", value)

        elif data_type == "0-15":
            value = data_bytes[start] & 0x0F
            # print("value 0-15: ", value)

        else:
            value = "Unsupported data type"
            # print("unsupported: ", value)

        data_values[description] = (value, value_range, units)
        # print("data values: ", data_values)

    return data_values


def format_can_message(msg):
    pdo_label = pdo_map.get(msg.id, "Unknown PDO")
    data_values = decode_data(msg.id, msg.data)

    return {
        'pdo_label': pdo_label,
        'data_values': data_values,
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
                msg_data = format_can_message(msg)
                # print("msg_data: ", msg_data)
                # create_table_for_pdo(pdo_label)
                # store_to_db(pdo_label, trial_number, msg)
                # print(f"\n{pdo_label} (COB-ID: {msg.id:X}):")
                for desc, (value, value_range, units) in msg_data['data_values'].items():
                    os.system("cls")
                    if (desc == "Scaled throttle percent"):
                        print("Actual throttle percent: ", value/32767)
                    if (desc == "Actual speed"):
                        print("Real speed scaled: ", value/1000)
                    if (desc == "DC Bus Voltage"):
                        print("Actual Voltage: ", value*0.01)
                    if (desc == "Actual Torque"):
                        print("Actual Torque: ", value*0.1, " nm")
                    if (desc == "Internal Speed Reference"):
                        print("Speed Reference: ", value)
                    # print(f"{desc}: {value} {units} (Range: {value_range})")
            except canlib.CanNoMsg:

                pass  # No new message yet
            except KeyboardInterrupt:
                break  # Exit the loop on Ctrl+C
            # time.sleep(0.5)
    ch.busOff()


if __name__ == "__main__":
    trial_num = get_next_trial_number()
    print("running telemetry display: ", trial_num)
    read_can_messages(trial_num)
    print("finished telemetry display: ", trial_num)
