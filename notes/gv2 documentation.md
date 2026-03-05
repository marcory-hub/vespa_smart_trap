
**One-line purpose:** links to officiel documentation form seeed
**Short summary:** wiki, seeedstudio, sensecraft, swift yolo, github, edge impuls, himax webtoolkit, tutorials, reference 
**Agent:** too long user has to refactor it

---

to do
- [[doc arm ml developers guide for Cortex‑M + Ethos‑U (Vela “bible”)]]
- find out if we have to do something with export: model.export(format="onnx", end2end=False) [https://docs.ultralytics.com/models/yolo26/#python_1](https://docs.ultralytics.com/models/yolo26/#usage-examples)

Test:
- **one-to-one head** for max speed and simplicity
- **one-to-many head** when accuracy is top priority
	- model.export(format="onnx", end2end=False) [https://docs.ultralytics.com/models/yolo26/#python_1](https://docs.ultralytics.com/models/yolo26/#usage-examples)





- [Computer Vision at the Edge with Grove Vision AI Module V2](https://www.hackster.io/mjrobot/computer-vision-at-the-edge-with-grove-vision-ai-module-v2-0003c7) 
	- achtergrond info, Edge Impulse Studio, model conversion (tflite int8 quantized), vela compilation for ARM, Arduino IDE code voor inference
# Officiele documentatie
[Seeed Studio Official Wiki](https://wiki.seeedstudio.com/grove_vision_ai_v2/)
- hardware
- boot
- reset
- driver: 
	- macOS Vendor VCP Driver: [CH34xSER_MAC.ZIP](https://files.seeedstudio.com/wiki/grove-vision-ai-v2/res/CH341SER_MAC.ZIP)
- [bootloader recovery tool manual](https://wiki.seeedstudio.com/grove_vision_ai_v2/#bootloader-recovery-tool-manual)
>  `Before connecting the Grove Vision AI V2 to your computer, keep the BOOT button pressed while connecting to your computer via the data cable, and then release the BOOT button. In some cases, you may have to try 3-10 times to recover the bootloader successfully.`
- getting started
	- arduino [Program on Arduino connecting with Seeed Studio XIAO Board](https://wiki.seeedstudio.com/grove_vision_ai_v2_software_support/#-program-on-arduino-connecting-with-seeed-studio-xiao-board-)
	- senseCraft AI [No code getting started with SenseCraft AI]()
# Seeed studio
- **Wiki Seeed Studiio - Grove Vision AI Module V2**[](https://wiki.seeedstudio.com/grove_vision_ai_v2/)
	- Program on Arduino connecting with Seeed Studio XIAO Board[](https://wiki.seeedstudio.com/grove_vision_ai_v2_software_support/#-program-on-arduino-connecting-with-seeed-studio-xiao-board-)
	- For more information about Grove Vision AI's protocol definitions, you can read the [**protocol documentation**](https://github.com/Seeed-Studio/SSCMA-Micro/blob/dev/docs/protocol/at_protocol.md).
	- Developing Grove Vision AI V2 using Himax SDK[](https://wiki.seeedstudio.com/grove_vision_ai_v2_himax_sdk/) swift-yolo to sensecraft ai
> 	We don't really recommend that you change the image size in the Colab code, as this value is a more appropriate dataset size that we have verified to be a combination of size, accuracy, and speed of inference. If you are using a dataset that is not of this size, and you may want to consider changing the image size to ensure accuracy, then please do not exceed 240x240.
- [[seeed broken links]]
## SenseCraft AI
- **SenseCraft AI**[](https://sensecraft.seeed.cc/ai/model)
- [SenseCraft-Web-Toolkit website.](https://seeed-studio.github.io/SenseCraft-Web-Toolkit/#/setup/process) 
> 	We apologize that the AI model in the tool is not updating at this time.
- **Using a model for Grove Vision AI V2**[](https://wiki.seeedstudio.com/sensecraft_ai_pretrained_models_for_grove_visionai_v2/)
	- flashen van model via sensecraft ai website
## SSMCA
- SSMCA = SenseCraft Model Assistant by Seeed Studio
	- provides a complete toolchain for users to easily deploy AI models on low-cost hardwares, including:
- [SSCMA-Model-Zoo](https://sensecraft.seeed.cc/ai/#/model) SSCMA Model Zoo provides a series of pre-trained models for different application scenarios for you to use. The source code for this web is [hosted here](https://github.com/Seeed-Studio/sscma-model-zoo).
- [SSCMA-Web-Toolkit, which is now renamed to SenseCraft AI](https://sensecraft.seeed.cc/ai/#/home) A web-based tool that makes trainning and deploying machine learning models (with a focus on vision models by now) fast, easy, and accessible to everyone.
- [SSCMA-Micro](https://github.com/Seeed-Studio/SSCMA-Micro) A cross-platform framework that deploys and applies SSCMA models to microcontrol devices.
- [Seeed-Arduino-SSCMA](https://github.com/Seeed-Studio/Seeed_Arduino_SSCMA) Arduino library for devices supporting the SSCMA-Micro firmware.
- [Python-SSCMA](https://github.com/Seeed-Studio/python-sscma) A Python library for interacting with microcontrollers using SSCMA-Micro, and for higher-level deep learning applications.
## SWIFT-YOLO
- **SenseCraft Model Assistant by Seeed Studio**[](https://wiki.seeedstudio.com/ModelAssistant_Tutorials_Training_YOLO/)
- [yolov5-swift github](https://github.com/Seeed-Studio/yolov5-swift)
- [SenseCraft platform](https://sensecraft.seeed.cc/ai/model)
	- pretrained models + own models
- [[swift-yolo 192 Roboflow-Colab-SenseCraft]] 
	- **Bug fix**
		- [Grove AI vision - Install tensorflow for yolov5-swift error](https://forum.seeedstudio.com/t/grove-ai-vision-install-tensorflow-for-yolov5-swift-error/292556) 
		- [[z colab bugfix]]
- [SenseCraft-Web-Toolkit](https://seeed-studio.github.io/SenseCraft-Web-Toolkit/#/setup/process)
	- AI model in the tool
	- is not updating at this time...
	- vervangen door [SenseCraft platform](https://sensecraft.seeed.cc/ai/model)
## Firmware
- [Firmware source code](https://github.com/edgeimpulse/firmware-seeed-grove-vision-ai-module-v2)
## Seeed forum
- [[gv2 seeedstudio forum relevante posts]] 
# Github
- **Himax WiseEyePlus/Seeed Grove Vision AI Module V2**[](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2)
	- build the firmware (macOS intel environment)
	- flash the firmware
	- restore factory settings
	- scenario_app
		- face mesh [tflm_fd_fm](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/blob/main/EPII_CM55M_APP_S/app/scenario_app/tflm_fd_fm/README.md)
		- yolov8n object detection|[tflm_yolov8_od](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/blob/main/EPII_CM55M_APP_S/app/scenario_app/tflm_yolov8_od/README.md)
		- yolov8n pose [tflm_yolov8_pose](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/blob/main/EPII_CM55M_APP_S/app/scenario_app/tflm_yolov8_pose/README.md)
		- yolov8n gender classification [tflm_yolov8_gender_cls](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/blob/main/EPII_CM55M_APP_S/app/scenario_app/tflm_yolov8_gender_cls/README.md)pdm mic record [pdm_record](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/blob/main/EPII_CM55M_APP_S/app/scenario_app/pdm_record/README.md)
		- KeyWord Spotting using Transformers [kws_pdm_record](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/blob/main/EPII_CM55M_APP_S/app/scenario_app/kws_pdm_record/README.md)
		- imu read [imu_read](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/blob/main/EPII_CM55M_APP_S/app/scenario_app/imu_read/README.md)
		- peoplenet from TAO [tflm_peoplenet](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/blob/main/EPII_CM55M_APP_S/app/scenario_app/tflm_peoplenet/README.md)
		- yolo11n object detection [tflm_yolo11_od](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/blob/main/EPII_CM55M_APP_S/app/scenario_app/tflm_yolo11_od/README.md)
	- Edge Impulse examples
	- How to use CMSIS-NN at the project?
- **Himax WiseEyePlus / YOLOv8 on WE2**[](https://github.com/HimaxWiseEyePlus/YOLOv8_on_WE2)
	- Export yolov8n object detection pytorch model to int8 tflite[](https://github.com/HimaxWiseEyePlus/YOLOv8_on_WE2?tab=readme-ov-file#export-yolov8n-object-detection-pytorch-model-to-int8-tflite)
	- How to use HIMAX config file to generate vela model[](https://github.com/HimaxWiseEyePlus/YOLOv8_on_WE2?tab=readme-ov-file#how-to-use-himax-config-file-to-generate-vela-model)
	- Export yolov8n object detection pytorch model to int8 tflite and delete 4 transpose ops[](https://github.com/HimaxWiseEyePlus/YOLOv8_on_WE2?tab=readme-ov-file#export-yolov8n-object-detection-pytorch-model-to-int8-tflite-and-delete-4-transpose-ops)

**Seeed-Studio/sscma-example-we2**[](https://github.com/Seeed-Studio/sscma-example-we2)
- **Seeed-Studio/wiki documents**[](https://github.com/Seeed-Studio/wiki-documents/blob/docusaurus-version/docs/Sensor/Grove/Grove_Sensors/AI-powered/Grove-vision-ai-v2/Development/grove-vision-ai-v2-himax-sdk.md)
	- effectively utilize microSD cards for data management 
	- PDM microphones for audio capture. 

**Issues**
- [[gv2 issue max firmware image size open]]
- [[z yolo issue performance drop TFLite YOLOv8 YOLO11]]
- [[gv2 seeedstudio forum relevante posts]]
# Edge Impulse
- Firmware source code: [GitHub repository](https://github.com/edgeimpulse/firmware-seeed-grove-vision-ai-module-v2)
- Edge Impulse pre-compiled firmware: [seeed-grove-vision-ai-module-v2.zip](https://cdn.edgeimpulse.com/firmware/seeed-grove-vision-ai-module-v2.zip
- **Edge Impulse Docs for Grove Vision AI V2**
	- Official documentation for model deployment and hardware support. Relevant for those training models with Edge Impulse and wanting to export and deploy YOLOv8n.[](https://docs.edgeimpulse.com/docs/edge-ai-hardware/mcu-+-ai-accelerators/himax-seeed-grove-vision-ai-module-v2-wise-eye-2)[](https://docs.edgeimpulse.com/docs/edge-ai-hardware/mcu-+-ai-accelerators/himax-seeed-grove-vision-ai-module-v2-wise-eye-2)
- **Hackster Guide—Edge Impulse with Grove Vision V2**
	- Tutorial for creating, converting, and deploying custom vision models. Although Edge Impulse-centric, this guide includes general steps for flashing models not limited to YOLOv5.[](https://www.hackster.io/abhinav123krish/getting-started-with-grove-vision-v2-in-edge-impulse-3c5328)[](https://www.hackster.io/abhinav123krish/getting-started-with-grove-vision-v2-in-edge-impulse-3c5328)
- **Edge Impuls model on Himax AI**[](https://github.com/HimaxWiseEyePlus/Edge-Impulse-model-on-Himax-AI)
	- convert models
	- prepare custom application code
	- flash a YOLOv8n or Edge Impulse model to the Grove Vision AI V2
- **Edge Impulse firmware for Seeed Grove Vision AI Module V2 (Himax WiseEye2)**[](https://github.com/edgeimpulse/firmware-seeed-grove-vision-ai-module-v2)
- **Edge Impulse Example: standalone inferencing using Grove Vision AI Module V2 (Himax WiseEye2)**[](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/tree/main/EPII_CM55M_APP_S/app/scenario_app/ei_standalone_inferencing) 
# Himax webtoolkit zip
- **Himax AI Web Toolkit**[](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/releases/download/v1.1/Himax_AI_web_toolkit.zip)

# pt to TFLite
- **PyTorch to TensorFlow Lite for deploying on Arm Ethos-U55 and U65**[](https://community.arm.com/arm-community-blogs/b/ai-blog/posts/pytorch-to-tensorflow-lite-for-deploying-on-arm-ethos-u55-and-u65)
- TinyNeuralNetwork[](https://github.com/alibaba/TinyNeuralNetwork)

# PDM
- [[z audio PDM Pulse Density Modulation documentation]]
# Tutorials en Voorbeelden
- Arm
	- **Run a Computer Vision Model on a Himax Microcontroller**[](https://learn.arm.com/learning-paths/embedded-and-microcontrollers/yolo-on-himax/) 
		- Run a You-Only-Look-Once (YOLO) object detection model on a Himax WiseEye2 module.
		- Build the Himax Software Development Kit (SDK) and generate a firmware image file.
		- Update firmware on the Himax WiseEye2.
		- Connect to and use Grove Vision AI module.
- Hackster.io
	- **Getting Started with Grove Vision AI V2 and SenseCraft**[](https://www.hackster.io/etolocka/getting-started-with-grove-vision-ai-v2-and-sensecraft-bf4df6)
	- **Computer Vision at the Edge with Grove Vision AI Module V2**[](https://www.hackster.io/mjrobot/computer-vision-at-the-edge-with-grove-vision-ai-module-v2-0003c7)
- **Grove Vision Setup and No-Code Applications**[](https://www.mlsysbook.ai/contents/labs/seeed/grove_vision_ai_v2/setup_and_no_code_apps/setup_and_no_code_apps.html)
	- [Machine Learning Systems](https://www.mlsysbook.ai/)
> 	 The **WebUSB tool** may not function correctly in certain browsers, such as Safari. Use Chrome instead.
- **Q42 Engineering—Deploying Embedded AI**
	- yolov8 model getraind op hippo's, geen bruikbare uitleg
- **Getting Started with Grove Vision AI V2 and SenseCraft**[](https://www.hackster.io/etolocka/getting-started-with-grove-vision-ai-v2-and-sensecraft-bf4df6)
# Referenties
[A collection of useful links for those developing applications for Grove Vision AI V2](https://forum.seeedstudio.com/t/a-collection-of-useful-links-for-those-developing-applications-for-grove-vision-ai-v2/280236)
[WiseEye2 AI Processor](https://www.himax.com.tw/products/wiseeye-ai-sensing/wiseeye2-ai-processor)
# Datasets models code blocks
coco model voor evt test https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
# Afkortingen
PFLD=Practical Facial Landmark Detector












