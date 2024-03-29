import canopen
import logging
import time
# Set up logging
logging.basicConfig(level=logging.INFO, filename='canbus_log.txt', filemode='w',
                    format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to log messages


def log_message(message):
    logger.info(f"Message: {message}")


# Start with creating a new network representing one CAN bus
network = canopen.Network()

# Connect to the CAN bus
network.connect(channel='0', bustype='kvaser')

# Subscribe to messages
network.subscribe(0, log_message)

# You can create a node with a known node-ID
node_id = 6  # Replace with your node ID
node = canopen.BaseNode402(node_id, canopen.import_od('testing/69GUS222C00x03.epf')
                           )  # Use a dummy EDS here
network.add_node(node)
# canopen.import_od('testing/69GUS222C00x03.epf')


# Define the object dictionary manually
# Here you should add the SDOs you want to interact with

# node.object_dictionary.add_object(canopen.objectdictionary.Variable(
#     'DCBusVoltage',
#     index=0x2A06,
#     subindex=1,
# ))

# node.object_dictionary.add_object(canopen.objectdictionary.Variable(
#     'ThrottleSignalValue_mV',
#     index=0x2013,
#     subindex=1,

# ))

# node.object_dictionary.add_object(canopen.objectdictionary.Variable(
#     'ScalledThrottlePercent',
#     index=0x2013,
#     subindex=7,

# ))

# node.object_dictionary.add_object(canopen.objectdictionary.Variable(
#     'DC Voltage',
#     index=0x2030,
#     subindex=2,
# ))


# Remember, your application logic goes here
# For example, reading or writing to the nodes

# Don't forget to disconnect from the CAN bus when you're done


def read_and_log_sdo(node, index, subindex):

    try:
        value = node.sdo[index][subindex].raw

        print(f"SDO [{hex(index)}:{subindex}] Value: {value}")
        return value
    except Exception as e:
        print(f"Error reading SDO [{hex(index)}:{subindex}]: {e}")
        return 0

# Read and log each SDO
# read_and_log_sdo(node, 0x2A06, 1)
# read_and_log_sdo(node, 0x2013, 1)
# read_and_log_sdo(node, 0x2030, 2)


def get_sdo_obj() -> {}:
    # voltage = read_and_log_sdo(node, 0x2A06, 1)
    throttle_mv = read_and_log_sdo(node, 0x2013, 1)
    # throttle_percent = read_and_log_sdo(node, 0x2013, 7)
    # rpm
    # rpm = read_and_log_sdo(node, 0x2001, 2)
    # # torque
    # torque = read_and_log_sdo(node, 0x2076, 2)
    # # current
    # current = read_and_log_sdo(node, 0x2073, 1)
    # # temperature
    # temperature = read_and_log_sdo(node, 0x2A0D, 1)

    # timestamp = read_and_log_sdo(node, 0x2A03, 1)
    #
    return {
        # 'timestamp': timestamp,
        # 'voltage': voltage,
        'throttle_mv': throttle_mv,
        # 'throttle_percentage': throttle_percent,
        # 'RPM': rpm,
        # 'torque': torque,
        # 'motor temp': temperature,
        # 'current': current
    }


if __name__ == "__main__":
    for i in range(100):
        # read_and_log_sdo(node, 0x2A06, 1)
        # read_and_log_sdo(node, 0x2013, 1)
        get_sdo_obj()
        # node.sdo.read_response()

        # read_and_log_sdo(node, 0x2030, 2)
        time.sleep(0.5)

network.disconnect()
