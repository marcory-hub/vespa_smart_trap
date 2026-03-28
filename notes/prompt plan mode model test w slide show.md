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
1. **Strict Factuality:** Only include verified steps. If a process is not standard or verifiable, mark it as `[to be verified]`.
2. **Safety First:** Do not suggest destructive commands (delete/overwrite/remove) without a clear, bold warning about data loss.
3. **Plain English:** Use simple wording and short sentences.
4. **Concise Structure:** Use a high-level table or bullet list. Skip intro/outro filler.
5. **Context-Driven:** Use only facts from this session or cited sources. Do not invent tools/behaviors.

**Objective:**
Create a safe, simple Python experiment script that runs a slideshow of 388 test images on screen, reads live WE2/Grove Vision AI V2 serial `INVOKE` detections from the camera-on-screen setup, and compares **class sets only** (not box positions, not instance counts) against ground truth.
Use the existing local slideshow service at `scripts/image_slider_web` as the image presentation source for timing and image display events.

**Exact experiment decisions (must be enforced):**
- Use **live camera hardware path only**. Do **not** send JPEG files directly to device.
- Pair each shown image to detections using **timestamp matching** between slideshow events and serial lines.
- Compare **set of GT classes** vs **set of predicted classes** per image.
- Per-class TP/FP/FN must be **presence-based per image/class**.
- Apply runtime confidence threshold using **`conf >= 0.30`** (include exactly 0.30; do not use `>`).
- Build predicted class sets using only detections with **`conf >= 0.30`**.
- Save raw per-detection confidence values so threshold sweeps can still be done offline later.
- Keep raw detections in logs even when they are below threshold.
- On missing `INVOKE` for an image within timeout: treat as **empty prediction set** and continue.
- `NUL` is allowed as background class.
- For `NUL` images, derive `NUL` GT from filename token when appropriate.
- Ask model name at run start and write outputs to a **new folder per run**: `outputs/<yyyy-mm-dd_HHMMSS>__<model_name>/`.
- Overall metric is **exact set match rate only**.
- Also report per-class precision/recall from TP/FP/FN as diagnostics.
- Always process all **388 images** per model run.
- If the same class is detected multiple times in one image, count class presence once for set comparison.
- For images that may contain 2+ species, keep standard set logic and allow manual user inspection workflow.
- Detection window policy per image: use a strict fixed frame window and sample at **0.5s, 1.0s, and 1.5s** after image display start. Average confidence per class across available samples in-window, then keep the class confidence representative with the highest averaged confidence for reporting.
- Sampling policy details: for each sampling point (0.5s, 1.0s, 1.5s), use the nearest valid detection event within **+-200 ms**; if none exists, mark that sample point as missing.
- Tie-break rule for nearest-event sampling: if two detections are equally near a sampling point, choose the earlier timestamp.
- Duplicate detection handling: within a sample point, if the same class appears multiple times, reduce to the class-wise maximum confidence before averaging across sample points.
- Set-membership rule: predicted class presence is based on **any** detection with `conf >= 0.30` in the frame window (not on averaged confidence thresholding).
- Threshold precision rule: apply threshold check on raw float confidence values first; round only for display/export.
- Frame assignment rule: use half-open frame windows **[t0, t0+2.0)** to prevent boundary double assignment.
- Fixed grace rule: use a fixed post-frame grace of **150 ms** for timeout and late-event handling.
- Late serial policy: reassign a detection only if its timestamp falls in the next frame window; otherwise drop it and log it as an unmatched event.
- Timeout policy: timeout is based on absence of valid parsed detection events, not on absence of serial traffic.
- Timeout declaration rule: declare timeout only at frame end (`t0+2.0s+150ms`) when no valid parsed detection events were assigned to the frame.
- Event ownership precedence: assign events to frames strictly by frame interval first, then apply sampling logic.
- Manual review artifact: export `review_candidates.csv` for mismatch and multi-species inspection (image filename, GT set, predicted set, raw detections, match type).
- Precision/recall denominator rule: output `NA` when denominator is zero, and include support counts.
- Ordering/reproducibility: default deterministic image order (sorted), with optional shuffle controlled by fixed seed **42**.
- Serial parse robustness rule: if an `INVOKE` line is partially malformed, reject the whole line and log a parse error counter.
- Clock-domain rule: use host-side timestamps for both slideshow events and serial receive events.
- Unknown class rule: if parsed class ID is outside `0..3`, ignore it for scoring and log as `unknown_class_id`.
- Label integrity rule: if an image label file is missing, fail fast and stop the run.
- `NUL` conflict rule: if filename implies `NUL` but label content contains non-`NUL` classes, treat as data integrity error and fail fast.
- Reproducibility artifact rule: save `run_config.json` per run (threshold, seed, sampling points, windows, grace, parser settings).
- Benchmark interaction rule: use strict locked benchmark mode so manual pause/next/restart controls are disabled during scored runs.

**The Plan:**

| Step | What to do (plain English) |
|---|---|
| 1 | Load the 388 images and matching label files from the exact task paths. Parse only class IDs from labels for GT classes. |
| 2 | Parse slideshow filename tokens and support `NUL` as background class. Use exact class mapping/order from task: `0=amel, 1=vcra, 2=vespsp, 3=vvel`, plus `NUL` background handling. |
| 3 | Start run by asking for flashed model name. Create a new output folder with timestamp + model name. |
| 4 | Start and use `scripts/image_slider_web` for slideshow display/timing (2s cadence). Emit/ingest timestamped “image shown” events from the slideshow flow. Use deterministic order by default; if shuffle is enabled, use seed 42. |
| 5 | Read serial `INVOKE` lines from WE2/GV2 while slideshow runs. Extract predicted class IDs and confidences in WE2 output style. Mark parser assumptions as `[to be verified]` if format is unclear. |
| 6 | Match detections to shown images by strict timestamp windows. Use sampling points at 0.5s, 1.0s, and 1.5s in the frame window; only detections with `conf >= 0.30` contribute to predicted sets. If no valid detection arrives in time, assign empty predicted set and mark timeout flag. |
| 7 | For each image, build GT class set and predicted class set (thresholded set logic). Classify result as complete match / partial match / no match. |
| 8 | Update running per-class TP/FP/FN using presence-only logic across all 388 images. |
| 9 | Save per-image rows (timestamps, filename, GT set, predicted set, raw confidences, thresholded confidences, timeout flag, unmatched-event flag, parse-error flag, match type) and aggregate totals to CSV. Save `review_candidates.csv` and `run_config.json`. |
| 10 | Print final summary table with per-class TP/FP/FN, per-class precision/recall, and overall exact set-match rate for the run. |

**Safety/Verification Check:**
- `[to be verified]` Exact WE2 `INVOKE` serial line format and parser robustness in this environment.
- Filename token rule for `NUL`: treat files matching `vvv_sss*.jpg` with `sss=NUL` as `NUL` GT.
- Fail-fast rule: if filename token parsing is ambiguous or invalid, stop the run with a logged warning.
- No delete/overwrite/remove operations allowed.
- Write outputs only to new run folders; do not reuse old output files.
- Use only provided paths/class mapping/model names from the task; do not invent extras.
- Class mapping is fixed and guaranteed: `0=amel, 1=vcra, 2=vespsp, 3=vvel`.
```


