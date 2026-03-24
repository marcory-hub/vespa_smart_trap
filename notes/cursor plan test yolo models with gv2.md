**One-line purpose:** plan mode tips
**Short summary:** planmode workflow
**Agent:** go to [[gv2 yolo model test plan]]
**Index:** [[_experiment_vst]]
**SoT**: https://cursor.com/blog/agent-best-practices

---


from gemini
```md
Create a Python benchmarking suite for YOLO11n models on Grove Vision AI v2.

Hardware/Environment Context:

Device: Grove Vision AI v2 (connected via /dev/tty.usbmodem58FA1047631 @ 921600 baud).

Physical Setup: Camera is 10cm from the monitor.

Setup:
- 388 images located in data/test/images/.
- Filename Format: [view]_[class]_[id].jpg (e.g., top_amel_0143.jpg).
- Labeling Logic: >   - View is the first part (top, sid, oth).
 - Class is the second part (amel:0, vcra:1, vesp:2, vvel:3).

Software Requirements:

slideshow_server.py (Flask):

Create a minimal Flask app that serves a single HTML page.

The page should display an image at exactly 10cm width (use CSS pixels/mm to approximate).

Implement a POST endpoint /update_image that takes a file path and updates the image on the screen using WebSockets or simple AJAX polling.

benchmark_runner.py (Main Logic):

Initialization: Ask the user for the "Model Name" (e.g., "30px").

The Loop: Iterate through all 388 images.

Step A (Display): Tell the Flask server to show the current image.

Step B (Stabilization): Wait 1.0 seconds for the camera to settle and the inference to stabilize.

Step C (Serial Capture): Read the Serial port. Locate the most recent {"type": 1, "name": "INVOKE", ...} JSON object.

Step D (Parsing): Extract target and score from the boxes array. If boxes is empty, record it as "No Detection". If multiple boxes exist, take the one with the highest score.

Step E (Logging): Compare the target against the ground truth from the filename.

Metrics & Output:

After the 388 images, generate:

results_{model_name}.csv: Columns [Image_Path, Ground_Truth, Predicted, Score, Result].

A Confusion Matrix (4x4) printed to the terminal.

Accuracy, Precision, and Recall calculated per class.

Use pandas and scikit-learn (or matplotlib) for the matrix/stats if available.

Error Handling:

Handle SerialException if the device is unplugged.

Robustly parse the JSON; the GV2 output often contains raw image bytes (Base64) mixed with JSON—the script must isolate the JSON string correctly.

Please generate both files and a requirements.txt.
```


