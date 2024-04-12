#! /usr/bin/python

# URM14 functional code appropriated from https://wiki.dfrobot.com/SKU_DFR0824_RS485_Expansion_HAT_for_Raspberry_Pi
# Google sheets API code appropriated from http://www.whatimade.today/log-sensor-data-straight-to-google-sheets-from-a-raspberry-pi-zero-all-the-python-code/

from __future__ import print_function
import sys
import os
import time
import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import datetime
import random
import yaml

sensor_address = 0x0C # Sensor address is 0x0C which is 12 in decimal
#print(f"sensor_address: {sensor_address}")
control_register = 0x08 # Control register address is 0x08 which is 8 in decimal
#print(f"control_register: {control_register}")

# 00000100 bit 2 = 1 Sets measure mode bit (passive detection) ; 4 in decimal
# 00000000 bit 0 = 0 Selects internal temperature compensation
# 00000000 bit 1 = 0 enables temperature compensation function
sensor_baudrate = 19200

# Define serial port settings
serial_port = '/dev/ttyS0'  # Serial port on Raspberry Pi; UART pins on GPIO
baudrate = 19200 # 19200 baud rate
bytesize = serial.EIGHTBITS # 8 bit byte size
parity = serial.PARITY_NONE # no parity bit
stopbits = serial.STOPBITS_ONE # One stop bit

# Initialize serial connection
ser = serial.Serial(port=serial_port,
                    baudrate=baudrate,
                    bytesize=bytesize,
                    parity=parity,
                    stopbits=stopbits)

# Google spreadsheet ID, can be found in google sheet URL: https://docs.google.com/spreadsheets/d/SPREADSHEETID/edit#gid=0
MY_SPREADSHEET_ID = '19bpbvqJYwY_Cslh-34vE48LasRu3WjDB2dd8Y_JoiOY'

def update_sheet(sheetname, spec_grav, temperature, avg_dist):
    # authentication, authorization step
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    creds = ServiceAccountCredentials.from_json_keyfile_name(
            '/opt/FermenTech/FermentechKey.json', SCOPES)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API, append the next row of sensor data
    # values is the array of rows we are updating, its a single row
    values =[ [ str(datetime.datetime.now()),
            spec_grav, temperature, avg_dist ] ]
    body = { 'values': values }
    # call the append API to perform the operation
    result = service.spreadsheets().values().append(
                spreadsheetId=MY_SPREADSHEET_ID,
                range='!A1:D1',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body).execute()


# Globalize config variable so specific gravity can be updated throughout script
global config

# Load the YAML file
with open('/opt/FermenTech/Calibrate.yaml', 'r') as file:
   config = yaml.safe_load(file)

# Globalize variable
global specific_gravity

# Import variable from config file
initial_specific_gravity = config['specific_gravity']


def main():
  master = modbus_rtu.RtuMaster(ser) # create modbus_rtu client based on serial connection
  master.set_timeout(5.0)  # Timeout after 5 seconds
  master.set_verbose(True)
  #print("ser.name = ", ser.name)

  # Control register default value; 0x04 is 4
  crval = 0x04

  # Write default value (0x04) to control register
  master.execute(sensor_address, cst.WRITE_SINGLE_REGISTER, 0x08, output_value=crval)
  time.sleep(0.1) # Wait 100 ms


  # Import variable from config file
  initial_specific_gravity = config['specific_gravity']

  if initial_specific_gravity == 0:  # User has not calibrated the sensor yet
     print("Please follow these steps to calibrate the FermenTech digital hydrometer.")
     print("A physical hydrometer is necessary to calibrate this sensor")
     print("Insert the physical hydrometer into the brew")
     print("Read the hydrometer scale at the lowest point of the liquid's surface")
     print("Please input the physical hydrometer reading to three decimal places (example: 1.000)")
     print("\n")
     initial_specific_gravity = float(input("Input reading now: "))
     # Update the specific_gravity variable in calibrate file
     config['specific_gravity'] = initial_specific_gravity
     # Save the updated configuration back to the file
     with open('Calibrate.yaml', 'w') as file:
        yaml.dump(config, file)

  previous_distance = 0 # Initialize first "measurement" to zero
  average_distance = 0 # Initialize first "measurement" to zero
  current_specific_gravity = initial_specific_gravity # Initialize current gravity to intial obtained from calibration
  calibrate = True

  try:
    while True:
      ser.flushInput()
      ser.baudrate = sensor_baudrate

      # Read all registers (registers 0x00 to 0x09)
#      data = master.execute(addr_sensor, cst.READ_HOLDING_REGISTERS, 0x00, 10)
#      time.sleep(3)

      # Display register values
#      print("data = ", data)

      sum = 0 # Initialize sum to 0 before loop
      ignored_count = 0 # Initialize to zero
      ignore_sum = 0 # Initialize to zero
      num_measurements = 60 # Target measurements is 60
      last_measurement = 0 # Initialize to zero
      initial_measurement = 0 # Initialize to zero
      average_distance = 0 # Initialize first "measurement" to zero


      for i in range(num_measurements):
         #00001100 bit 3 = 1 Sets trigger bit, triggers one measurement then resets bit 3 to 0; 12 in decimal
         master.execute(sensor_address, cst.WRITE_SINGLE_REGISTER, 0x08, output_value=12)
         time.sleep(0.5) # Wait 500 ms

         # Read distance register
         distance = master.execute(sensor_address, cst.READ_HOLDING_REGISTERS, 0x05, 1)

         # Divide by 10, one LSB is 0.1mm
         distance = distance[0] / 10
         # Print distance value in mm
         #print(f"distance = {distance:.1f} mm")

         if initial_measurement == 0:
