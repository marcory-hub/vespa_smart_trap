This project aims to build an Asian hornet detector application using Python. The core of the application will leverage the YOLOv11s object detection model, for which optimized weights are already available.

The application will be deployed on a Raspberry Pi 4 (4GB) equipped with a Camera Module 3. Development will primarily be done remotely via SSH using Cursor and VSCode.

The project structure is organized as follows:

```txt
vespCV/
├── src/
│   ├── core/         # Core detection logic
│   ├── gui/          # GUI implementation
│   └── utils/        # Utility functions
├── config/           # Configuration files
├── tests/            # Test files
├── data/
│   ├── images/       # Stored detection images
│   └── logs/         # CSV log files
└── models/           # YOLO model directory
    └── yolov11s.pt   # Your YOLO model
```

Our development approach involves a hybrid strategy:

- **Remote Development:** Utilizing SSH with Cursor/VSCode for the majority of the coding.
- **On-Device Testing:** Direct development and testing on the Raspberry Pi for real-time performance evaluation.
- **Version Control:** Employing Git for managing code changes.

Dependency management will be handled using `requirements.txt`, with a distinction between production and development dependencies. We will also consider Pi-specific package requirements.

To ensure code quality and maintainability, we will establish an automated testing setup and follow a structured workflow for updates.

The next steps for this project include:

1. Creating the necessary configuration files.
2. Implementing the core Asian hornet detection logic.
3. Developing the user interface (GUI).
4. Setting up the automated testing framework.
5. Implementing data logging functionality.
6. Configuring the application for automatic startup on the Raspberry Pi.