```python
# Input: test USB camera
# Output: capture photo every 5 seconds and save it to images if a VVN is detected
# Goal: simulate functions on RPI
# Note: q only works when not switching to other applications

import os
import cv2
import torch
import numpy as np
from ultralytics import YOLOv10 as YOLO
import time

# Load the YOLOv10 model
model = YOLO('content_data3000_24-09-20/content/runs/detect/train/weights/last.pt')

# Set up the USB camera
camera_index = 0  # Default camera index (change if using a different camera)
video_capture = cv2.VideoCapture(camera_index)

# Verify camera initialization
if not video_capture.isOpened():
    print("Error: Could not open camera.")
    exit()

# Get camera resolution properties
frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Configuration variables
image_capture_interval = 5  # Time between captures in seconds
last_capture_time = time.time()  # Initialize timer

# Create directory for storing captured images
image_folder = "images"
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Initialize display window with blank image
cv2.imshow('Camera Feed', np.zeros((100, 100, 3), dtype=np.uint8))

# Initialize frame counter for tracking
frame_count = 0

# Main processing loop
while True:
    # Check if it's time to capture a new frame
    if time.time() - last_capture_time >= image_capture_interval:
        # Capture a single frame from the camera
        ret, frame = video_capture.read()
        if not ret:
            break

        # Run object detection on the captured frame
        results = model(frame)[0]

        # Initialize detection flag for this frame
        class_0_now_detected = False

        # Process each detection in the frame
        for result in results.boxes.data.tolist():
            # Extract detection information: [x1, y1, x2, y2, confidence, class]
            x1, y1, x2, y2, conf, cls = result[:6]
            
            # Check if we detected class 0 with high confidence
            if cls == 0 and conf > 0.7:
                class_0_now_detected = True

                # Save frame if confidence is very high (≥ 0.77)
                if conf >= 0.77:
                    # Generate timestamp for unique filename
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    image_name = f"VVN_{timestamp}.jpg"
                    image_path = os.path.join(image_folder, image_name)
                    cv2.imwrite(image_path, frame)
                    print(f"Saved image: {image_path}")

        # Increment frame counter and print progress
        frame_count += 1
        print(f'Processed frame {frame_count}')

        # Resize frame for display (25% of original size)
        resized_frame = cv2.resize(frame, (int(frame_width * 0.25), int(frame_height * 0.25)))

        # Show the resized frame
        cv2.imshow('Camera Feed', resized_frame)

        # Update the last capture time
        last_capture_time = time.time()

    # Check for 'q' key press to quit
    # Note: This only works when the window is in focus
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up resources
video_capture.release()  # Release the camera
cv2.destroyAllWindows()  # Close all OpenCV windows

print(f'Finished processing.')