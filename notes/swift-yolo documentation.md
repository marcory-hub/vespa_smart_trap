**One-line purpose:** swift yolo information
**Short summary:** 
**SoT:** 
**Agent:** link to seeed modelzoo
**Main Index:** [[_model]]

---


https://github.com/Seeed-Studio/sscma-model-zoo/tree/main/notebooks/en

# Bestaande modellen
Alle modellen zijn swift-yolo modellen
# Custom modellen
yolov8n float16 en 32 en yolo11n float16 geven 'model failed' en 'invoke failed'

[Deploying Models from Datasets to Grove Vision AI V2](https://github.com/Seeed-Studio/wiki-documents/blob/docusaurus-version/docs/Sensor/Grove/Grove_Sensors/AI-powered/Grove-vision-ai-v2/grove_vision_ai_v2_sscma.md)

voorbeeld colab apple detection https://colab.research.google.com/github/seeed-studio/sscma-model-zoo/blob/main/notebooks/en/Apple_Detection_Swift-YOLO_192.ipynb
Geeft RuntimeError: Numpy is not available
image size max 240x240 (demo's zijn met 192x192)

https://github.com/Seeed-Studio/wiki-documents/issues/2203

issues [404 melden](https://github.com/Seeed-Studio/wiki-documents/issues/449)

# Image size
max 240x240, echter geen macht 6, dus 192 gebruiken
[In roboflow al naar 192x192](https://wiki.seeedstudio.com/Train-Deploy-AI-Model-Grove-Vision-AI/#jump2:~:text=Step%2013.%20Now%20you%20can%20add%20Preprocessing%20and%20Augmentation%20if%20you%20prefer.%20Here%20we%20will%20change%20the%20Resize%20option%20to%20192x192)

# YOLOv5 training
[Train using YOLOv5 on Google Colab](https://wiki.seeedstudio.com/Train-Deploy-AI-Model-Grove-Vision-AI/#train-using-yolov5-on-google-colab)
