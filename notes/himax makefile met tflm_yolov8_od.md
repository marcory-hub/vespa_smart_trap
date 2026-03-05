
**One-line purpose:** 
**Short summary:** 
**Agent:** 

---

```sh
cd /Users/md/Developer/vespCVacc/Himax/Seeed_Grove_Vision_AI_Module_V2/EPII_CM55M_APP_S
```


Aanpassen van de makefile
- open makefile
```sh
nano makefile
```
- pas **APP_TYPE** aan (helemaal onderaan)
	- |tflm_yolov8_od
	- Object detection
	- model_zoo\tflm_yolov8_od\yolov8n_od_192_delete_transpose_0xB7B000.tflite 0xB7B000 0x00000

[[himax makefile]]
[[himax modelzoo readme]]

Firmware leegmaken
```sh
make clean
make
```

regenereer nieuwe firmware image
```sh
cd ../we2_image_gen_local/
cp ../EPII_CM55M_APP_S/obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf input_case1_secboot/
```

run script
```sh
./we2_local_image_gen_macOS_arm64 project_case1_blp_wlcsp.json
```
en cd terug naar Seeed folder
```sh
cd ..
```


en flash
```sh
python xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model=/model_zoo/tflm_yolov8_od/yolov8n-2025-08-23-Imgsz192_integer_quant_vela.tflite,0xB7B000,0x00000


```
/Users/md/Developer/vespCVacc/Himax/Seeed_Grove_Vision_AI_Module_V2/model_zoo/tflm_yolov8_od/bestyolov8nImgsz192_int8.tflite

als Uart port open fail
```sh
lsof | grep tty.usbmodem58FA1047631
```

```sh
kill -9 <PID>
```
verder met [[himax ai web toolkit installation]]


---
netron.app

![[acc yolov8n_od_192_delete_transpose_0xB7B000.tflite.png]]cd ..