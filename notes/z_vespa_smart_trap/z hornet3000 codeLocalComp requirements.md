

# Streamlined Requirements for hornet3000 Project

## Core Dependencies
opencv-python==4.10.0.84
torch==2.4.1
torchvision==0.19.1
ultralytics
pillow==10.4.0
numpy==2.1.1

## Optional Dependencies (if needed)
matplotlib==3.9.2  # For visualization
pandas==2.2.3     # For data handling
scipy==1.14.1     # For scientific computing

## Installation Instructions

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

2. Install the requirements:
   ```
   pip install -r requirements.txt
   ```

## Notes

- This requirements file includes only the essential dependencies needed for the hornet3000 project.
- The original requirements file included many macOS-specific pyobjc-framework dependencies that are automatically installed when using pyobjc on macOS.
- If you're running on macOS and need specific pyobjc functionality, you can install it separately:
  ```
  pip install pyobjc
  ```