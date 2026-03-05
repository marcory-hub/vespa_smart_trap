
**One-line purpose:** installation and documentation of bookworm
**Short summary:** 
**Agent:** archived

---


Bron: [Quick Start Guide - YOLO Raspberry Pi with Ultralytics YOLO11](https://docs.ultralytics.com/guides/raspberry-pi/)

# Flash bookworm 64-bit pi 5 8gb [[SD3 vespCV]]


# Flash bookworm 64-bit pi 4 4gb [[SD6 bookworm 64-bit pi4]]
hostname pi.local
gebruiksnaam: vcv
wachtwoord: alert
SSH: inschakelen
Gebruik wachtwoord authenthicatie
(geen wifi ingesteld)
# Connectie met Mac mini
Ethernetkabel aansluiten (of connecten via wifi)
IP-adres opzoeken
```sh
ping pi.local
```
of via Address Resolution Protocol
```sh
arp -a
```
of via IP scanner 
```sh
ssh vcv@192.168.178.203
```


## Virtual environment maken voor ultralytics
```
sudo apt install python3-venv -y
python3 -m venv venv
source venv/bin/activate
```

#### Install Ultralytics Package

Here we will install Ultralytics package on the Raspberry Pi with optional dependencies so that we can export the [PyTorch](https://www.ultralytics.com/glossary/pytorch) models to other different formats.

1. Update packages list, install pip and upgrade to latest
    
```
sudo apt update
sudo apt install python3-pip -y
pip install -U pip
```
    
2. Install `ultralytics` pip package with optional dependencies
    
```
pip install ultralytics[export]
```
    
3. Reboot the device
    
```
sudo reboot
```


## Install rpi-connect
bron: https://www.raspberrypi.com/documentation/services/connect.html
If Connect isn’t already installed in your version of Raspberry Pi OS, open a Terminal window. Run the following command to update your system and packages:

```
sudo apt update && sudo apt full-upgrade -y
```

Run the following command on your Raspberry Pi to install Connect:

```
sudo apt install rpi-connect
```

You can also install Connect from the Recommended Software application.

After installation, use the `rpi-connect` command line interface to start Connect for your current user:

```
rpi-connect on
```

```sh
rpi-connect signin
```
LET OP: Complete sign in by visiting https://connect.raspberrypi.com/verify/

Alternatively, click the Connect icon in the menu bar to open a dropdown menu and select **Turn On Raspberry Pi Connect**:


Best Practices when using RPI
- use SSD
- Flash without GUI --> wel minder gebruikersvriendelijk
- Overclock