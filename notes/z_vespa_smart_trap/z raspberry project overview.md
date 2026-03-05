
**One-line purpose:** project summary
**Short summary:** goal, hardware, software, installation, error handeling
**Agent:** archived

---



# Project Overview
- **Objective**: Develop a hornet detection system utilizing a Raspberry Pi 4 or 5, Camera Module 3, and YOLOv11s for real-time monitoring and detection.
## Hardware Specifications
- **Device**: Raspberry Pi 4 or 5 (4GB or higher)
  - **Hostname**: `pi`
  - **Username**: `vcv`
- **Camera**: Camera Module 3
- **GPIO**: Used for controlling LEDs and other hardware components.
- **Graceful shutdown**: by pressing a button connected to GPIO pins.
## Software Environment
- **Operating System**: Linux (Bookworm, compatible version for Raspberry Pi)
- **Programming Language**: Python
- **Virtual Environment**: Utilizes a virtual environment (`venv`) for package management.
- **Project Directory**: The project is located in the folder `/home/vcv/vespcv/` on the Raspberry Pi.
## System Behavior
- **Auto-start** on boot using cron
- Designed for both **headless** mode and **interactive** via GUI with Raspberry Pi Connect
- **Monitor** detections and key system health indicators (CPU, temp, SD usage, uptime
- Logs locally in `data/logs/`)
- Save images in `data/images`: original jpg, annotated jpg, and txt with `<class_id> <x_center> <y_center> <width> <height>`

### Installing vespCV
Refer to `README.md` for the installation procedure to set up vespCV in the `vespCV` folder. This includes creating a launch script named `start_vespcv`:

1. **Create the launch script**:
   ```bash
   nano /home/vcv/start_vespcv
   ```

2. **Copy and paste the following lines into the file**:
   ```bash
   #!/bin/bash

   # Change to the vespCV directory
   cd /home/vcv/vespcv

   # Activate the virtual environment
   source venv/bin/activate

   # Set display for GUI
   export DISPLAY=:0

   # Add the project root to PYTHONPATH
   export PYTHONPATH=/home/vcv/vespcv:$PYTHONPATH

   # Start the application using the virtual environment's Python
   /home/vcv/vespcv/venv/bin/python src/core/main.py
   ```

3. **Save the file** by pressing:
   - `Ctrl + X`
   - Press `Y` to confirm
   - Press `Enter` to save

4. **Make the script executable**:
   ```bash
   chmod +x /home/vcv/start_vespcv
   ```

## Autostart Configuration
To set up the application to start automatically after powering on the Raspberry Pi:

1. **Open the crontab editor**:
   ```bash
   crontab -e
   ```

2. **Add the following line to start the application at boot**:
   ```bash
   @reboot sleep 30 && /home/vcv/start_vespcv >> /home/vcv/vespcv/data/logs/startup.log 2>&1
   ```
   The `sleep 30` command ensures the system is fully booted before starting the application.

## Key Libraries and Frameworks
- **OpenCV**: For image processing tasks.
- **PyTorch**: For running the YOLO model.
- **Ultralytics**: For YOLOv11s implementation.
- **Tkinter**: For the graphical user interface.
- **RPi.GPIO**: For GPIO control on the Raspberry Pi.

## Configuration Management
- Configuration settings are loaded from `config/config.yaml` file, ensuring that all required parameters are validated before the application runs.

## Error Handling
- The system includes error handling for various scenarios, such as:
  - Image loading errors
  - Detection errors
  - GPIO operation errors

