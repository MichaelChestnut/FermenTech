# code appropriated from https://wiki.dfrobot.com/SKU_DFR0824_RS485_Expansion_HAT_for_Raspberry_Pi

from __future__ import print_function
import sys
import os
import time
import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

# Sensor address is 0x0C which is 12 in decimal
sensor_address = 0x0C
#print(f"sensor_address: {sensor_address}")

# Control register address is 0x08 which is 8 in decimal
control_register = 0x08
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

  try:
    while True:
      ser.flushInput()
      ser.baudrate = sensor_baudrate

      # Read all registers (registers 0x00 to 0x09)
#      data = master.execute(addr_sensor, cst.READ_HOLDING_REGISTERS, 0x00, 10)
#      time.sleep(3)

      # Display register values
#      print("data = ", data)

      #00001100 bit 3 = 1 Sets trigger bit, triggers one measurement then resets bit 3 to 0; 12 in decimal
      master.execute(sensor_address, cst.WRITE_SINGLE_REGISTER, 0x08, output_value=12)
      time.sleep(0.5) # Wait 500 ms

      # Read distance register
      distance = master.execute(sensor_address, cst.READ_HOLDING_REGISTERS, 0x05, 1)

      # Divide by 10, one LSB is 0.1mm
      distance = distance[0] / 10

      # Print distance value in mm
      print(f"distance = {distance:.1f} mm")

      time.sleep(5) # Wait 5 seconds

  except Exception as err:
    print(str(err))

if __name__ == "__main__":
    main()
