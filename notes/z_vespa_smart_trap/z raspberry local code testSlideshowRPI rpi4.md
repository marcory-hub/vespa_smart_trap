**One-line purpose:** code for raspberry
**Short summary:** test usb cam images
**Agent:** archived

---


to test torch and ultralytics installation
copy hornet3000.m4v

# Save Images
```python
# Use a slideshow in .m4v as surrogate for the camera to test the model
# Output is in images without boundingboxes, classes and conficence scores
# Can be used to test the model and saving of the images 

import cv2
import torch
from ultralytics import YOLOv10 as YOLO
import time

# Load the YOLOv10 model
model = YOLO('content_data3000_24-09-20/content/runs/detect/train/weights/last.pt')

# Load the video file
input_video_path = '/Users/md/Developer/vespCV/test/dataSlider/hornet3000.m4v'

# Open the video using OpenCV
video_capture = cv2.VideoCapture(input_video_path)

# Get video properties
frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(video_capture.get(cv2.CAP_PROP_FPS))
total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

# Define variables
class_0_detected = False
last_class_0_time = None  # Time when class 0 was last detected
cooldown_time = 5  # Cooldown in seconds
previous_conf = 0  # Previous confidence score for class 0
detection_start_time = None  # Time when confidence first exceeds 0.77
threshold_duration = 0.04  # 10 ms = 0.01 seconds

# Iterate over each frame
frame_count = 0
while video_capture.isOpened():
    ret, frame = video_capture.read()  # Read a frame
    if not ret:
        break

    # Apply YOLOv10 object detection
    results = model(frame)[0]

    # Check for class 0 detection with high confidence
    class_0_now_detected = False  # Reset class detection for each frame
    for result in results.boxes.data.tolist():  # Each detection in format [x1, y1, x2, y2, conf, class]
        x1, y1, x2, y2, conf, cls = result[:6]
        if cls == 0 and conf > 0.7:  # If class 0 is detected
            class_0_now_detected = True
            
            # Check if confidence crosses the threshold (above 0.77)
            if conf >= 0.77:
                if detection_start_time is None:  # Start the timer when the confidence first crosses 0.77
                    detection_start_time = time.time()
                elif (time.time() - detection_start_time) >= threshold_duration:  # Check if it stays above 0.77 for 10 ms
                    if last_class_0_time is None or (time.time() - last_class_0_time) >= cooldown_time:
                        # Save frame as JPG with timestamp
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        image_name = f"VVN_{timestamp}.jpg"
                        cv2.imwrite(image_name, frame)
                        print(f"Saved image: {image_name}")
                        last_class_0_time = time.time()  # Update time of class 0 detection
                    detection_start_time = None  # Reset detection start time after saving the image
            else:
                detection_start_time = None  # Reset if confidence drops below 0.77
            previous_conf = conf  # Update previous confidence score
            break

    if not class_0_now_detected:
        previous_conf = 0  # Reset confidence if no class 0 detected in the frame
        detection_start_time = None  # Reset detection timer if class 0 is no longer detected

    frame_count += 1
    print(f'Processed frame {frame_count}')

# Release resources
video_capture.release()
cv2.destroyAllWindows()

print(f'Finished processing video.')

```

# Save video with bounding boxes
```python
# Input: weights of the model and slideshow in .m4v as surrogate for the camera to test the model
# Output: a video with bounding boxes, classes and confidence score
# Goal: check installed dependencies and adjust the tresholds 

import cv2
import torch
from ultralytics import YOLOv10 as YOLO

# Load the YOLOv10 model, copy path to last.pt in folder weights
model = YOLO('content_data3000_24-09-20/content/runs/detect/train/weights/last.pt')  # or another version of YOLOv8 (e.g., yolov8s.pt for small)

# Load the video file
input_video_path = '/Users/md/Developer/vespCV/test/dataSlider/hornet3000.m4v'
output_video_path = 'test_hornet3000_24-09-20.mp4'

# Open the video using OpenCV
video_capture = cv2.VideoCapture(input_video_path)

# Get video properties
frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(video_capture.get(cv2.CAP_PROP_FPS))
total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

# Define the codec and create VideoWriter object to save output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec
out_video = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

# Iterate over each frame
frame_count = 0
while video_capture.isOpened():
    ret, frame = video_capture.read()  # Read a frame
    if not ret:
        break
    
    # Apply YOLOv8 object detection
    results = model(frame)[0]
    
    # Iterate through the detections and draw bounding boxes
    for result in results.boxes.data.tolist():  # Each detection in the format [x1, y1, x2, y2, conf, class]
        x1, y1, x2, y2, conf, cls = result[:6]
        label = f'{model.names[cls]} {conf:.2f}'
        
        # Draw bounding box and label on the frame
        if conf > 0.77: 
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 4)  # Bounding box
                cv2.putText(frame, label, (int(x1), int(y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Write the processed frame to the output video
    out_video.write(frame)
    
    # Print progress
    frame_count += 1
    print(f'Processed frame {frame_count}/{total_frames}')

# Release resources
video_capture.release()
out_video.release()
cv2.destroyAllWindows()

print(f'Output video saved to {output_video_path}')
```