for grok
```
	   **Role:** You are a Prompt Architect specializing in safety, deployment of yolo11n on edge devices and non-technical clarity.


**Task:** Review this detailed prompt for cursor.ai agent to reate a Python benchmarking suite for YOLO11n models on Grove Vision AI v2.

---

**Role**
You are a helpful coding assistant working in strict "plan mode" only. Your specialty is safe, simple code for edge camera devices like the Grove Vision AI v2. You make the plan extremely concise. Sacrifice grammar for the sake of concision. You make small to-dos that one agent can code. 

**Task**
Write two small Python files plus a requirements.txt to test how well a picture-recognition models work on the Grove Vision AI v2 camera. Put all necessary files in experiments/gv2_yolomodel_test. Give me a list of unresolved questions to answer, if any in the Safety/Verification Check

**Hardware and setup details (Use these facts as ground truth. You may use standard Python libraries and common patterns.)**
- Device: Grove Vision AI v2, connected at /dev/tty.usbmodem58FA1047631 with speed 921600.
- Camera sits exactly 10 cm from the computer monitor.
- There are 388 test pictures inside the folder data/test/images/.
- Each picture name looks like: top_amel_0143.jpg or sid_vcra_0056.jpg.
- From the name you can tell the true answer: first word is the view (top, side (sid), or other (oth)), second word is the object type (amel = 0, vcra = 1, vesp = 2, vvel = 3).
- image size for the grove vision ai v2 model is 224x224px

**What the two files must do**
slideshow_server.py
- Starts a simple web page that shows one picture at a time.
- The picture on screen must be exactly Approximate 10 cm width using CSS (e.g., ~378px at 96 DPI) [to be verified by user on the first picture].
- Has one easy way for the other program to tell it “show this new picture file now”.
- Use a simple HTTP endpoint (e.g., localhost) for communication.

benchmark_runner.py
- First asks the user for a short model name (example: “30px”).
- Then goes through all 388 pictures one by one in random order (seed 42):
  1. Tells the web page to show the current picture.
  2. Shows the first picture 30 sec so user can adjust size to 10 cm and adjust the camera position
  3. For next images it waits exactly 1 second so the camera can settle.
  4. Reads the latest message from the Grove device over the serial connection.
  5. Finds the most recent JSON part that says “INVOKE”.
  6. Parses the serial message:
- Only process JSON objects where "name": "INVOKE".
- Ignore all other messages (like NAME?, VER?, etc.).
- Assume JSON appears as valid {...} blocks inside the serial stream.
- From data.boxes, read detections where each box looks like:
[x, y, width, height, score, class_id]
- The last value is the class_id (example: 3)
- The second-to-last value is the confidence score (example: 75)
- If multiple boxes exist, keep only the one with the highest score.
- If boxes is empty or missing, record “No Detection”.
- Example INVOKE message: `{"name": "INVOKE", "data": {"boxes": [[85,112,168,94,75,3]]}}` → class_id = 3, score = 75
- The second-to-last value is the confidence score (0–100).
- Optionally apply a confidence threshold (e.g., 50) [to be verified].
- If below threshold, treat as “No Detection”.
- The `image` field may contain large base64 data and should be ignored.
1. Compares the result with the true object type from the picture filename.
- After all pictures, creates:
  - A file called results_{model_name}.csv with columns: Image_Path, Ground_Truth, Predicted, Score, Result.
  - Prints a simple 4×4 confusion table in the terminal
  - Prints accuracy, precision, and recall for each of the four object types.
  - Prints accuracy, precision, and recall for each of the tree views (top, sid=side, oth=other)
- Uses plain helper libraries only if they are listed in requirements.txt.

**Extra safety rules for reading the device**
- Sometimes the device sends picture data mixed with the JSON. The code must carefully pick out only the JSON part.
- If the device is unplugged, stop gently with a clear message.

**Please generate both files and a requirements.txt.**

**Instructions for cursor.ai in plan mode (The Rules) – follow every one exactly**
1. Strict Factuality: Only include verified steps. If a process is not standard or verifiable, mark it as '[to be verified]'.
2. Safety First: Do not suggest destructive commands (e.g., "delete all," "force overwrite," or "remove folder") without a clear, bold warning about potential data loss.
3. No Jargon: Use plain English. Explain words like "API," "Backend," "Latency," or other technical terms in a short sentence. Explain any idea in one short sentence.
4. Concise Structure: Use a high-level table or bulleted list for the plan. Skip preambles/introductory filler and omit closing summaries.
5. Context-Driven: Only use the information provided in this session or from cited sources. Do not invent hypothetical tools or behaviors.
6. Prefer the simplest possible working solution over a complex or optimized one.

**Output Format for cursor agent – your entire reply must be exactly this and nothing else (no code, no extra text):**

- **Objective:** [One sentence goal]
- **The Plan:** [High-level steps in a table]
- **Safety/Verification Check:** [A list of any [to be verified] items or warnings]

--> save to workspace `.cursor/plans/`

---
end of the concept prompt
```

# for cursor

**Role**
You are a helpful coding assistant working in strict "plan mode" only. Your specialty is safe, simple code for edge camera devices like the Grove Vision AI v2. You make the plan extremely concise. Sacrifice grammar for the sake of concision. You make small to-dos that one agent can code. 

**Task**
Write two small Python files plus a requirements.txt to test how well a picture-recognition models work on the Grove Vision AI v2 camera. Put all necessary files in experiments/gv2_yolomodel_test. Give me a list of unresolved questions to answer, if any in the Safety/Verification Check

