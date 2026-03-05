### Installeer xmodem

```sh
cd /Users/md/Developer/vespCVacc/Himax/Seeed_Grove_Vision_AI_Module_V2
pip install -r xmodem/requirements.txt
```
**Let op**: gebruik gewoon `pip` als je in een virtuele omgeving zit — dat zorgt ervoor dat het de juiste versie pakt.
### Zoek poort
```sh
ls /dev/tty.*
```

/dev/tty.usbmodem58FA1047631

```sh
sudo chmod 777 /dev/tty.usbmodem58FA1047631
```

pwd hieronder aanpassen bij installatie in ander folder
```sh
python xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=/Users/md/Developer/cv_vespcv_acc/Himax1/Seeed_Grove_Vision_AI_Module_V2/we2_image_gen_local/output_case1_sec_wlcsp/output.img
```

```sh
python3 /Users/md/Developer/cv_vespcv_acc/Himax1/Seeed_Grove_Vision_AI_Module_V2/xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=/Users/md/Developer/cv_vespcv_acc/Himax1/Seeed_Grove_Vision_AI_Module_V2/we2_image_gen_local/output_case1_sec_wlcsp/output.img
```
als dit personen detecteert verder met [[himax makefile met tflm_yolov8_od]]
