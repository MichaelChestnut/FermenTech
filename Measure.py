# URM14 functional code appropriated from https://wiki.dfrobot.com/SKU_DFR0824_RS485_Expansion_HAT_for_Raspberry_Pi
# Google sheets API code appropriated from http://www.whatimade.today/log-sensor-data-straight-to-google-sheets-from-a-raspberry-pi-zero-all-the-python-code/

from __future__ import print_function
import sys
import os
import time
import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
from Calibrate.py import initial_specific_gravity # Importing the variable from Calibrate.py
from googleapiclient.discovery import build  
from httplib2 import Http  
from oauth2client import file, client, tools  
from oauth2client.service_account import ServiceAccountCredentials  
import datetime
import random

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
MY_SPREADSHEET_ID = 'ID_HERE'

def update_sheet(sheetname, spec_grav, temperature):  
    # authentication, authorization step
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    creds = ServiceAccountCredentials.from_json_keyfile_name( 
            'FermentechKey.json', SCOPES)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API, append the next row of sensor data
    # values is the array of rows we are updating, its a single row
    values =[ [ str(datetime.datetime.now()),
            spec_grav, temperature ] ]
    body = { 'values': values }
    # call the append API to perform the operation
    result = service.spreadsheets().values().append(
                spreadsheetId=MY_SPREADSHEET_ID,
                range='!A1:C1',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body).execute()


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


  if initial_specific_gravity == 0  # User has not calibrated the sensor yet
     print("USER ERROR")
     print("Please run Calibrate.py prior to executing this script.")
     sys.exit() # Terminate the script
  
  try:
    while True:
      ser.flushInput()
      ser.baudrate = sensor_baudrate

      # Read all registers (registers 0x00 to 0x09)
#      data = master.execute(addr_sensor, cst.READ_HOLDING_REGISTERS, 0x00, 10)
#      time.sleep(3)

      # Display register values
#      print("data = ", data)

      calibrate = True
      sum = 0 # Initialize sum to 0 before loop
      previous_distance = 0 # Initialize first "measurement" to zero
      average_distance = 0 # Initialize first "measurement" to zero
      current_specific_gravity = initial_specific_gravity # Initialize current gravity to intial obtained from calibration
      
      for i in range(60):      
         #00001100 bit 3 = 1 Sets trigger bit, triggers one measurement then resets bit 3 to 0; 12 in decimal
         master.execute(sensor_address, cst.WRITE_SINGLE_REGISTER, 0x08, output_value=12)
         time.sleep(0.5) # Wait 500 ms

         # Read distance register
         distance = master.execute(sensor_address, cst.READ_HOLDING_REGISTERS, 0x05, 1)

         # Divide by 10, one LSB is 0.1mm
         distance = distance[0] / 10
         # Print distance value in mm
         #print(f"distance = {distance:.1f} mm")


        # ADD CODE TO FIlTER DISTANCE MEASUREMENTS
        # I.E IF THE MEASUREMENT IS NOT CLOSE TO THE PREVIOUS MEASUREMENT, DISREGARD IT AND DO NOT ADD INTO THE AVERAGE
        
         sum = sum + distance 

         time.sleep(0.5) # Wait 500 ms



      
      avg_distance = sum / 60 # Find the average distance

      if calibrate is True:
         first_distance = avg_distance # Record first measurement for later reference
         reference_distance = avg_distance # Record a reference distance for later use
         calibrate = False  # Set calibrate to false
      
      # Print average distance value in mm
      print(f"distance: {avg_distance:.1f} mm")

      # Read temperature register
      temp = master.execute(sensor_address, cst.READ_HOLDING_REGISTERS, 0x06, 1)

      time.sleep(0.2) # Wait 200 ms
      
      # Divide by 10, one LSB is 0.1℃
      temp =  temp / 10.0

      # Print temperature value in celsius
      print(f"internal tempreture: {temp:.1f} C") 

      # Find the difference in bobber height change i.e. (last measurement - reference measurement)
      distance_difference = previous_distance - reference_distance

      distance_difference = abs(distance_difference)

      if distance_difference > 5.0 # change was too substantail (I.E fruits were added and brew level rised)
         # Set reference distance to most recent measurement because brew level has changed, or there was an error
         reference_distance = previous_distance
         pass
        
      else if distance_difference > SOME_VALUE_DETERMINED_BY_TESTING:

        # THIS IF STATEMENT WILL FIND THE CHANGE IN SPECIFIC GRAVITY BASED ON THE CHANGE IN BOBBER DISTANCE
        current_specific_gravity = current_specific_gravity + SOME_VALUE_DETERMINED_BY_TESTING 
        
        # Set reference distance to most recent measurement because specific gravity has been updated
        reference_distance = previous_distance
      
      previous_distance = avg_distance # Set variable equal to previous distance measurement

      currentDandT = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Current date and time, Use this line for telegraf

      # Print current specific gravity value in grams per milliliter
      print("Current Specific Gravity: {current_specific_gravity:.3f} g/mL")

      update_sheet('SHEET_NAME_HERE', spec_grav, temperature)


      output = currentDandT + f",{spec_grav}" + f",{temperature}"
      print(output)

  except Exception as err:
    print(str(err))

if __name__ == "__main__":
    main()
