
**One-line purpose:** format and size of the quantized and converted model on grove vision ai v2
**Short summary:**
- 192x192px or 224x224px max
- [[vela]] int 8
- max 2.4 MB 
**SoT:** yes
**Agent:** when flashing gv2 with himax is considered, check these
**Index:** [[_himax sdk]]

---

1. The input image size for the model must be square 192x192 pixels or 224x224 pixels
2. should not exceed 240x240 pixels. 
3. yolo makes steps of 32px, so 224px is the max image size when using yolo
4. quantization: full integer int8 tflite
5. conversion to vela to be used on the gv2
6. max 2.4GB model size


**Online documentation**
Github Seeed studio wiki documentation
- [Deploying Models from Datasets to Grove Vision AI V2](https://github.com/Seeed-Studio/wiki-documents/blob/docusaurus-version/docs/Sensor/Grove/Grove_Sensors/AI-powered/Grove-vision-ai-v2/grove_vision_ai_v2_sscma.md)
Seeed studio
- [Grove vision AI module V2 wiki](https://wiki.seeedstudio.com/grove_vision_ai_v2/)
- [Deploying Models from Datasets to Grove Vision AI V2](https://wiki.seeedstudio.com/grove_vision_ai_v2_sscma/)