**Hardware and setup details (Use these facts as ground truth. You may use standard Python libraries and common patterns.)**
- Device: Grove Vision AI v2, connected at /dev/tty.usbmodem58FA1047631 with speed 921600.
- The YOLO model must already be deployed on the Grove Vision AI V2 by the users The benchmark only reads serial results — it never changes the device firmware.
- Camera sits exactly 10 cm from the computer monitor.
- There are 388 test pictures inside the folder data/test/images/.
- Each picture name looks like: top_amel_0143.jpg or sid_vcra_0056.jpg.
- From the name you can tell the true answer: first word is the view (top, side (sid), or other (oth)), second word is the object type (amel = 0, vcra = 1, vesp = 2, vvel = 3).
- image size for the grove vision ai v2 model is 224x224px

**What the two files must do**
slideshow_server.py
- Starts a simple web page that shows one picture at a time.
- The picture on screen must be exactly Approximate 10 cm width using CSS (e.g., ~378px at 96 DPI) [to be verified by user on the first picture].
- Has one easy way for the other program to tell it “show this new picture file now”.
- Use a simple HTTP endpoint (e.g., localhost) for communication.

benchmark_runner.py
- First asks the user for a short model name (example: “30px”).
- Then goes through all 388 pictures one by one in random order (seed 42):
  1. Tells the web page to show the current picture.
  2. Shows the first picture 30 sec so user can adjust size to 10 cm and adjust the camera position
  3. For next images it waits exactly 1 second so the camera can settle.
  4. Reads the latest message from the Grove device over the serial connection.
  5. Finds the most recent JSON part that says “INVOKE”.
  6. Parses the serial message:
- Only process JSON objects where "name": "INVOKE".
- Ignore all other messages (like NAME?, VER?, etc.).
- Assume JSON appears as valid {...} blocks inside the serial stream.
- From data.boxes, read detections where each box looks like:
[x, y, width, height, score, class_id]
- The last value is the class_id (example: 3)
- The second-to-last value is the confidence score (example: 75)
- If multiple boxes exist, keep only the one with the highest score.
- If boxes is empty or missing, record “No Detection”.
- Example INVOKE message: `{"name": "INVOKE", "data": {"boxes": [[85,112,168,94,75,3]]}}` → class_id = 3, score = 75
- The second-to-last value is the confidence score (0–100).
- Optionally apply a confidence threshold (e.g., 50) [to be verified].
- If below threshold, treat as “No Detection”.
- The `image` field may contain large base64 data and should be ignored.
1. Compares the result with the true object type from the picture filename.
- After all pictures, creates:
  - A file called results_{model_name}.csv with columns: Image_Path, Ground_Truth, Predicted, Score, Result.
  - Prints a simple 4×4 confusion table in the terminal
  - Prints accuracy, precision, and recall for each of the four object types.
  - Prints accuracy, precision, and recall for each of the tree views (top, sid=side, oth=other)
- Uses plain helper libraries only if they are listed in requirements.txt.

**Extra safety rules for reading the device**
- Sometimes the device sends picture data mixed with the JSON. The code must carefully pick out only the JSON part.
- If the device is unplugged, stop gently with a clear message.

**Please generate both files and a requirements.txt.**

**Instructions for cursor.ai in plan mode (The Rules) – follow every one exactly**
1. Strict Factuality: Only include verified steps. If a process is not standard or verifiable, mark it as '[to be verified]'.
2. Safety First: Do not suggest destructive commands (e.g., "delete all," "force overwrite," or "remove folder") without a clear, bold warning about potential data loss.
3. No Jargon: Use plain English. Explain words like "API," "Backend," "Latency," or other technical terms in a short sentence. Explain any idea in one short sentence.
4. Concise Structure: Use a high-level table or bulleted list for the plan. Skip preambles/introductory filler and omit closing summaries.
5. Context-Driven: Only use the information provided in this session or from cited sources. Do not invent hypothetical tools or behaviors.
6. Prefer the simplest possible working solution over a complex or optimized one.

**Output Format for cursor agent – your entire reply must be exactly this and nothing else (no code, no extra text):**

- **Objective:** [One sentence goal]
- **The Plan:** [High-level steps in a table]
- **Safety/Verification Check:** [A list of any [to be verified] items or warnings]

--> save to workspace `.cursor/plans/`

[[gv2 yolo model test plan]]
