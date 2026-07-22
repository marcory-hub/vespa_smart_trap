**One-line purpose:** index for the raspberry pi4 prototype notes
**Short summary:** models hornet3000 and 17000 with arducam on raspberry pi 4
**Agent:** archived [[z rules documentation-readme]] might be used as template when writing documentation for beekeepers and other users of the detector

---

# Overview
[[z raspberry project overview]], goal, hardware, software, installation, error handeling
[[z rules documentation-readme]], audience, tone and style, doc types, writing approach, format guidelines
# Hardware
[[z raspberry hardware]]
# Connections
[[z raspberry connect]]
[[z raspberry connect wifi]], enable wifi connection with sd or ethernet
# OS
[[z raspberry installation bookworm, venv, rpi-connect, ultralystics]], installation and documentation of bookworm
# Python code blocks
[[z raspberry code rules module-overview]], summary of the modules in the vespCV project, detailing their purpose, key functionalities, and interdependencies
[[z raspberry code tree structure]]
[[z raspberry code unit test]], detector and logger tests
[[z raspberry code  camera module 3 autofocus]], code for camera module 3 to autofocus en fix focus 
[[z raspberry code  logging implementatie]], logs detections, time, temperature
[[z raspberry code  start_vespcv]], script to start detector
[[z raspberry code yolo inference]], code to run inference with camera on raspberry pi
[[z raspberry code and doc  graceful shutdown via gpio and switch]], online examples for graceful shutdown
[[z raspberry code camera interface implementation]], calibrate and focus
[[z raspberry code core detector]], load model, get image every 15s, run detection
[[z raspberry code detectie loop met 15-second intervals]], inference loop
[[z raspberry code headless or debug preview with logging]], code for headless detector
[[z raspberry code logger helper]], code for logger
# UI
[[z raspberry ui concept v0]]
# Backup
[[z raspberry doc sd backup]], backup script
# Documentation
[[z rules documentation-readme]]
[[z raspberry rules Product Requirements Document]], prd, might be a template for new projects
[[z raspberry yolov10n model on raspberry pi 4]]