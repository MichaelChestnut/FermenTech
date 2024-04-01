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

- Telegraf installation:
```
curl -s https://repos.influxdata.com/influxdata-archive_compat.key > influxdata-archive_compat.key
```
```
echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
```
```
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
```
```
sudo apt-get update && sudo apt-get install telegraf
```

- For telegraf to work, data must be printed to Standard Output

- Move directory into /opt:
```
Sudo mv <directory> /opt
```
- To generate Telegraf config file:
- There is an example configuration file located in this repository, but here are steps to generate a new one. This is required as you need a unique key for each instance data transfer on a host. 
   - Access telegraf on device through a web search bar, Telegraf on port 8086
   - example: device_DNS_or_IPaddress:8086
- Select exec source 
- Generate config file
- Take generated token and place in config file on machine under test
- Put config file in /etc/telegraf/telegraf.d/CONFIG_NAME.conf
- Test telegraph user: sudo -u telegraf /opt/YOUR_DIRECTORY/YOUR_EXECUTABLE.sh 
- If error: serial.serialutil.SerialException: [Errno 13] could not open port /dev/ttyUSB0: [Errno 13] Permission denied: '/dev/ttyUSB0'
   - Use command:
  ```
  sudo usermod -aG dialout telegraf
  ```
  
- To give telegraf i2c permissions:
  ```
  sudo groupadd i2c
  ```
  ```
  sudo chown :i2c /dev/i2c-1
  ```
  ```
  sudo chmod g+rw /dev/i2c-1
  ```
  ```
  sudo usermod -aG i2c telegraf
  ```

- Enable telegraf service:
```
sudo systemctl enable telegraf
```
- Start telegraf service:
```
sudo systemctl start telegraf
```
- Check telegraf status:
```
sudo systemctl status telegraf
```


## Using Grafana to display data

NOTES: 
 - These instructions use ubuntu installation, for other OS, refer to https://grafana.com/docs/grafana/latest/setup-grafana/installation/ 
 - These instructions assume you are installing grafana on the same device on which the database is located

STEPS:
- Install required packages 
```
sudo apt-get install -y apt-transport-https software-properties-common wget
```
- Download the Grafana repository signing key 
```
sudo wget -q -O /usr/share/keyrings/grafana.key https://apt.grafana.com/gpg.key
```
- Add a repository for stable releases: 
```
echo "deb [signed-by=/usr/share/keyrings/grafana.key] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
```
- Update the list of available packages: 
```
sudo apt-get update
```
- Install the latest OSS release: 
```
sudo apt-get install grafana
```
- Enable the Grafana service to run on boot: 
```
sudo systemctl enable grafana-server.service
```
- Start the Grafana service: 
```
sudo systemctl start grafana-server.service
```
- Check the status of the Grafana service to ensure it is running: 
```
sudo systemctl status grafana-server.service
```

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


## Google Sheets