#           print(f"initial measurement: {initial_measurement}")     # FOR DEBUGGING
           initial_measurement = distance # Set initial measurement for data filtering


# FOR DEBUGGING
#         print(f"initial measurement: {initial_measurement}")
#         print(f"recent distance mesurement: {distance}")
#         print(f"DATA FILTERING PREV_AVG - MOST RECENT MEASUREMENT: ")
#         print(abs(initial_measurement - distance))

         # FIlTER DISTANCE MEASUREMENTS
         if last_measurement == 0:
            sum = sum + distance

         elif abs(initial_measurement - distance) >= 5: # IF THE MEASUREMENT IS NOT CLOSE TO THE PREVIOUS MEASUREMENT, DISREGARD IT AND DO NOT ADD INTO THE AVERAGE
            num_measurements = num_measurements - 1 # Decrement num measurements
            ignored_count = ignored_count + 1 # Incremenmt ignore count
            ignore_sum = ignore_sum + distance # sum ignored values for an ignored average

         else:
            sum = sum + distance

         last_measurement = distance

# FOR DEBUGGING
#         print(f"initial measurement: {initial_measurement}")
#         print(f"recent distance mesurement: {distance}")
#         print(f"last measurement: {last_measurement}")
#         print(f"number of mesurements: {num_measurements}")
#         print(f"ignored_count: {ignored_count}")
#         print(f"ignored sum: {ignore_sum}")
#         print("")
#         print("")
#         print("")


         time.sleep(0.5) # Wait 500 ms


      if ignored_count > 10:
         avg_distance = ignore_sum / ignored_count # Set average distance to ignored measurement, since they are the majority and correct

      else:
         avg_distance = sum / num_measurements # Find the average distance using normal measurements


#      print(f"average distance after testing ignore count: {avg_distance}")  # FOR DEBUGGING


      if calibrate is True:
         first_distance = avg_distance # Record first measurement for later reference
         reference_distance = avg_distance # Record a reference distance for later use
         previous_distance = avg_distance # make previous distance equal to first measurment to prevent error
         calibrate = False  # Set calibrate to false

      # Print average distance value in mm
#      print(f"distance: {avg_distance:.1f} mm")   # FOR DEBUGGING

      # Read temperature register
      temperature = master.execute(sensor_address, cst.READ_HOLDING_REGISTERS, 0x06, 1)

      time.sleep(0.2) # Wait 200 ms

      temp = temperature[0]
      # Divide by 10, one LSB is 0.1℃
      temp =  temp / 10.0

      # Print temperature value in celsius
#      print(f"internal tempreture: {temp:.1f} C")   # FOR DEBUGGING

      if ignored_count > 10:
         pass # Do not update previous_distance variable because the avg_distance variable contains bad data

      else:
         previous_distance = avg_distance # Set variable equal to previous distance measurement


      # Find the difference in bobber height change i.e. (last measurement - reference measurement)
      distance_difference = previous_distance - reference_distance

      if abs(distance_difference) > 5.0: # change was too substantail (I.E fruits were added and brew level rised)
         # Set reference distance to most recent measurement because brew level has changed, or there was an error
         reference_distance = previous_distance
         pass

      elif abs(distance_difference) >= 0.5:

         change_in_spec_grav = .002831 * abs(distance_difference)

#         print(f"Change in spec grav value: {change_in_spec_grav}")

         if (distance_difference < 0):
            # THIS IF STATEMENT WILL FIND THE CHANGE IN SPECIFIC GRAVITY BASED ON THE CHANGE IN BOBBER DISTANCE
            current_specific_gravity = current_specific_gravity + change_in_spec_grav

         if (distance_difference > 0):
            # THIS IF STATEMENT WILL FIND THE CHANGE IN SPECIFIC GRAVITY BASED ON THE CHANGE IN BOBBER DISTANCE
            current_specific_gravity = current_specific_gravity - change_in_spec_grav

         # Update the specific_gravity variable in calibrate file
         config['specific_gravity'] = current_specific_gravity
         # Save the updated configuration back to the file
         with open('Calibrate.yaml', 'w') as file:
            yaml.dump(config, file)


         # Set reference distance to most recent measurement because specific gravity has been updated
         # do not use average_distance because it may contain a mix of brew level measurements before and after fruits are added
         reference_distance = previous_distance

      else:
         pass


      currentDandT = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Current date and time, Use this line for telegraf

      # Print current specific gravity value in grams per milliliter
#      print(f"Current Specific Gravity: {current_specific_gravity} g/mL")   # FOR DEBUGGING

      update_sheet('FermenTech', current_specific_gravity, temp, avg_distance)

      current_specific_gravity = float(current_specific_gravity)
      temp = float(temp)

      output = currentDandT + f",{current_specific_gravity}" + f",{temp}"
      print(output)

      # Flush the standard output buffer
      sys.stdout.flush()

# FOR DEBUGGING:
#      print(f"reference distance: {reference_distance}")
#      print(f"previous distance: {previous_distance}")
#      print(f"average distance: {avg_distance}")
#      print("")
#      print("")
#      print("")
#      print("")


  except Exception as err:
    print(str(err))

if __name__ == "__main__":
    main()
