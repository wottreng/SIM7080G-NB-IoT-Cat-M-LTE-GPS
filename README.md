# SIM7080G-NB-IoT-Cat-M-LTE-GPS
Project repository for working with SIM7080G Multi-Band CAT-M and NB-IoT module

documentation and references: \
https://www.simcom.com/product/SIM7080G.html
https://www.waveshare.com/wiki/SIM7080G_Cat-M/NB-IoT_HAT
https://www.techstudio.design/getting-started-with-techstudio-sim7080-development-board/
http://www.spotpear.com/index/study/detail/id/241.html
https://github.com/vshymanskyy/TinyGSM/issues/592
https://github.com/tmcadam/sim7000-tools

Hardware: \
sim7080g module: https://amzn.to/3Lz5Kg9 \
IOT sim card: https://amzn.to/3GRQOWZ \
5v battery pack: https://amzn.to/3oTOAjL \
rpi zero W: https://amzn.to/3oSA6jV
- - - -
![sim module](https://github.com/wottreng/SIM7080G-NB-IoT-Cat-M-LTE-GPS/blob/main/pics/SIM7080G-Cat-M-NB-IoT-HAT-rpi.jpg)
![prototype](https://github.com/wottreng/SIM7080G-NB-IoT-Cat-M-LTE-GPS/blob/main/pics/prototype_v1.jpg)
## RPI SETUP:
* add `gpio_init.sh` (in ref folder) to RPI `/bin`
* add command `/bin/gpio_init.sh &` to RPI `/etc/rc.local`
* this will set power pin low and turn off SIM7080G hat

## ON FIRST BOOT:
* SIM7080G module is auto baud so send AT commands at 115200 baud until it responds
* set baud rate for sim7080g: `AT+IPR=115200`

## FOR HTTPS request:
* ssl cert can be loaded into flash on sim7080G module (to verify ssl server) or you can run unverified
* see `/libs/tools/certs/READ_ME_certs.txt` for information on how to load cert into module

## How to run:
* download this repository onto rpi that is connected to sim7080g module
    * wget https://github.com/wottreng/SIM7080G-NB-IoT-Cat-M-LTE-GPS/archive/refs/heads/main.zip
* edit /libs/config_template.py and save as config.py in lib directory
    * `mv ./libs/config_template.py ./libs/config.py && nano ./libs/config.py`
* create python virtual environment
    * `python3 -m venv venv`
* install required packages into virtual environment
    * `./venv/bin/pip3 install -r requirements.txt`
* run main script
    * `./venv/bin/python3 main.py` 

## NOTES
* GPS/GNSS and cellular can not be used together. Causes module to hang and be unresponsive
  * make sure to turn off network activity then use GPS/GNSS then turn network back on and use Data functions
* Module can be very finiky so lots of error handling is necessary 

- - - -
![module connections](https://github.com/wottreng/SIM7080G-NB-IoT-Cat-M-LTE-GPS/blob/main/pics/SIM7080G_Cat-M_NB-IoT_HAT.jpg)

Connections: 

| usbToUART | SIM7080G |
|-----------|----------|
| VCC       | 5v       |
| GND       | GND      |
| TX        | TX       |
| RX        | RX       |

or
    
| rpi Zero W | SIM7080G  |
|------------|-----------|
| GPIO 4     | P7 {PWR}  |
| Tx         | RX {UART} |
| Rx         | TX {UART} |
| GND        | GND       |
| 5v         | 5v        |

Notes: \
SIM7080G uart jumper on VCC to 3V3 {rpi zero UART is 3.3v only} \
SIM7080G jumper on PWR to P7 
----
Cheers,
Mark
