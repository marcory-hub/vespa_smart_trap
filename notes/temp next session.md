**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---

# Context for next session (2026-03-05)

  

Paste this into your prompt so the AI knows the current state of the YOLO11 / YOLO26 WE2 firmware and what is still open.

  

---

  

## What was done (2026-03-04)

  

- **YOLO11 workflow:** Fixed and documented. Post-processing in `cvapp_yolo11n_ob.cpp` (tflm_yolo11_od) now:

- Maps the three TFLite outputs by spatial size (28→14→7) so Vela output order no longer breaks detection.

- Uses a single tensor arena (1061K), unconditional stride/anchor allocation in init, and proper free in deinit.

- **YOLO11:** Works correctly on device: one (or few) boxes per object, correct placement.

- **YOLO26 scenario:** Separate build with `APP_TYPE=tflm_yolo26_od`; same flash slot (0xB7B000), different `common_config.h` define (`YOLO26_OBJECT_DETECTION_FLASH_ADDR`). Post-processing is shared; the dispatcher selects YOLO26 by tensor shape (3 outputs × 8 channels, or 1 output `[1,8,1029]`).

- **YOLO26 bbox decode:** Updated to match Ultralytics `dist2bbox` (tal.py): 4 channels = (left, top, right, bottom) in grid units, anchor at (grid + 0.5). Formula: `cx = (anchor_x + (right-left)/2)*stride`, same for cy; `w = (left+right)*stride`, `h = (top+bottom)*stride`. Invalid boxes (w≤0 or h≤0) are skipped. NMS is called (`yolo11_NMSBoxes`) after collecting boxes.

- **Full reproduction steps:** Documented in `YOLO11_TO_WE2_REPRODUCTION.md` (all cvapp changes, main.c, tflm_yolo26_od copy/rename, web toolkit class labels).

- **Ultralytics version:** User uses 8.3.53 for pt → int8 TFLite → Vela. Recommendation: keep 8.3.53 for this pipeline unless a specific need to upgrade; re-validate export shapes if changing version.

  

---

  

## Open issue: YOLO26 – many boxes per object

  

- **Symptom:** YOLO26 on the WE2 still produces **many bounding boxes for a single object** (e.g. three overlapping detections for one “Aziatische hoornaar”: vespsp 37, vespsp 50, vespsp 54). In the preview, boxes can look like horizontal bars/lines rather than full rectangles.

- **What is already in place:** NMS is invoked in `yolo26_nopost_three_output_processing`; score threshold 0.25, NMS threshold 0.45 (from `cv_yolo11n_ob_init`). Bbox decode uses ltrb + anchor (grid+0.5) as above.

- **Possible causes to investigate:**

1. **Decode still wrong:** e.g. raw TFLite/Vela output might be in a different format (e.g. exp(ltrb), or different channel order), so boxes are mispositioned and NMS does not merge them (low IOU).

2. **NMS params:** 0.25/0.45 might be too loose for YOLO26; try raising score threshold (e.g. 0.4–0.5) or tuning NMS threshold.

3. **Quantization/dequant:** Scale/zero-point or indexing for the 8-channel (4 bbox + 4 class) tensor might be wrong for YOLO26, giving bad coordinates or scores.

4. **Stride/anchor index:** `stride_756_1[j]` and the mapping from linear index `j` to (dims_cnt_1, dims_cnt_2, output_data_idx) must match the same 28²+14²+7² layout used for YOLO11; any mismatch could duplicate or misplace boxes.

- **Screenshot:** User has a preview showing multiple overlapping yellow boxes and “vespsp” labels (37, 50, 54) on one insect; FPS 9.66, threshold 30.

  

---

  

## Files to look at for YOLO26 fix

  

- `EPII_CM55M_APP_S/app/scenario_app/tflm_yolo11_od/cvapp_yolo11n_ob.cpp` (and the same file under `tflm_yolo26_od/` if that scenario builds its own copy):

- `yolo26_nopost_three_output_processing`: ltrb decode, score/NMS, scaling.

- `cv_yolo11n_ob_init`: `modelScoreThreshold`, `modelNMSThreshold` passed to post-processing.

- Compare with Ultralytics export: for no_post YOLO26 (reg_max=1), confirm whether the 4 bbox channels are raw ltrb or e.g. exp(ltrb); adjust firmware decode if needed (see comment in code: “If export uses exp(ltrb)…”).

  

---

  

## Repo layout (relevant)

  

- **YOLO11 build:** `APP_TYPE = tflm_yolo11_od` in `EPII_CM55M_APP_S/makefile`; model at `YOLO11_OBJECT_DETECTION_FLASH_ADDR` (0x3AB7B000).

- **YOLO26 build:** `APP_TYPE = tflm_yolo26_od`; model at `YOLO26_OBJECT_DETECTION_FLASH_ADDR` (0x3AB7B000). See `app/scenario_app/tflm_yolo26_od/README_YOLO26.md` for build/flash steps.

- **Reproduction:** `YOLO11_TO_WE2_REPRODUCTION.md` in the same directory as this file.