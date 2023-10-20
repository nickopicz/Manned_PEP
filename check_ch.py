from canlib import canlib
import time
import matplotlib.pyplot as plt
# Mapping from COB-ID to PDO and its information
pdo_map = {
    0x186: "TX1",
    0x286: "TX2",
    0x386: "TX3",
    0x486: "TX4",
}

# Dictionary to map COB-ID and bytes to the corresponding description
desc_map = {
    (0x186, (0, 1)): "Status word",
    (0x186, (2, 3)): "Actual speed",
    (0x186, (4, 5)): "RMS motor Current",
    (0x186, (6, 7)): "DC Bus Voltage",
    (0x286, (0, 1)): "Internal Speed Reference",
    (0x286, (2, 3)): "Reference Torque",
    (0x286, (4, 5)): "Actual Torque",
    (0x286, (6, 7)): "Field weakening control: voltage angle",
    (0x386, 0): "Field weakening control: regulator status",
    (0x386, 1): "Current limit: actual limit type",
    (0x386, (2, 3)): "Motor voltage control: U peak normalized",
    (0x386, (4, 5)): "Digital status word",
    (0x386, (6, 7)): "Scaled throttle percent",
    (0x486, (0, 1)): "Motor voltage control: idLimit",
    (0x486, (2, 3)): "Motor voltage control: Idfiltered",
    (0x486, (4, 5)): "Actual currents: iq",
    (0x486, (6, 7)): "Motor measurements: DC bus current",
}


def decode_data(msg_id, data_bytes):
    data_values = {}
    for i in range(0, len(data_bytes), 2):
        desc = desc_map.get((msg_id, (i, i+1)))
        if desc:
            value = (data_bytes[i] << 8) + \
                data_bytes[i+1]  # 16-bit big-endian value
            data_values[desc] = value

    # For single byte data
    for i in range(len(data_bytes)):
        desc = desc_map.get((msg_id, i))
        if desc:
            value = data_bytes[i]
            data_values[desc] = value

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


def read_can_messages():
    # Initialize and open the channel
    channel = 0

    with canlib.openChannel(channel, canlib.canOPEN_ACCEPT_VIRTUAL) as ch:
        ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
        ch.setBusParams(canlib.canBITRATE_500K)
        ch.busOn()

        while True:
            try:
                msg = ch.read()
                msg_data = format_can_message(msg)

                # Print one parameter per line
                print(f"Received message:")
                print(f"ID={msg.id} ({msg_data['pdo_label']})")
                for desc, value in msg_data['data_values'].items():
                    print(f"{desc}={value}")
                print(f"DLC={msg_data['dlc']}")
                print(f"Flags={msg_data['flags']}")
                print(f"Timestamp={msg_data['timestamp']}\n")

            except canlib.CanNoMsg:
                pass  # No new message yet
            except KeyboardInterrupt:
                break  # Exit the loop on Ctrl+C

    ch.busOff()


if __name__ == "__main__":
    read_can_messages()
