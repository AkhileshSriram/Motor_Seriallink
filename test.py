import time
import serial
from simple_pid import PID
import CastleSerialLinkControl
import math

# PID parameters
Kp = 1.0 
Ki = 0.1 
Kd = 0.5  

# Setpoint (desired RPM)
desired_rpm = 2000

pid = PID(Kp, Ki, Kd, setpoint=desired_rpm)

# Connect to the ESC
ser = serial.Serial('/dev/tty.usbserial-A5XK3RJT', baudrate=115200, timeout=1)
new_conn = CastleSerialLinkControl.SerialLink(ser, device_id=1)

# Initial throttle setting
throttle = 4000
print(new_conn.write_var("write throttle", throttle))
time.sleep(5)

while True:
    # Read the current RPM from the ESC
    current_rpm = new_conn.read_var("speed")
    print(f"Current RPM: {current_rpm}")

    # Update the PID controller with the current RPM and get the control output
    control_output = math.floor(pid(current_rpm))

    # Adjust the throttle based on the control output
    throttle = control_output
    throttle = max(0, min(throttle, 60000))  
    print(f"Current throttle: {throttle}")

    # Write the adjusted throttle setting to the ESC
    print(new_conn.write_var("write throttle", throttle))


    time.sleep(0.5)

# Stop the motor
print(new_conn.write_var("write throttle", 0))
