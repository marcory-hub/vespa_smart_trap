**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---

# Plan: Slideshow of 388 test images with class-only evaluation

  

**Goal:** A slideshow that shows one test image per second, runs detection (using the same output format as the WE2 INVOKE JSON), and compares **predicted classes** (and optionally confidence per class) with **ground-truth classes** from the YOLO `.txt` labels. Bbox position is **not** evaluated—only class.

  

---

  

## 1. Inputs

  

- **388 test images** in YOLO layout, e.g.:

- `images/test/*.jpg` (or `images/val/` if the 388 are from val)

- One `.txt` per image in `labels/test/` (or `labels/val/`) with same base name

- **YOLO label format:** One line per object: `class_id x_center y_center width height` (normalized 0–1). Only `class_id` is used for this plan.

- **Class names:** 4 classes (e.g. amel, vcra, vespsp, vvel) — index 0..3.

- **Device output format (target):** Same as WE2 INVOKE JSON:

- `data.boxes`: array of `[x, y, w, h, score, target]`

- `target` = class index (0..3)

- `score` = confidence (e.g. 0–100 or 0–1 depending on firmware)

  

---

  

## 2. Detection source (two options)

  

### Option A — Local inference (recommended for 388 images)

  

- Run inference **on the host** for each of the 388 images so each image has a matching detection.

- Use the **same model** as on the WE2 (e.g. the `.tflite` or `.pt` used for WE2).

- Output must match the INVOKE format: list of boxes with `[x, y, w, h, score, class_index]`.

- Implementation: Python + TFLite Interpreter (or Ultralytics `model.predict()`), then convert to the same box format. No need for the physical WE2 or serial port.

  

### Option B — Live from WE2 (if device can be fed images)

  

- Only possible if there is a **tool or mode** that sends a single image (e.g. JPEG) to the WE2 and receives one INVOKE JSON back (e.g. over serial).

- If that exists: slideshow sends image N to the device, reads one INVOKE response, parses `data.boxes`, then advances to the next image after 1 second (or after response).

- If the WE2 only runs on its **camera** stream, Option B is not viable for “388 test images from disk”; use Option A.

  

---

  

## 3. Slideshow behaviour

  

1. **Load dataset**

- Enumerate all images in the test folder (e.g. `images/test/`); expect 388.

- For each image, load the corresponding `.txt` (same base name in `labels/test/`).

- Parse each `.txt`: collect ground-truth **class IDs** (first column of each line). Ignore x_center, y_center, width, height.

  

2. **Per image (once per second)**

- Display the image in a window (e.g. OpenCV `imshow` or a simple GUI).

- Run detection (Option A: local model; Option B: send to WE2 and read one INVOKE).

- Parse detection result into a list of `(class_index, confidence)` (and optionally bbox for drawing only).

- **Compare with ground truth (class only):**

- Define a rule, e.g.:

- **Image-level:** For each GT class in the .txt, check if that class appears in the detections (e.g. with confidence above a threshold). Or: “predicted set of classes” vs “GT set of classes” (e.g. match/mismatch, or count TP/FP/FN per class).

- **Object-level (optional):** For each GT object (each line), check if there is at least one detection with the same class (no bbox IoU). Count correct-class detections vs GT objects per class.

- Optionally show on screen:

- Ground-truth classes (from .txt).

- Predicted classes and confidence scores (from detection).

- Match/mismatch (e.g. “OK” / “Mismatch” or per-class TP/FP/FN).

- Advance to next image after 1 second (or after detection result if slower).

  

3. **Timing**

- Display 1 image per second. If inference takes longer than 1 s, either:

- Wait for inference then show for 1 s, or

- Show image immediately and update text when inference completes (still advance to next image every 1 s).

  

---

  

## 4. Output format to parse (WE2 INVOKE)

  

From the terminal output, the WE2 sends JSON like:

  

```json

{"type": 1, "name": "INVOKE", "code": 0, "data": {"count": 0, "algo_tick": [[41373392]], "boxes": [], "image": "<base64 JPEG>"}}

```

  

- **boxes:** Array of arrays: `[x, y, w, h, score, target]`.

- `target` = class index (0..3).

- `score` = confidence (check firmware: e.g. 0–100 or 0–1).

- **count:** Number of boxes (can be used to sanity-check length of `boxes`).

- For class-only evaluation, only `boxes[*][4]` (score) and `boxes[*][5]` (target) are needed.

  

If using **local inference**, the script should produce a structure that mirrors this (e.g. list of dicts or list of `[x,y,w,h,score,class_id]`) so the same comparison and display logic works.

  

---

  

## 5. Comparison logic (class only)

  

- **Input:** For one image:

- GT: set (or list) of class IDs from the .txt (one per line, first column).

- Pred: list of (class_id, confidence) from detection (from `boxes[*][5]` and `boxes[*][4]`).

- **Optional:** Apply a confidence threshold (e.g. 0.3 or 30) so that only detections above the threshold count as “predicted”.

- **Metrics (examples):**

- Per image: “GT classes” vs “predicted classes” (set comparison): match / partial / mismatch.

- Running totals: For each class (0..3), count TP, FP, FN across all 388 images (class-only: a TP = GT has that class and we predicted that class; no bbox overlap required).

- Do **not** use bbox position or IoU in this plan.

  

---

  

## 6. Implementation outline

  

- **Language:** Python.

- **Location:** e.g. `scripts/slideshow_388_test_class_eval/` (or under `himax/` if WE2-specific).

- **Dependencies:** OpenCV (or PIL) for display; serial + JSON if Option B; TFLite or Ultralytics if Option A.

- **Config:** Path to test images dir, path to labels dir, class names list, path to model (if Option A), serial port (if Option B), confidence threshold, display duration (1 s).

- **Output:** On-screen during slideshow; optionally log per-image and per-class stats to a CSV or JSON for later analysis.

  

---

  

## 7. Suggested order of tasks

  

1. **Dataset loader:** List 388 images, load corresponding .txt, parse GT class IDs per image.

2. **Detection path:** Implement Option A (local TFLite or Ultralytics) and convert output to INVOKE-like `boxes` (at least `[..., score, target]`).

3. **Comparison:** For one image, compute GT set vs predicted set (with optional confidence threshold); define match/mismatch and optionally TP/FP/FN per class.

4. **Slideshow loop:** For each image, show image, run detection, show GT and predicted classes + comparison, wait 1 s, next.

5. **Optional:** If a WE2 image-input tool exists, add Option B (send image, read INVOKE, parse boxes).

6. **Optional:** Log per-image and per-class stats; print or plot a short summary at the end (e.g. accuracy per class, overall class match rate).

  

---

  

## 8. Notes

  

- **388 test set:** From dataset_vespa_2026-02v1-4 (test=388). Confirm paths (e.g. `images/test/` and `labels/test/`) in your repo or dataset.

- **Empty boxes:** If the device often returns `"boxes": []`, the slideshow can still show the image and GT and display “No detections” so you can see how many images have no device output.

- **Class index consistency:** Ensure model/firmware class order (0=amel, 1=vcra, 2=vespsp, 3=vvel) matches the order in your YOLO `data.yaml` / training so that `target` in INVOKE matches the first column in the .txt files.