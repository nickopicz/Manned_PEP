import serial

#This program is for reading serial data from the arduino
# Any new sensor or data being read, must be added to the dictionaries below.
# All you must do is make sure the order in which it is getting printed corresponsd to the loop below

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
def read_serial():
    try:
        line = ser.readline().decode('utf-8').strip()  # Read a line from the serial port
        values = line.split(",")  # Split the line by commas
        
        # Ensure we have the expected number of values before proceeding
        if len(values) != 7:
            return {
                'yaw':0,
                'pitch':0,
                'roll':0,
                'ax': 0,
                'ay':0,
                'az':0,
                'heading':0
                }

        #loop mentioned in desctiption
        yaw, pitch, roll, ax, ay, az, heading = [float(v) for v in values]
#         print("good data:", values)
        return {
                'yaw':yaw,
                'pitch':pitch,
                'roll':roll,
                'ax': ax,
                'ay':ay,
                'az':az,
                'heading':heading
            }
    except UnicodeDecodeError:
        print("Received invalid byte sequence. Skipping...")
        return {'yaw':0,
                'pitch':0,
                'roll':0,
                'ax': 0,
                'ay':0,
                'az':0,
                'heading':0
                }
    except ValueError:
        print("Error in converting values. Skipping...")
        return {'yaw':0,
                'pitch':0,
                'roll':0,
                'ax': 0,
                'ay':0,
                'az':0,
                'heading':0
                }

