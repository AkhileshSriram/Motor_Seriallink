import serial
import time
import CastleSerialLinkControl
# import simple_pid as sp
import math

rpm_command = 2000
# pid = sp.PID(Kp=0, Ki=0.1, Kd=0, setpoint=rpm_command)
Ki = 0.05
dt = 0.01
baseline_throttle = 4000
integrator = baseline_throttle

try:
    ser = serial.Serial('/dev/tty.usbserial-A5XK3RJT', baudrate=115200, timeout=1)
    new_conn = CastleSerialLinkControl.SerialLink(ser, device_id=1)
    # new_conn_1 = CastleSerialLinkControl.SerialLink(ser, device_id=1)
    # new_conn_2 = CastleSerialLinkControl.SerialLink(ser, device_id=2)
    # print(new_conn.write_var("write throttle", 5000))
    # time.sleep(10)
    print(new_conn.read_var("speed"))
    # time.sleep(1)
    print(new_conn.read_var("voltage"))

    error = rpm_command
    throttle_command = 10000

    # while math.fabs(error) > 50
    while True:
        current_rpm = new_conn.read_var("speed") / 2
        print(f"RPM: {current_rpm}")
        error = rpm_command - current_rpm
        integrator += error*Ki*dt
        throttle_command = math.floor(integrator)
        print(f"Throttle: {throttle_command}")
        new_conn.write_var("write throttle", throttle_command)
        # new_conn_1.write_var("write throttle", throttle_command)
        # new_conn_2.write_var("write throttle", throttle_command)
        time.sleep(dt)
    
    time.sleep(5)


finally:
    print(new_conn.write_var("write throttle", 0))

# def control_throttle()