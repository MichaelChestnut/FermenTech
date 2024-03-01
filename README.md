# FermenTech Specific Gravity Sensor


## Components

***RASPBERRY PI 4:***

   Used to run power monitoring python script
   
   
   
***RS485 CAN HAT:***

   Used to facilitate UART to RS485 conversion
  
  

***URM14 Ultrasonic Sensor:***

   Sensor to gather distance and temperature measurements


***BOCHEN 3296:***

   Voltage booster to converse pi4's 5v output to a suitable 7v-15v for the URM14 



# Using The Sensor


## Dependencies

- Install pyserial: 
```
sudo pip3 install pyserial 
```

- Install modbus-tk:
```
sudo pip3 install modbus-tk 
```




## Calibrating The Sensor
- Execute calibration script:
```
python3 Calibrate.py 
```

- Follow instructions provided by script

- Tip for reading hydrometer:

   ![image](https://github.com/MichaelChestnut/FermenTech/assets/72172361/54cb42fd-aea1-44ee-85d8-aa68b97ad962)




## Running With Python





## Implementing The Script as a Service





## Common Errors





## Notes
