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

## Schematic


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





## Telegraf




## Grafana

Listed below are steps to begin setting up a dashboard to display the data from the influxDB database. For official instructions, refer to the documenation here: https://grafana.com/docs/grafana/latest/

1. Open a browser and access port 3000 of the device that the database and Grafana instance are running on
   <img width="413" alt="Screen Shot 2023-05-22 at 1 47 13 PM" src="https://github.com/NAU-IoT/CSVtoSQL/assets/72172361/6a7c722f-6b13-4bf4-a1e6-6994bcdc0bbb">
   
2. Navigate to the "Add Data Source" page and add InfluxDB
   <img width="1006" alt="Screen Shot 2024-03-20 at 1 35 44 PM" src="https://github.com/MichaelChestnut/FermenTech/assets/72172361/948a8666-9a43-4dc8-a0aa-d5ddc8a2874b">


3. Fill out necessary fields, scroll to the bottom and click "Save and Test"

   <img width="311" alt="Screen Shot 2024-03-20 at 1 38 08 PM" src="https://github.com/MichaelChestnut/FermenTech/assets/72172361/af99b935-34bb-4c5c-ac03-822e2bfa4289">

5. Back on the home page, click the plus and select "New dashboard" from the dropdown menu and select "New visualization"
   <img width="1390" alt="Screen Shot 2023-05-22 at 2 04 33 PM" src="https://github.com/NAU-IoT/CSVtoSQL/assets/72172361/a5e07160-cab1-4928-9dbc-838829a5bfa6">

6.
   1) Select type of visualization. This example is comparing Power Consumption of a load against time using MySQL, but you will use flux instead.
   2) Switch from builder to code under the query section.
   3) Next, write your query.
   4) Next, hit run query.
   5) Finally, if you are satisfied with the look of your graph, click Apply.
   <img width="1361" alt="Screen Shot 2023-05-22 at 2 07 56 PM" src="https://github.com/NAU-IoT/CSVtoSQL/assets/72172361/ac0704a6-fa4c-4b92-be9d-83d15012e10a">



