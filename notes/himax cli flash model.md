
**One-line purpose:** cli command to flash a model to gv2
**Short summary:** flashcommands for the different models (and results)
**Agent:** inactive

---

```sh
cd /Users/md/Developer/vespCVacc/Himax/
source .venv/bin/activate
```

```sh
export PATH="/Applications/ArmGNUToolchain/14.3.rel1/arm-none-eabi/bin:$PATH" 
hash -r
```

```sh
which arm-none-eabi-gcc
```
expected output: gnu

check path
```sh
echo "int main() { return 0; }" | arm-none-eabi-gcc --specs=nano.specs -x c -c -o /dev/null -
```

pas APP_TYPE aan
```sh
cd /Users/md/Developer/vespCVacc/Himax/Seeed_Grove_Vision_AI_Module_V2/EPII_CM55M_APP_S
nano makefile
```

```sh
cd /Users/md/Developer/vespCVacc/Himax/Seeed_Grove_Vision_AI_Module_V2/EPII_CM55M_APP_S
make clean
make
```

```sh
cd ../we2_image_gen_local/
cp ../EPII_CM55M_APP_S/obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf input_case1_secboot/
```

```sh
./we2_local_image_gen_macOS_arm64 project_case1_blp_wlcsp.json
```

```sh
cd /Users/md/Developer/vespCVacc/Himax/Seeed_Grove_Vision_AI_Module_V2
```

---
# Flash commands for the different models


2025-08-31
```sh
python3 xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolo11_od/yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite 0xB7B000 0x00000"
```
[Himax AI](file:///Users/md/Developer/vespCVacc/Himax/Seeed_Grove_Vision_AI_Module_V2/Himax_AI_web_toolkit/index.html)

 

```
#define YOLOV8_POSE_FLASH_ADDR 0x3A3BB000
```

256 model -> geen detectie
```sh
python xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolo11_od/best256_full_integer_quant_vela.tflite 0xB7B000 0x00000"
```
[Himax AI](file:///Users/md/Developer/vespCVacc/Himax/Seeed_Grove_Vision_AI_Module_V2/Himax_AI_web_toolkit/index.html)

yolov8n 192 modelzoo delete transpose
```sh
python xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolov8_od/yolov8n_od_192_delete_transpose_0xB7B000.tflite 0xB7B000 0x00000"
```

yolo11n 224 modelzoo
```sh
python xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolo11_od/yolo11n_full_integer_quant_vela_imgz_224_kris_nopost_241230.tflite 0xB7B000 0x00000"
```


```sh
python xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolo11_od/yolo11n_full_integer_quant_vela.tflite 0xB7B000 0x00000"
```

/Users/md/Developer/vespCVacc/Himax/Seeed_Grove_Vision_AI_Module_V2/model_zoo/tflm_yolo11_od/yolo11n_full_integer_quant_vela.tflite
```sh
python xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolo11_od/yolo11n_full_integer_quant_vela.tflite 0x3AB7B000 0x00000"
```



expected output
```
(.venv) md@m2 Seeed_Grove_Vision_AI_Module_V2 % python xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolov8_pose/yolov8n_pose_256_vela_3_9_0x3BB000.tflite 0x3BB000 0x00000"
Open Serial Port /dev/tty.usbmodem58FA1047631
Device init successfully
Please press reset button!!
b'1st BL Modem Build DATE=Nov 30 2023, 0x0002000b'
b'Please input any key to enter X-Modem mode in 100 ms'
b'waiting input key'
b'Set X-modem flag = Yes'
b''
b'slot flash_offset 0x00000000'
b'jump_addr=0x3401f000'
b'Compiler Version: ARM CLANG, Clang 13.0.0 (ssh://ds-gerrit/armcompiler/llvm-project 1f5770d6f72ee4eba2159092bbf4cbb819be323a)'
b'set_IP_secure done'
b'flash type[0], flash size[5]'
b'slot FlashOffset 0x00100000'
b'Image max size 0x00100000'
b'------------------------------------------------------------'
b'[0] Reboot system'
b'[1] Xmodem download and burn FW image'
b'------------------------------------------------------------'
b''
b'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
b'!!  Please keep the power on during the program upgrade process  !!'
b'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
b''
b''
b'Send data using the xmodem protocol from your terminal'
xmodem_sending >> we2_image_gen_local/output_case1_sec_wlcsp/output.img
[██████████████████████████████] 100.00% 2816/2816 error: 0

xmodem_send bin file done!!
generate _temp_model_0_preamble_data.bin for model_zoo/tflm_yolov8_pose/yolov8n_pose_256_vela_3_9_0x3BB000.tflite preamble data
xmodem_sending >> _temp_model_0_preamble_data.bin
[██████████████████████████████] 100.00% 1/1 error: 0

xmodem_send bin file done!!
xmodem_sending >> model_zoo/tflm_yolov8_pose/yolov8n_pose_256_vela_3_9_0x3BB000.tflite
[██████████████████████████████] 100.00% 17993/17993 error: 0

xmodem_send bin file done!!
xmodem_send bin file result =  True
b'\x06'
b''
b'Do you want to end file transmission and reboot system? (y)'
```

then press black reset button

An connect with [Himax AI toolkit](file:///Users/md/Developer/vespCVacc/Himax/Seeed_Grove_Vision_AI_Module_V2/Himax_AI_web_toolkit/index.html#/setup/process)


