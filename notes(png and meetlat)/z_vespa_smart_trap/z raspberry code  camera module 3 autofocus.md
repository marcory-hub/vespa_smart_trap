**One-line purpose:** code for camera module 3 to autofocus en fix focus 
**Short summary:** 
**Agent:** archived

---

Test de lensposition om deze daarna als vaste focus in te stellen:
```sh
libcamera-still -t 0 --autofocus-mode continuous --info-text "%lp"
```


# Camera Module 3 Setup and Testing Guide

### Basic Camera Test
```sh
# Test if camera is recognized
libcamera-hello
```

### Manual Focus Testing
```sh
# Test manual focus with specific parameters
libcamera-still --autofocus-mode manual --lens-position 7.0 --timeout 10000 --width 640 --height 640 --viewfinder-width 640 --viewfinder-height 640
```

#### Focus Position Guide
- Position 10: Close-up (approximately 10 cm)
- Position 1: Medium distance (approximately 1 meter)
- Position 0: Infinity

## Python Camera Control

### Manual Focus Control Script

```python
#!/usr/bin/env python3
"""
Simple script to test manual focus on Raspberry Pi Camera Module 3
Iterates through a predefined list of lens positions:
7 to 10 with 0.5 step size

To see what dioptry the autofocus has use this command

libcamera-still -t 0 --autofocus-mode continuous --info-text "%lp"

"""

import subprocess # To be able to use libcamera-still manual focus
import time

def test_manual_focus(lens_position=7.0, duration=10):
    """
    Test manual focus using libcamera-still command
    
    """
    print(f"Testing manual focus at position {lens_position} for {duration} seconds...")
    
    # Build the command for libcamera-still manual focus
    cmd = [
        "libcamera-still",
        "--autofocus-mode", "manual",
        "--lens-position", str(lens_position),
        "--timeout", str(duration * 1000),  # Convert to milliseconds
        "--width", "640",
        "--height", "640",
        "--viewfinder-width", "640",
        "--viewfinder-height", "640"
    ]
    
    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print("Focus test completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Test manual focus at position 7.0 for 10 seconds
    print("Testing focus at position 7.0...")
    time.sleep(10)  # Brief pause between showing the position
    test_manual_focus(7.0, 10)
    
    # Ask if user wants to test more positions
    response = input("\nI tested 7.0. \nDo you want to test for positions (6.0 to 10.0) also? (y/n): ")
    if response.lower() == 'y':
        # Test different focus positions
        positions = [6, 7, 8, 9, 10]  # 8.0, 9.0, 10.0
        for position in positions:
            print(f"Testing focus at position {position}...")
            time.sleep(10)  # Brief pause between showing the position
            test_manual_focus(position, 10)
            time.sleep(1)  # Brief pause between tests
    
    print("\nFocus testing complete!")
```


maak het executable
```sh
chmod +x testCamFocus.py
```

./picam2Focus.py
