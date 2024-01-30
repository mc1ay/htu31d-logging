#!/usr/bin/env python3

"""
Reads serial output from an HTU31D sensor connected to an ESP32-C3 microcontroller running firmware from the arduino folder from the following repository:
https://github.com/mc1ay/htu31d-logging

Dependencies:
- argparse: To parse command line arguments
- csv: To write data to a CSV file
- datetime: To include timestamps in the CSV output
- re: To match the expected format of the parsed data
- serial: To communicate with the serial port
- serial.tools.list_ports: To list available serial ports

To install the dependencies:
pip3 install argparse csv serial

Author: Mitchell Clay - mclay@astate.edu
"""

import argparse
import csv
import datetime
import re
import serial
import serial.tools.list_ports

# Function to check if the input string matches the expected format after stripping the text information
def match_format(input_string):
    pattern = re.compile(r'\b\d{2}\.\d{2}, \d{2}\.\d{2}\b')
    match = pattern.match(input_string)
    return bool(match)

# Get command line options from the user
parser = argparse.ArgumentParser(description="Logging utility for serial output from an HTU31D sensor connected to an ESP32-C3")
parser.add_argument("-p", "--port", help="Serial port to read from")
parser.add_argument("-b", "--baud", help="Baud rate")
parser.add_argument("-l", "--list", help="List available serial ports", action="store_true")
parser.add_argument("-f", "--file", help="Log data to CSV file with the specified name")
parser.add_argument("-s", "--suppress", help="Suppress raw output", action="store_true")
parser.add_argument("-t", "--timestamp", help="Include timestamp in CSV output", action="store_true")
args = parser.parse_args()

# If the user specified the list option, list the available serial ports and exit
if args.list:
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(port.device)
    exit()

# If the user specified a port, use it. Otherwise, prompt the user to choose a port
if args.port:
    selected_port = args.port
else:
    # Get a list of available serial ports
    ports = serial.tools.list_ports.comports()
    # Prompt the user to choose a serial port
    print("Available serial ports:")
    for i, port in enumerate(ports, start=1):
        print(f"{i}. {port.device}")

    selection = input("Enter the number of the serial port you want to use: ")
    selected_port = ports[int(selection) - 1].device

# If the user specified a baud rate, use it. Otherwise, prompt the user to choose a baud rate
if args.baud:
    baud_rate = int(args.baud)

else:
    # Ask the user to select the baud rate
    baud_rate = input("Enter the baud rate (default is 115200): ")
    if not baud_rate:
        baud_rate = 115200
    else:
        baud_rate = int(baud_rate)

# Open the output file and write the header if the user specified a file
if args.file:
    output_file = args.file
    with open(output_file, "w", newline='') as f:
        writer = csv.writer(f)
        # if the user specified a timestamp, add it to the header
        if args.timestamp:
            writer.writerow(["Timestamp", "Temperature (C)", "Humidity (%)"])
        else:
            writer.writerow(["Temperature (C)", "Humidity (%)"])
        # Output file successfully opened message with filename
        print(f"Output file opened: {output_file}")

# Open the selected serial port
ser = serial.Serial(selected_port, baud_rate, timeout=1)

# Output serial port successfully opened message with port and baud rate
print(f"Serial port opened: {selected_port} at {baud_rate} baud")

# Read and print data from the serial port
while True:
    data = ser.readline().decode().strip()
    # Output to terminal if not suppressed
    if not args.suppress:
        print(data)
    # Strip all text except for the temperature and humidity
    data = data.replace("Temperature (C):", "").replace("Relative Humidity (%):", "")

    # Output to file if specified and data matches expected format
    if args.file:
        # Use regex to check for expected format
        if match_format(data):
            # Add timestamp to beginning of data string if specified
            if args.timestamp:
                data = f"{datetime.datetime.now()},{data}"
            with open(output_file, "a", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(data.split(","))

# Close the serial port
ser.close()

# Close the output file if it was opened
if output_file:
    f.close()