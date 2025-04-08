import canopen
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, filename='canbus_log.txt', filemode='w',
                    format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to log messages


def log_message(message):
    logger.info(f"Message: {message}")

# Function to log SDO responses


def log_sdo_response(index, subindex, value):
    logger.info(
        f"Received SDO response: Index={index:X}, SubIndex={subindex}, Value={value}")


# Start with creating a new network representing one CAN bus
network = canopen.Network()

# Connect to the CAN bus
network.connect(channel='0', bustype='kvaser')

# You can create a node with a known node-ID
node_id = 10
node = canopen.BaseNode402(node_id, None)  # Use a dummy EDS here
network.add_node(node)

# Assuming you have already defined the object dictionary entries as in your setup...

# Example function to read an SDO


def read_sdo(node, index, subindex):
    try:
        value = node.sdo.upload(index, subindex)
        log_sdo_response(index, subindex, value)
    except canopen.SdoCommunicationError as e:
        logger.error(f"SDO communication error: {e}")
    except canopen.SdoAbortedError as e:
        logger.error(f"SDO aborted: {e}")


# Example: Read 'Temperature', 'ActualSpeed', and 'ActTorque' via SDO
read_sdo(node, 0x2040, 2)
read_sdo(node, 0x2001, 2)
read_sdo(node, 0x2076, 2)

# Don't forget to disconnect from the CAN bus when you're done
network.disconnect()
