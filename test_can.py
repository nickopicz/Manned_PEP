#!/usr/bin/env python3

from canlib import canlib


class CANReader:
    def __init__(self, channel=0, bitrate=canlib.canBITRATE_500K):
        self.channel = channel
        self.bitrate = bitrate
        self.running = True

    def setup_can_channel(self):
        self.ch = canlib.openChannel(
            self.channel, canlib.canOPEN_ACCEPT_VIRTUAL)
        self.ch.setBusOutputControl(canlib.canDRIVER_NORMAL)
        self.ch.setBusParams(self.bitrate)
        self.ch.busOn()

    def read_can_messages(self):
        try:
            self.setup_can_channel()
            print("Reading CAN messages. Press Ctrl+C to stop.")
            while self.running:
                try:
                    msg = self.ch.read()
                    if msg.flags & canlib.MessageFlag.ERROR_FRAME:
                        print(
                            f"Error frame detected: Timestamp {msg.timestamp}")
                    else:
                        print(
                            f"Message: ID={msg.id}, Data={msg.data}, Timestamp={msg.timestamp}")
                except canlib.CanNoMsg:
                    continue
                except Exception as e:
                    print(f"Error reading CAN message: {e}")
        finally:
            self.ch.busOff()

    def stop(self):
        self.running = False


if __name__ == "__main__":
    reader = CANReader()
    try:
        reader.read_can_messages()
    except KeyboardInterrupt:
        reader.stop()
        print("Stopped reading CAN messages.")
