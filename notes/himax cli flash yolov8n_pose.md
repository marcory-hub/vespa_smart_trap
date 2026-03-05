
**One-line purpose:** cli flash command for yolov8n_pose
**Short summary:** 
**Agent:** inactive

---
[[himax cli flash model]]

adjust APP_TYPE to pose

```sh
python xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolov8_pose/yolov8n_pose_256_vela_3_9_0x3BB000.tflite 0x3BB000 0x00000"
```
