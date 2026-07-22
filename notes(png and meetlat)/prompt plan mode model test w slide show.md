**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---

after grill-me
```
You are operating in plan mode. Follow these instructions exactly for every response you give.

**Instructions for cursor.ai in plan mode (The Rules):**
1. Strict Factuality: Only include verified steps. If a process is not standard or verifiable, mark it as `[to be verified]`.
2. Safety First: Do not suggest destructive commands (delete/overwrite/remove) without a clear, bold warning about data loss.
3. Plain English: Use simple wording and short sentences.
4. Concise Structure: Use a high-level table or bullet list. Skip intro/outro filler.
5. Context-Driven: Use only facts from this session or cited sources. Do not invent tools/behaviors.

**Objective:**
Create a safe, simple Python experiment script that runs a slideshow of 388 test images on screen using the existing `scripts/image_slider_web` service, reads live WE2/Grove Vision AI V2 serial `INVOKE` detections from the camera-on-screen setup, and compares class sets only (not box positions, not instance counts) against ground truth.

**Exact experiment decisions (must be enforced):**
- Use live camera hardware path only. Do not send JPEG files directly to device.
- Pair each shown image to detections using timestamp matching between slideshow events and serial lines.
- Compare set of GT classes vs set of predicted classes per image.
- Per-class TP/FP/FN must be presence-based per image/class.
- Apply runtime confidence threshold using `conf >= 0.30` (include exactly 0.30; do not use `>`).
- Build predicted class sets using only detections with `conf >= 0.30`.
- Save raw per-detection confidence values so threshold sweeps can still be done offline later.
- Keep raw detections in logs even when they are below threshold.
- On missing `INVOKE` for an image within timeout: treat as empty prediction set and continue.
- `NUL` is allowed as background class.
- For `NUL` images, derive `NUL` GT from filename token when appropriate (files matching `vvv_sss*.jpg` with `sss=NUL`).
- Ask model name at run start and write outputs to a new folder per run: `outputs/<yyyy-mm-dd_HHMMSS>__<model_name>/`.
- Overall metric is exact set match rate only.
- Also report per-class precision/recall from TP/FP/FN as diagnostics (use `NA` when denominator is zero and include support counts).
- Always process all 388 images per model run.
- If the same class is detected multiple times in one image, count class presence once for set comparison.
- For images that may contain 2+ species, keep standard set logic and allow manual user inspection workflow.
- Detection window policy: use strict fixed frame window and sample at 0.5s, 1.0s, and 1.5s after image display start.
- Sampling policy: for each sampling point use nearest valid detection event within ±200 ms; if none, mark sample missing. Tie-break by choosing earlier timestamp.
- Duplicate handling: within a sample point reduce same class to max confidence before averaging.
- Set-membership rule: predicted class presence based on any detection with `conf >= 0.30` in frame window.
- Frame rule: use half-open windows `[t0, t0+2.0)`.
- Fixed grace: 150 ms after frame end.
- Late serial policy: reassign only if timestamp falls in next frame window; otherwise drop and log as unmatched event.
- Timeout policy: based on absence of valid parsed detection events. Declare at frame end + 150 ms.
- Export `review_candidates.csv` containing all images needing manual review (mismatches + multi-species + timeouts).
- Default deterministic image order (sorted); optional shuffle with seed 42.
- Serial parse rule: reject partially malformed `INVOKE` lines entirely and count parse errors.
- Use host-side timestamps for both slideshow and serial events.
- Ignore class IDs outside 0-3 for scoring; log as `unknown_class_id`.
- Fail fast and stop run on missing label file, ambiguous filename, or `NUL` filename vs label conflict.
- Save `run_config.json` per run with all settings (threshold, seed, windows, grace, etc.).

**The Plan:**

| Step | What to do |
|------|----------------------------|
| 1 | Load the 388 images and matching label files from the exact task paths. Parse only class IDs from labels for GT classes. |
| 2 | Parse slideshow filename tokens and support `NUL` as background class. Use exact class mapping: `0=amel, 1=vcra, 2=vespsp, 3=vvel`. |
| 3 | Start run by asking for flashed model name. Create a new output folder with timestamp + model name. |
| 4 | Start and use `scripts/image_slider_web` for slideshow display/timing (2s cadence). Ingest timestamped “image shown” events. Use deterministic order by default (seed 42 if shuffling). |
| 5 | Read serial `INVOKE` lines from WE2/GV2 (hardcoded to `/dev/cu.usbmodem*`). Extract predicted class IDs and confidences. |
| 6 | Match detections to shown images by strict timestamp windows using the sampling points. Only `conf >= 0.30` detections contribute to predicted sets. |
| 7 | For each image, build GT class set and predicted class set (thresholded). Classify as complete/partial/no match. |
| 8 | Update running per-class TP/FP/FN using presence-only logic across all 388 images. |
| 9 | Save per-image CSV rows (with all flags) + `review_candidates.csv` + `run_config.json`. |
| 10 | Print final summary table with per-class metrics and overall exact set-match rate. |

**Safety/Verification Check:**
- `[to be verified]` Exact WE2 `INVOKE` serial line format and parser robustness.
- No delete/overwrite/remove operations allowed.
- Write outputs only to new run folders.
- Use only provided paths/class mapping/model names from the task.
- Class mapping is fixed and guaranteed: `0=amel, 1=vcra, 2=vespsp, 3=vvel`.
```




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