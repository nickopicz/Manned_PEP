import canopen

# Start with creating a new network representing one CAN bus
network = canopen.Network()

# Connect to the CAN bus
# The specifics here depend on your hardware interface
network.connect(channel='can0', bustype='socketcan')  # Example for SocketCAN

# You can create a node with a known node-ID
node_id = 10  # Replace with your node ID
node = canopen.BaseNode402(
    node_id, None)  # Use a dummy EDS here
network.add_node(node)

# Define the object dictionary manually
# Here you should add the SDOs you want to interact with
# For example, let's define 'LED1ErrorBlinkRate' and 'LED2CurrentReducedBlinkRate'

node.object_dictionary.add_object(canopen.objectdictionary.Variable(
    'Temperature',
    index=0x2040,
    subindex=2,
    data_type=canopen.objectdictionary.INTEGER16,
    access_type="ro"
))

node.object_dictionary.add_object(canopen.objectdictionary.Variable(
    'ActualSpeed',
    index=0x2001,
    subindex=2,
    data_type=canopen.objectdictionary.INTEGER16,
    access_type="ro"
))

node.object_dictionary.add_object(canopen.objectdictionary.Variable(
    'ActTorque',
    index=0x2076,
    subindex=2,
    data_type=canopen.objectdictionary.INTEGER16,
    access_type="ro"
))


# Don't forget to disconnect from the CAN bus when you're done
network.disconnect()
