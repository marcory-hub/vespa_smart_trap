**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---



- [[vela.tflite]] int 8
- max 2.4 MB (grootste op github 2.2 MB)

Grove Vision AI V2 only supports models in the `int8_vela.tflite` format
https://github.com/Seeed-Studio/wiki-documents/blob/docusaurus-version/docs/Sensor/Grove/Grove_Sensors/AI-powered/Grove-vision-ai-v2/grove_vision_ai_v2_sscma.md
https://wiki.seeedstudio.com/grove_vision_ai_v2_sscma/

The input image size for the model must be square (e.g., 192x192 pixels) and should not exceed 240x240 pixels. https://wiki.seeedstudio.com/grove_vision_ai_v2_sscma/
yolo kan echter alleen machten van 2, dus 2^6 is max afmeting

[Grove vision AI module V2 wiki](https://wiki.seeedstudio.com/grove_vision_ai_v2/)
- Dual Cortex-55 + ethos_U55
- Supports TensorFlow and PyTorch frameworks and is compatible with Arduino IDE
- With the SenseCraft AI algorithm platform, trained ML models can be deployed to the sensor without the need for coding.





