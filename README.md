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

## Wiring Schematic


<img width="785" alt="Screen Shot 2024-02-27 at 11 08 19 AM" src="https://github.com/MichaelChestnut/FermenTech/assets/72172361/287015cc-f51c-48b5-af59-3d350bb9bc22">



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

- Install the GPIO package:
   - On Raspbian: 
   ```
   sudo apt-get install rpi.gpio
   ```
   - On Ubuntu: 
   ```
   sudo apt install python3-lgpio
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

After installing dependencies: 

- Clone this repo to get necessary files: 
```
git clone https://github.com/MichaelChestnut/FermenTech.git
```
- Change into FermenTech directory: 
```
cd FermenTech
```
- Verify that permissions are set so that the script is executable by running: 
```
chmod +x Calibrate.py
```
```
chmod +x Measure.py
```

- Execute the script:
```
python3 Measure.py
```

- Done!




## Implementing The Script as a Service

- Create a systemd entry


  - Change into Systemctl directory: 
      ```
      cd FermenTech/Systemctl
      ``` 
   - Copy the .service file to correct location: 
      ```
      sudo cp FermenTech.service /etc/systemd/system
      ```
  - Modify Measure.sh to include the correct paths (located inside of the Systemctl directory): 
  ```
  nano FermenTech.sh
  ```
  - Set file permissions for Measure.sh: 
  ```
  sudo chmod 744 FermenTech/Systemctl/FermenTech.sh
  ```
  - If previous step is unsuccessful, here are potential solutions:
     - Change permissions further: 
     ```
     sudo chmod 755 FermenTech/Systemctl/FermenTech.sh
     ```
     - Change permissions for the directory as well: 
     ```
     sudo chmod 755 FermenTech
     ```
  - Enable the service: 
      ```
      sudo systemctl daemon-reload
      ```
      ```
      sudo systemctl enable FermenTech.service
      ```
      
  - Start the service: 
  ```
  sudo systemctl start FermenTech.service
  ```
  
  - Check the status of the service: 
  ```
  sudo systemctl status FermenTech.service
  ```
  
  - Done! The service should now run on boot. 


## Common Errors





## Notes
