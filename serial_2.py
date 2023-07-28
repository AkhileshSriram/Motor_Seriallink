import time
import csv
import CastleSerialLinkControl
import math
from tkinter import Tk, Label, Entry, Button, StringVar
import threading
import os
import serial

Ki = 1
dt = 0.1
baseline_throttle = 4000
integrator = baseline_throttle

output_folder = '/Users/ruchithaprakash/Desktop'
ser = serial.Serial('/dev/tty.usbserial-A5XK3RJT', baudrate=115200, timeout=1)
new_conn = CastleSerialLinkControl.SerialLink(ser)

print(new_conn.read_var("speed"))
print(new_conn.read_var("voltage"))

error = 0
throttle_command = 0
rpm_command = 4000
collect_data = False
start_time = 0
data_buffer = []
file_name_third_component = 'default'

def update_rpm():
    global rpm_command
    rpm_command = int(rpm_entry.get())

def update_name():
    global file_name_third_component
    file_name_third_component = str(name_entry.get())

def start_collecting():
    global collect_data, start_time
    collect_data = True
    start_time = time.time()

def stop_collecting():
    global collect_data, rpm_command, data_buffer, file_name_third_component
    collect_data = False
    output_file_name = f'testdata_{rpm_command}_{file_name_third_component}_{int(time.time())}.csv'
    output_path = os.path.join(output_folder, output_file_name)
    with open(output_path, 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(['Timestamp', 'RPM', 'Throttle'])
        for row in data_buffer:
            writer.writerow(row)
    data_buffer.clear()  

def control_loop():
    global error, throttle_command, integrator
    try:
        while True:
            current_rpm = new_conn.read_var("speed") / 2
            print(f"RPM: {current_rpm}")
            error = rpm_command - current_rpm
            integrator += error * Ki * dt
            throttle_command = math.floor(integrator)

            if collect_data:
                elapsed_time = int(time.time() - start_time)
                data_buffer.append([elapsed_time, current_rpm, throttle_command])

            print(f"Throttle: {throttle_command}")
            new_conn.write_var("write throttle", throttle_command)
            time.sleep(dt)

        time.sleep(5)
    finally:
        new_conn.write_var("write throttle", 0)

def create_gui():
    global rpm_entry, name_entry, data_buffer
    root = Tk()
    root.geometry("400x300")  
    rpm_label = Label(root, text="RPM Command")
    rpm_label.pack()
    rpm_entry = Entry(root)
    rpm_entry.pack()
    rpm_entry.insert(0, "7000")
    rpm_button = Button(root, text="Update RPM", command=update_rpm)
    rpm_button.pack()

    name_label = Label(root, text="File Name Third Component")
    name_label.pack()
    name_entry = Entry(root)
    name_entry.pack()
    name_entry.insert(0, "default")
    name_button = Button(root, text="Update Name", command=update_name)
    name_button.pack()

    collect_button = Button(root, text="Collect Data", command=start_collecting)
    collect_button.pack()
    stop_collect_button = Button(root, text="Stop Collecting", command=stop_collecting)
    stop_collect_button.pack()

    elapsed_time_label = Label(root, text="")
    elapsed_time_label.pack()

    data_buffer = []

    def update_elapsed_time():
        if collect_data:
            elapsed_time = int(time.time() - start_time)
            elapsed_time_label.config(text=f"Elapsed Time: {elapsed_time} seconds")
        root.after(1000, update_elapsed_time)

    update_elapsed_time()
    root.mainloop()

control_thread = threading.Thread(target=control_loop)
control_thread.start()

create_gui()