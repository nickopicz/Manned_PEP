from canlib import canlib

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


def format_can_message(msg):
    data_hex = ' '.join(['{:02X}'.format(byte) for byte in msg.data])
    pdo_label = pdo_map.get(msg.id, "Unknown PDO")
    descriptions = []

    for i in range(0, len(msg.data), 2):  # Assuming data bytes always come in pairs
        desc = desc_map.get((msg.id, (i, i+1)))
        if desc:
            descriptions.append(desc)

    description_str = ', '.join(descriptions)

    return f"Received message: ID={msg.id} ({pdo_label}), Descriptions=[{description_str}], Data=[{data_hex}], DLC={msg.dlc}, Flags={msg.flags}, Timestamp={msg.timestamp}"


def read_can_messages():
    # Initialize and open the channel
    channel = 0  # As mentioned: "Kvaser U100 (channel 0)"
    with canlib.openChannel(channel, canlib.canOPEN_ACCEPT_VIRTUAL) as ch:
        ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
        ch.setBusParams(canlib.canBITRATE_500K)
        ch.busOn()

        while True:
            try:
                msg = ch.read()
                formatted_msg = format_can_message(msg)
                print(formatted_msg)
            except canlib.CanNoMsg:
                pass  # No new message yet
            except KeyboardInterrupt:
                break  # Exit the loop on Ctrl+C

        ch.busOff()


if __name__ == "__main__":
    read_can_messages()
