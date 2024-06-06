import serial
import time
from threading import Event
import serial.tools.list_ports

BAUD_RATE = 115200

def remove_comment(string):
    if (string.find(';') == -1):
        return string
    else:
        return string[:string.index(';')]

def remove_eol_chars(string):
    # removed \n or trailing spaces
    return string.strip()

def send_wake_up(ser):
    # Wake up
    # Hit enter a few times to wake the Printrbot
    ser.write(str.encode("\r\n\r\n"))
    time.sleep(1)   # Wait for Printrbot to initialize
    ser.flushInput()  # Flush startup text in serial input

def wait_for_movement_completion(ser, cleaned_line):
    Event().wait(1)

    if cleaned_line != '$X' and cleaned_line != '$$':
        idle_counter = 0
        while True:
            ser.reset_input_buffer()
            command = str.encode('?' + '\n')
            ser.write(command)
            grbl_out = ser.readline() 
            grbl_response = grbl_out.strip().decode('utf-8')

            if grbl_response != 'ok':
                if 'Idle' in grbl_response:
                    idle_counter += 1
            if idle_counter > 10:
                break
    return

def send_gcode_command(ser, command):
    cleaned_line = remove_eol_chars(remove_comment(command))
    if cleaned_line:
        print(f"Sending gcode: {cleaned_line}")
        ser.write(str.encode(cleaned_line + '\n'))  # Send g-code
        wait_for_movement_completion(ser, cleaned_line)
        grbl_out = ser.readline()  # Wait for response with carriage return
        print(f" : {grbl_out.strip().decode('utf-8')}")


def moveX(positionX, relative=False):
    with serial.Serial(GRBL_port_path, BAUD_RATE) as ser:
        mode_command = "G91" if relative else "G90"
        send_gcode_command(ser, mode_command)
        send_gcode_command(ser, f"G1 X{positionX}")

def moveY(positionY, relative=False):
    with serial.Serial(GRBL_port_path, BAUD_RATE) as ser:
        mode_command = "G91" if relative else "G90"
        send_gcode_command(ser, mode_command)
        send_gcode_command(ser, f"G1 Y{positionY}")

def moveZ(positionZ, relative=False):
    with serial.Serial(GRBL_port_path, BAUD_RATE) as ser:
        mode_command = "G91" if relative else "G90"
        send_gcode_command(ser, mode_command)
        send_gcode_command(ser, f"G1 Z{positionZ}")

def homeXY():
    with serial.Serial(GRBL_port_path, BAUD_RATE) as ser:
        send_gcode_command(ser, "$H")


def get_current_position_():
    with serial.Serial(GRBL_port_path, BAUD_RATE) as ser:
        ser.write(str.encode("?" + '\n'))
        grbl_out = ser.readline()  # Wait for response with carriage return
        response = grbl_out.strip().decode('utf-8')
        print(f"Current Position: {response}")
        return response


def get_current_position():
    with serial.Serial(GRBL_port_path, BAUD_RATE) as ser:
        send_wake_up(ser)
        ser.write(str.encode("?" + '\n'))
        grbl_out = ser.readline()  # Wait for response with carriage return
        response = grbl_out.strip().decode('utf-8')
        print(f"Current Position: {response}")
        
        # Extracting the WPos values from the response
        if 'WPos:' in response:
            start = response.find('WPos:') + len('WPos:')
            end = response.find('|', start)
            wpos_str = response[start:end]
            x, y, z = map(float, wpos_str.split(','))
            position = {'X': x, 'Y': y, 'Z': z}
            return position
        return None

def find_GRBL_port_path():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'Arduino' in port.manufacturer:
            return port.device
    return None


if __name__ == "__main__":
    GRBL_port_path = find_GRBL_port_path()
    if GRBL_port_path:
        print(f"Arduino Uno found at port: {GRBL_port_path}")
    else:
        print("Arduino Uno not found")

    
    # scan all ports and select the arduino uno port 

    print("USB Port: ", GRBL_port_path)
    
    # Test the new move functions
    moveX(10)  # Move to X=10 absolute
    get_current_position_() 
    mPosition = get_current_position()  # Get the current position
    print(mPosition)
    moveY(20, relative=True)  # Move 20 units in Y relative to the current position
    moveZ(5)   # Move to Z=5 absolute
    homeXY()   # Home the X and Y axes
    