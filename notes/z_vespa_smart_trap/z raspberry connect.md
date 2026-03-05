
**One-line purpose:** documentation of raspberry connect
**Short summary:** installation on raspberry
**Agent:** archived

---



Connect signs communication with your device serial number. Moving your SD card between devices will sign you out of Connect.

If you receive an email that says a device that you do not recognise has signed into Connect, change your Raspberry Pi ID password immediately. Remove the device from Connect to permanently disassociate it from your account. Consider enabling two-factor authentication to keep your account secure.

Installatie op RPI
```sh
sudo apt update
sudo apt full-upgrade
sudo apt install rpi-connect
rpi-connect on
```
We recommend enabling user-lingering on all headless Raspberry Pi OS Lite setups to prevent your device from becoming unreachable after a remote reboot.

Connect runs as a user-level service, not as root. As a result, Connect only works when your user account is currently logged in on your device. This can make your device unreachable if you reboot with automatic login disabled. To continue running Connect even when you aren’t logged into your device, enable **user-lingering**. Run the following command from your user account to enable user-lingering:
```sh
loginctl enable-linger
```

Visit [connect.raspberrypi.com](https://connect.raspberrypi.com/) on any computer.
