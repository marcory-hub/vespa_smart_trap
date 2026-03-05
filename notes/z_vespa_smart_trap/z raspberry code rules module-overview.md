
**One-line purpose:** module overview
**Short summary:** summary of the modules in the vespCV project, detailing their purpose, key functionalities, and interdependencies.
**Agent:** archived

---



## Overview

This document provides a summary of the modules in the vespCV project, detailing their purpose, key functionalities, and interdependencies.

### Files and modules

- **`.gitignore`**: Specifies files and directories that should be ignored by Git.
- **`LICENSE`**: Contains the GNU General Public License (GPL) Version 3.
- **`README.md`**: Overview, installation instructions, usage guide, and troubleshooting information for the vespCV project.
- **`requirements.txt`**: Lists all Python libraries with version numbers used in the project.

### Core Modules

- **`src/core/config_loader.py`**: Loads and validates configuration settings from a YAML file, ensuring required parameters are present and valid.
- **`src/core/detector.py`**: Core detection component responsible for loading the YOLO model, capturing images, and performing object detection in a separate thread. capturing images, and performing object detection in a separate thread. Depends on `config_loader.py` for settings and utilizes functions from `detection_utils.py`.
- **`src/core/logger.py`**: Logs system events and statistics, facilitating monitoring and debugging.
- **`src/core/main.py`**: Entry point for the vespCV application, initializing core components and handling application shutdown.

### Utility Modules

- **`src/utils/detection_utils.py`**: Provides utility functions for image capture, logging detection data, and saving images.
- **`src/utils/image_utils.py`**: Handles image processing tasks, including saving annotated images.
- **`src/utils/led_controller.py`**: Manages LED operations based on detection events using GPIO pins on a Raspberry Pi.
- **`src/utils/mail_utils.py`**: Sends warning emails with detection images attached.
- **`src/utils/test_gpio.py`**: Verifies the installation and functionality of the RPi.GPIO library.

### GUI Module

- **`src/gui/app.py`**: Implements the graphical user interface for the vespCV application, integrating image handling, detection control, and system logging.

### Testing

- **`tests/InsectSlider.m4v`**: A slider with different insects for testing purposes. To run tests, execute the relevant modules directly.
