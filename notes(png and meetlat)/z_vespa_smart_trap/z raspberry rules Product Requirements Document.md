**One-line purpose:** product requirements document for the raspberry pi prototype
**Short summary:** prd, might be a template for new projects
**Agent:** archived

---

# Product Requirements Document (PRD) - vespCV

_always prioritize_ the PRD

---

## 1. Introduction

* **1.1 Goal:** This document describes the functional and non-functional requirements for vespCV, an application for detecting Asian hornets (Vespa velutina) using a Raspberry Pi 4, a Camera Module 3, and a YOLOv11s object detection model.
* **1.2 Target Audience:** This document is intended for the development team, testers, and other stakeholders involved in the development of vespCV.
* **1.3 Context:** The Asian hornet is an invasive species that poses a threat to biodiversity and the honeybee population. Early detection is crucial for effective control. vespCV offers an automated solution for this detection.
* **1.4 Operation:** Camera input --> AI detection --> storage/logging

---

## 2. Goals

* **2.1 Primary Goals:** (Proof of Concept)
    * Real-time detection of Asian hornets in camera footage.
    * Local deployment on a cost-efficient Raspberry Pi 4.
    * Simple installation and configuration.
    * Storage of detection images and logging.
* **2.2 Secondary Goals:** (Application for Users)
    * User-friendly graphical interface (GUI) for monitoring and configuration.
    * Ability to export detection data.
    * Automation of application startup.
    * Graceful shutdown upon stopping.

---

## 3. User Stories

* As a beekeeper, I want to place vespCV in my apiary so that I am warned early about the presence of Asian hornets, allowing me to take quick action.
* As a volunteer monitoring invasive species, I want an affordable and easy-to-implement solution to map the spread of the Asian hornet in my region.
* As a researcher, I want access to logged detection data and images to analyze the behavioral patterns of Asian hornets.

---

## 4. Functional Requirements

* **4.1 Detection:**
    * FR01: The application must be capable of processing live video streams from the Raspberry Pi Camera Module 3.
    * FR02: The application must use the YOLOv11s model to perform object detection on the video streams.
    * FR03: The application must accurately detect Asian hornets in the video streams.
    * FR04: Upon detection, the application must provide the detected object with a bounding box and a label ("Asian hornet").
    * FR05: The application must apply a configurable threshold (confidence score) to filter detections. This threshold must be configurable.
* **4.2 Storage:**
    * FR06: Upon detection, the application must save an image of the frame with the detected hornet in the `data/images/` folder. The filename must include species, confidence score, and timestamp.
    * FR07: The application must log detection information (species, confidence score, timestamp, bounding box location) in a CSV file in the `data/logs/` folder.
* **4.3 Configuration:**
    * FR08: The application must load configuration settings from files in the `config/` folder.
    * FR09: The following parameters must be configurable:
        * Detection threshold (confidence score).
        * Storage location for images.
        * Storage location for log files.
        * Any model-specific parameters.
* **4.4 User Interface (GUI - Optional):**
    * FR10: If implemented, the application must provide a graphical interface (GUI).
    * FR11: The GUI must display a live feed from the camera with bounding boxes around detected hornets.
    * FR12: The GUI must allow configuration parameters to be adjusted (as mentioned in FR09).
    * FR13: The GUI must be able to display 4 detections with the highest confidence from the current session (with image and log information).
* **4.5 Autostart:**
    * FR14: The application must be configurable to start automatically when the Raspberry Pi boots up.
* **4.6 Error Handling:**
    * FR15: The application must log error messages (e.g., failed camera access or full storage medium) and make them visible (in GUI or CLI).

---

## 5. Non-Functional Requirements

* **5.1 Performance:**
    * NFR01: Detection must occur in near real-time (minimal delay between event and detection).
    * NFR02: The application must not excessively burden the Raspberry Pi 4's system resources (<70% CPU over a 5 min average).
* **5.2 Reliability:**
    * NFR03: The application must run stably and minimize crashes.
    * NFR04: Logged data must be consistent and accurate.
* **5.3 Usability:**
    * NFR05: The application must be easy to install and configure, even for users with limited technical knowledge (especially basic configuration). Installation via SD card.
    * NFR06: The GUI must be intuitive and easy to understand.
* **5.4 Maintainability:**
    * NFR07: The code must be structured and well-documented to facilitate future updates and maintenance.
* **5.5 Scalability (Future):**
    * NFR08 (Optional): Integration with cloud services or other platforms may be considered in the future.

---

## 6. Technical Requirements

* **6.1 Platform:** Raspberry Pi 4 (4GB)
* **6.2 Operating System:** Raspberry Pi OS (bookworm)
* **6.3 Programming Language:** Python
* **6.4 Libraries:** Requirements as specified in `requirements.txt`. This may include OpenCV, PyTorch (or another library for loading and running the YOLO model), and GUI libraries (such as Tkinter or PyQt if FR10-FR13 are implemented).
* **6.5 Hardware:** Raspberry Pi Camera Module 3
* **6.6 Model:** YOLOv11s (model weights optimized and ready in the `models/` folder)
* **6.7 Development Environment:** Development via SSH with Cursor/VSCode.

---

## 7. Release Criteria

* All primary functional requirements (FR01-FR07 and FR14) are implemented and tested.
* The application detects Asian hornets with an accuracy of at least 99%. Accuracy is measured by storing all observed insects (image and timestamp) in a test setup and then manually analyzing them and comparing them with the application's detections.
* The application runs stably on the Raspberry Pi 4 for 12 hours.
* Basic documentation for installation and configuration is available.

---

## 8. Future Improvements (Backlog)

* Implementation of the optional GUI (FR10-FR13).
* Ability to send detection notifications (e.g., via email or another service).
* Triggering a connected mechanical defense or capture mechanism upon detection (such as an electrically operated harp).
* Integration with GPS modules for geotagging detections.
* Support for training the model with new data.
* Implementation of more advanced analysis of detection patterns.

---

## 9. Log Format and Details

* **Format:** `.log` 
* **Content per detection:**
    * Species name
    * Confidence score of the detection.
    * Timestamp of the detection (YYYY-MM-DD HH:MM:SS).
    * Bounding box location (x_min, y_min, x_max, y_max) in the image.
    * Filename of the saved image.
    * *Example*: vvel-0.99-20250602-120233.jpg
* **Additional log information:**
    * **Detected species**: detected vvel and other classes, saved as class, confidence, date, time
    * **YOLO training data**: class_id center_x center_y width height. Stored in a txt file.
    * **Temperature:** CPU temperature of the Raspberry Pi, at 15 minute intervals.
    * **Camera Status:** Any error messages or status updates from the camera (e.g., if the camera is not working correctly or has timed out).
    * **Available Memory:** Regularly logging available spece on the Raspberry Pi's SD.
    * **CPU Load:** Regularly logging CPU load can also provide insight into application performance.