**One-line purpose:** how to generate a new firmware image with new custom model
**Short summary:** compile firmware image, copy and compile elf file, generate image firmware file
**Agent:** after adjusting the [[himax makefile]] user should generate new firmware image
**Index:** [[himax from pt to flash]]

---
[[himax flash firmware]]
# flash command

```sh
python xmodem/xmodem_send.py --port=/dev/tty.usbmodem58FA1047631 --baudrate=921600 --protocol=xmodem --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img --model="/Users/md/Developer/vespa_smart_trap/himax/Seeed_Grove_Vision_AI_Module_V2/model_zoo/tflm_yolo11_od/yolo26n_vespa_2026-02v1_allpx_imgsz224_full_integer_quant_vela.tflite 0xB7B000 0x00000"
```

---
xmodem is located in /Users/md/Developer/vespa_smart_trap/himax/Seeed_Grove_Vision_AI_Module_V2

---

**Documentation**
- baudrate: 921600
- check if COM port is correct `ls /dev/tty.*`
- nopost vela models are needed
- check makefile for APP_TYPE [[himax makefile]]

---

**Trouble shooting**
- make image from scratch after checking 

---

next check model with
[[himax ai web toolkit installation]]



**One-line purpose:** build model with himax sdk
**Short summary:** command to build the model
**Agent:** current stack, himax sdk
**Index:** [[himax from pt to flash]]

---


- Connect gv2 with USB
- Go to Seeed gv2 directory and activate the environment
```sh
cd Himax_gv2_esp32/Seeed_Grove_Vision_AI_Module_V2/
source .venv/bin/activate
```

- go to EPII_CM55M_APP_S
```bash
cd EPII_CM55M_APP_S
```
- make a clean model
```sh
make clean && make
```
- copy the elf
```sh
cp obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf ../we2_image_gen_local/input_case1_secboot/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf
```

```sh
cd ../we2_image_gen_local
./we2_local_image_gen_macOS_arm64 project_case1_blp_wlcsp.json
```

```sh
cd ..
```

**check port** 
- COM port `ls dev/ttx.*`
- macOS
```
screen /dev/cu.usbmodem58FA1047631
```
- windows
```
screen /dev/cu.usbmodem101
```

[[himax gv2 troubleshooting]]