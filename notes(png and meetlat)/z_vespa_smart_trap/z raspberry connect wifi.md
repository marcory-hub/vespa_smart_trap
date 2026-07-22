
**One-line purpose:** enable wifi connection on raspberry
**Short summary:** enable wifi connection with sd or ethernet
**Agent:** archived

---



# Raspberry Pi 4: Wifi-instelling

## Methode 1: Wi-Fi-instellingen via SD-kaart aanpassen

### Benodigdheden
- Raspberry Pi 4
- MicroSD-kaart met Raspberry Pi OS
- SD-kaartlezer
- Computer (Windows, macOS of Linux)
- App om IP adressen te scannen (bv IP scanner)

### Stappen

1. Schakel de Raspberry Pi uit.
2. Verwijder de microSD-kaart en plaats deze in een computer.
3. Open de boot-partitie van de SD-kaart.
4. Maak of overschrijf een bestand genaamd `wpa_supplicant.conf` met de volgende inhoud:

    ```
    country=NL
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1

    network={
        ssid="Nieuwe_WiFi_Naam"
        psk="Nieuw_WiFi_Wachtwoord"
        key_mgmt=WPA-PSK
    }
    ```

5. Maak een leeg bestand genaamd `ssh` (zonder extensie) in de boot-partitie.
6. Verwijder de SD-kaart veilig en plaats deze terug in de Raspberry Pi.
7. Sluit de Raspberry Pi aan op stroom.
8. Zoek het IP-adres via de routerinterface of een IP-scanner.
9. Maak verbinding via SSH:

    ```
    ssh pi@<ip-adres-van-raspberrypi>
    ```

10. Log in met gebruikersnaam `pi` en wachtwoord `raspberry` (indien standaard).

---

## Methode 2: Wifi instellen via Ethernet-kabel

### Benodigdheden
- Raspberry Pi 4
- MicroSD-kaart met Raspberry Pi OS
- Ethernet-kabel verbonden met router of switch
- Computer op hetzelfde netwerk met installatie van Raspberry Connect

### Stappen

1. Verbind de Raspberry Pi via Ethernet met de router of switch.
2. Sluit de Raspberry Pi aan op stroom.
3. Open Raspberry connect in de browser
4. Klik op ethernet connectie (pijl omhoog en omlaag rechts boven)
5. Open op de raspberry de terminal
6. ```sudo nmtui
7. Verwijder oude Wi-Fi
	1. Voeg nieuwe Wi-Fi gegevens toe (SSID (wifi naam) en password)

Troubleshooting SSH
- key verwijderen uit known_hosts
	- cd .ssh
	- nano known_hosts
	- verwijder alle keys die vermeld staan bij het IP adres van de raspberry
