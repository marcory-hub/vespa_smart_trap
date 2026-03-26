**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---


```
**Objective:** Create a safe, simple Python script that runs a slideshow of 388 test images (this one already is made), object detection runs on grove vision ai v2. (the user flashes the models to the grove vision ai v2), and compares only the predicted classes (not box positions) against the ground-truth classes from the label files, using the same output style as the WE2 device.

**The Plan:**

|Step|What to do (in plain English)|
|---|---|
|1|Load the 388 test images and their matching label files. For each image, read the label file and collect only the class numbers (first number on each line) as the ground-truth list.|
|2|Set up detection : user installs the model to the grove vision (swift-yolo, yolo11n_allpx, -30px, -40px or 60px) the WE2 device and get the INVOKE reply back, use that instead.|
|3|For every image shown on the screen, WE2 run detection, pull out only the class numbers and confidence scores from the boxes, and (if chosen) ignore any detection below the confidence threshold. So you should know what image is shown on the screen and what is detected by the WE2|
|4|Compare the set of ground-truth classes with the set of predicted classes for that image. Show on screen whether they match completely, partially, or not at all, plus the lists of classes for both sides.|
|5| Every 2 sec a new image is shown on the screen, keep a running count of true positives, false positives and false negatives for each class across all 388 images.|
|6|At the end, print a short table of results per class and overall match rate. Save the per-image details and totals to a simple CSV file.|
|7|Use only the exact folder paths, class order (0=amel, 1=vcra, 2=vespsp, 3=vvel) and file names given in the task. Make the script easy to change the model path or confidence threshold at the top.|
Repeat for each model. Ask the user at the start of the experiment for the name of the model that is flashed.

**Safety/Verification Check:**

- [to be verified] Whether a tool or mode exists to send a single JPEG image to the WE2 device and receive one INVOKE JSON reply over serial (if it does not exist, the script must default safely to local Option A only and clearly state this).
- No commands that delete, overwrite, or remove any folders or files are allowed; all file writing must use new output folders only.
- All paths, class names, and model names must come exactly from the provided task description—nothing extra may be added or assumed.
```