**One-line purpose:** instruction for the team
**Short summary:** Step-by-step deployment for the base station build. 
**Agent:** use this as current `_hardware_stack`. Do not change anything about this page. 

---

Update: 29-01-2026

Base station – Vision AI detection

The Vespa Smart Trap (VST) is a development project to detect, catch and kill Asian or Yellow Legged Hornets (_Vespa velutina_) and comprises multiple build. The first part is base station for Vision AI detection and designed to facilitate easy-to-deploy, following the principles of plug & play. That means that there is no craftwork like soldering, programming or other engineering required. It is solely based on off-the-shelf available modules from Seeed and web-based software deployment.

The VST project will deliver in a later stage the physical casing for the entrapment. The project end with a PRO versions extending the build with a solar power and LTE-M communications unit, capable of sending SMS and IoT messaging and photo uploads for machine learning.

**Base station modules**

The base station exist of three principal components and a couple of free to choose options:

-              Raspberry Camera V1.3 module, equipped with OV2640 camera

-              _Seeed Grove Vision AI V2_ microcomputer highly optimized for image recognition

-              XIAO-ESP32S3 microcomputer, plugged into a Seeed Studio Grove expansion board

![Afbeelding met elektronica, tekst, stroomkring, Elektronisch onderdeel
Door AI gegenereerde inhoud is mogelijk onjuist.](file:////Users/md/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image001.jpg)

Next there is a choice of actuators, making it possible performing specific actions, like:

-              Seeed Grove Relay v1.2, giving a 250V/10A contact, up to 3 relays, or

-              Seeed Grove LED, acting a warning signal, up to 3 LED (to be combined with relays), and

-              Seeed Grove Mini I2C Motor Driver, to activate two 2 3V DC motors or 1 2-channel bipolar stepper motor.

Build the stack of components with Grove connector cables. You can fix the modules with 2mm screws or with Grove Wrappers 1x2, allowing more flexibility.  In the picture only 1 output port is wired to a relay and the red LED.

|   |
|---|
|**Tech talk for experts**<br><br>The detection is based on Artificial Intelligence, existing of a tiny Yolo machine learning model, which runs autonomous on the modules, without the need of internet. The model runs on a Seeed Grove Vision AI V2 module on standard firmware from SenseCraft AI. It communicates over UART protocol to an XIAO-ESP32S3 Micro Compute Unit. Both MCU use Arduino based software, catering for the use of SSCMA library of SenseCraft, and ESP-S3 libraries of Espressif.<br><br>The expansion board offers next to the UART connector, 4 hard wired GPIO pins and 2 I2C connectors. These can be used to connect the optional modules as well as provide the communication in the PRO version for LTE-M (SMS/Web), GPS positioning.<br><br>For expert programmer, more options are available, like:<br><br>-               4 programmable hard wired GPIO ports<br><br>-              1 port I2C allowing expert programmers to connect to any I2C hub or device at choice|

**Deployment of software**

The software is available through GNU public license. For the VST Base station there are 2 parts for which you find the instructions below:

_Vision AI module_

1.         Plug the Vision AI in your computer, using an USB-C cable

2.         Surf to [**https://sensecraftai.com**](https://sensecraftai.com), account creation id not required

3.         Search for a model **Vespa velutina** and click **deploy model**

4.         Click **connect** and choose the available COM port

5.         Click deploy and wait a couple of minutes. After a while you should see camera images  
  
![Afbeelding met tekst, elektronica, computer, schermopname
Door AI gegenereerde inhoud is mogelijk onjuist.](file:////Users/md/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image002.png)  
  

6.         When you point the camera to a picture of a Vespa velutina wasp, you should see recognition.

7.         Optionally you can modify the Output options to light the onboard LED when the recognition of Vespa velutina, Vespa Crabro of Apis mellifera reaches a threshold you can set.

_XIAO ESP32S3_

1.         Place in the XIAO ESP32S3 MCU in the Seeed Studio Grove expander for XIAO

2.         Plug the XIAO EPS32S3 in your computer, using an USB-C cable

3.         Download the [ZIP file](https://github.com/aggerritsen/VespaSmartTrap-ONE/archive/refs/heads/main.zip) from: [https://github.com/aggerritsen/VespaSmartTrap-ONE/](https://github.com/aggerritsen/VespaSmartTrap-ONE/)

4.         Surf to [https://espressif.github.io/esptool-js/](https://espressif.github.io/esptool-js/)

5.         Click **connect** and choose the available COM port (Optional click **Erase Flash**)

6.         Fill out the correct **Flash Address** and select the downloaded files using **Choose File,** click **Add program** to complete all files form this list:  
  

|   |   |
|---|---|
|Flash Address|Program files|
|0x00000000|bootloader.bin|
|0x00008000|partitions.bin|
|0x00010000|firmware.bin|

  
  
![Afbeelding met tekst, schermopname, software, Webpagina
Door AI gegenereerde inhoud is mogelijk onjuist.](file:////Users/md/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image003.png)  
  

7.         Click **Program** to upload the files, wait a few moments to complete.  

**Monitoring**

When the USB-C cable is connected between the XIAO ESP32-S3 and the computer, the serial output can be monitored using a serial console like Putty:

·       Select the correct COM4 port

·       Set baudrate to 961200

·       Make sure to set **Implicit CR in every LF** in the **Terminal** options

![Afbeelding met tekst, schermopname, software, scherm
Door AI gegenereerde inhoud is mogelijk onjuist.](file:////Users/md/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image004.png) 

![Afbeelding met tekst, elektronica, schermopname, software
Door AI gegenereerde inhoud is mogelijk onjuist.](file:////Users/md/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image005.png)![Afbeelding met tekst, elektronica, schermopname, software
Door AI gegenereerde inhoud is mogelijk onjuist.](file:////Users/md/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image006.png) 

Currently this is the output in development stage, awaiting the next development stage for casing and the PRO version.

  

**Bill of materials**

_Required materials_

|   |   |   |   |
|---|---|---|---|
|**Number**|**Name**|**URL**|**Unit Price**|
|1|Raspberry Camera V1.3|https://www.tinytronics.nl/nl/sensoren/optisch/camera's-en-scanners/raspberry-pi-compatible-camera-5mp-v1.3|€ 8,00|
|1|Grove Vision AI V2|[https://www.kiwi-electronics.com/nl/grove-vision-ai-module-v2-20039](https://www.kiwi-electronics.com/nl/grove-vision-ai-module-v2-20039)|€ 18,74|
|1|XIAO-EPS32-S3|https://www.tinytronics.nl/nl/development-boards/microcontroller-boards/met-wi-fi/seeed-studio-xiao-esp32-s3|€ 9,00|
|1|Grove shield for XIAO|[https://www.tinytronics.nl/nl/development-boards/accessoires/adapter-boards/seeed-studio-grove-shield-voor-seeeduino-xiao](https://www.tinytronics.nl/nl/development-boards/accessoires/adapter-boards/seeed-studio-grove-shield-voor-seeeduino-xiao)<br><br>https://www.kiwi-electronics.com/nl/grove-shield-voor-seeeduino-xiao-met-accu-management-10097|€ 6,00<br><br>€ 5,07|
|1|Grove cable|https://www.tinytronics.nl/nl/kabels-en-connectoren/kabels-en-adapters/grove-compatible/grove-female-compatible-kabel-0.2mm2-4p-10cm|€ 0,80|
|**Total**|||**€ 42,54**|

_  
Optional materials_

|   |   |   |   |
|---|---|---|---|
|**Number**|**Name**|**URL**|**Unit Price**|
|1…3|Grove Relay V1.3|[https://www.kiwi-electronics.com/nl/grove-relais-1896](https://www.kiwi-electronics.com/nl/grove-relais-1896)|€ 3,13|
|1…3|Grove LED Socket R/G/B/Y  <br>(LED uitwisselbaar)|[https://www.kiwi-electronics.com/nl/grove-led-groen-5mm-241](https://www.kiwi-electronics.com/nl/grove-led-groen-5mm-241)  <br>[https://www.kiwi-electronics.com/nl/grove-led-rood-5mm-2746](https://www.kiwi-electronics.com/nl/grove-led-rood-5mm-2746)  <br>https://www.kiwi-electronics.com/nl/grove-led-blauw-5mm-2392|€ 2,29|
|1|Grove Mini I2C motor driver|[https://www.kiwi-electronics.com/nl/grove-i2c-mini-motor-driver-2378](https://www.kiwi-electronics.com/nl/grove-i2c-mini-motor-driver-2378)|€ 13,06|
|1|Grove 6-DIP switch|[https://wiki.seeedstudio.com/Grove-6-Position_DIP_Switch](https://wiki.seeedstudio.com/Grove-6-Position_DIP_Switch)  (Kiwi: SS-111020043 Grove - 6-Position DIP Switch)|€ 5,99|
|1|Grove I2C hub|[https://www.kiwi-electronics.com/nl/grove-i2c-hub-6-port-9908](https://www.kiwi-electronics.com/nl/grove-i2c-hub-6-port-9908)|€ 1,92|
|1…6|Grove cables|https://www.tinytronics.nl/nl/kabels-en-connectoren/kabels-en-adapters/grove-compatible/grove-female-compatible-kabel-0.2mm2-4p-10cm|€ 0,80|
|1|Mini camera holder|https://www.amazon.nl/dp/B0D5XY52SG|€5.57  (3x)|
|1|Grove wrapper 1x1|https://www.kiwi-electronics.com/nl/grove-yellow-wrapper-1x1-4-pack-2408|€ 2,53|
|1…2|Grove wrapper 1x2|https://www.kiwi-electronics.com/nl/grove-yellow-wrapper-1x2-4-pack-2235|€ 2,53|
||M2 nuts and bolts|https://www.amazon.nl/-/en/dp/B0D49DZS8Q|€ 7,00|
|2|Kabel voor motor|https://www.kiwi-electronics.com/nl/jst-ph-2-0-kabeltje-10cm-1069|€ 1,80|
|1|Bi-polaire stappenmotor|[https://www.tinytronics.nl/nl/mechanica-en-actuatoren/motoren/stappenmotoren/stappen-motor-met-uln2003-motoraansturing](https://www.tinytronics.nl/nl/mechanica-en-actuatoren/motoren/stappenmotoren/stappen-motor-met-uln2003-motoraansturing)|€ 4,50|