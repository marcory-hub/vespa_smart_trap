
**One-line purpose:** documentation how to flash the model to gv2
**Short summary:** 
**Agent:** inactive

---


ag2025-11-13 tbv AG
## Build firmware
https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2#build-the-firmware-at-windows-environment
Als het goed is zou deze moeten werken voor windows 
## APP_TYPE instellen
in de file `Himax/Seeed_Grove_Vision_AI_Module_V2/EPII_CM55M_APP_S`
staat onderaan vermoedelijk APP_TYPE = ...yolo8, deze even aanpassen naar `APP_TYPE = tflm_yolo11_od`

Model staat hier [yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite](https://imkersleiden.sharepoint.com/:u:/g/EUXNUx76w0RKsny0Om3cATsBJgR0dZhM7W07r8Q0Q3stUw?e=55LxHk)

Kopieer het model van naar de juiste `model_zoo` directory:
- YOLO11 OD: `model_zoo/tflm_yolo11_od/`
(is overigens 224x224 model, dus net iets beter dan de aanbevolen 192x192)
## Flash firmware
https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2?tab=readme-ov-file#how-to-flash-the-firmware

```sh
python xmodem/xmodem_send.py \
  --port=/dev/tty.usbmodem58FA1047631 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img \
  --model="model_zoo/tflm_yolo11_od/yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite 0xB7B000 0x00000"
```

output eindigt met
`b'Do you want to end file transmission and reboot system? (y)'`
vervolgens kort zwarte reset button indrukken
en GV begint meteen met detectie

Wat mooiere controle of het model werkt kan via de Himax ai toolkit:
- [Himax_AI_web_toolkit](https://imkersleiden.sharepoint.com/:f:/g/EiDhuDivZ7VJvZ_iX1ej6hABsC2NFON17SJ43janto9AAg?e=2IEz7w) downloaden (hierin zijn de coco classes vervangen door de juiste namen)
- openen via dubbelklikken op inde
- Selecteer "Grove Vision AI V2
- Klik op "Connect
- Controleer of detecties worden getoond


---


1. **GitHub Repository - HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2**
   - **Hoofdlink**: https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2
   - **Flash procedure (Python)**: https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2?tab=readme-ov-file#flash-image-update-at-linux-environment-by-python-code
   - **Firmware build (macOS)**: https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2?tab=readme-ov-fil

2. **Seeed Studio Wiki - Grove Vision AI V2**
   - **Hoofdlink**: https://wiki.seeedstudio.com/grove_vision_ai_v2/
   - **Himax SDK Development**: https://wiki.seeedstudio.com/grove_vision_ai_v2_himax_sdk/

### Gerelateerde repositories

- **YOLOv8 on WE2**: https://github.com/HimaxWiseEyePlus/YOLOv8_on_WE2
  - Model conversie en transpose optimalisatie
- **Seeed Studio Wiki Documents**: https://github.com/Seeed-Studio/wiki-documents/blob/docusaurus-version/docs/Sensor/Grove/Grove_Sensors/AI-powered/Grove-vision-ai-v2/Development/grove-vision-ai-v2-himax-sdk.md


---


