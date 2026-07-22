**One-line purpose:** 
**Short summary:** plan as made by grok
**Agent:** deployment failed and archived in himax_yolo26.zip
**Index:** [[_himax sdk]]

---

You are an expert AI coding assistant integrated with Cursor.ai, specializing in embedded systems, computer vision, and deploying ML models on edge devices like the Grove Vision AI V2 (based on Himax WE2 Plus). Your goal is to safely and efficiently modify code repositories to enable model deployment, with a focus on debugging, optimization, and clear documentation. Always prioritize safety by adding error checks, input validation, and fallback mechanisms (e.g., safe default configurations and recovery modes) to prevent device bricking or unsafe operations. Ensure all changes are backwards-compatible where possible, and document them in comments, README updates, and simple explanations for non-technical users—avoid jargon or explain terms like "NMS" (Non-Maximum Suppression: a step to filter overlapping detection boxes) and "IoU" (Intersection over Union: a measure of how much two boxes overlap, often used in thresholds like 0.45).

### Task Overview

Create a detailed Cursor.ai plan to adjust the Himax GitHub repository (forked from the official Himax WE2 Plus repo at [https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2), specifically the EPII_CM55M_APP_S directory) to support flashing a YOLO26n model onto the Grove Vision AI V2. This involves integrating support for the YOLO26 architecture, which is NMS-free and differs from YOLO8 and YOLO11 in output structure and processing. Base modifications primarily on the YOLO8 implementation (e.g., tflm_yolov8_od), and cross-reference YOLO11 (e.g., tflm_yolo11_od) only to identify and note differences, such as no-post-processing support in YOLO11. Pay special attention to debugging issues like "multiple boxes per object" (caused by insufficient filtering of overlapping detections) and "mixed classes per object" (where an object gets assigned multiple class labels incorrectly), stemming from candidate collection, NMS handling (not needed in YOLO26), and result structuring in the three-output flow.

Note: YOLO26's changes (e.g., native NMS-free design) may make full compatibility challenging on this hardware—include safety checks to test incrementally and revert if issues arise. If deployment proves impossible, document alternatives like falling back to YOLO8/YOLO11 or exploring YOLOv10 similarities (e.g., NMS-free aspects, but YOLO26 further removes DFL for simpler inference).

### Key Differences Between YOLO26, YOLO8, and YOLO11

- **YOLO26 Key Features** (Optimized for edge devices like Grove Vision AI V2):
    - **DFL Removal**: Eliminates Distribution Focal Loss, simplifying the model for better hardware compatibility and faster inference on low-power devices—reduces export complexity compared to YOLO8/YOLO11.
    - **End-to-End NMS-Free Inference**: Outputs direct predictions without a separate NMS step, lowering latency. Unlike YOLO8 (which requires NMS post-processing) and YOLO11 (which may include optional no-post variants), YOLO26 generates filtered results natively.
    - **Refined OBB Decoding**: Improves accuracy for square objects via specialized angle loss, resolving boundary issues—may require adjustments in box decoding code.
- **Comparison to YOLO8/YOLO11**:
    - YOLO8: Anchor-based with NMS; outputs need post-processing. Use as primary base for modifications.
    - YOLO11: Anchor-free with decoupled heads; has no-post-processing examples in the repo. Check for differences like output tensor handling or quantization tweaks, but prioritize YOLO8 code.
    - YOLO26 Similarities to YOLOv10: Both NMS-free, but YOLO26 adds DFL removal and optimizations (e.g., ProgLoss for training stability). Research shows unresolved issues in Ultralytics repos (e.g., [https://github.com/ultralytics/ultralytics/issues/13314](https://github.com/ultralytics/ultralytics/issues/13314) for TFLite INT8 conversion challenges; [https://github.com/ultralytics/ultralytics/issues/23228](https://github.com/ultralytics/ultralytics/issues/23228) noting IoU args are deprecated in newer models).

We have two TFLite models (object detection, trained on 4 classes: 0=amel, 1=vcra, 2=vespsp, 3=vvel; do not use COCO80; exported with YOLO INT8 and compiled with Vela):

- **NO_POST Model (Preferred, 2 MB)**: Path: /Users/md/Developer/vespa_smart_trap/yolo26_models/yolo26n_vespa2026-02v1_allpx_224_full_integer_quant_vela_nopost.tflite
    - Inputs: serving_default_images:0 (int8[1,224,224,3], Image(RGB), quantization: 0.003921568859368563 (q + 128))
    - Outputs (three heads, direct predictions: coordinates, class labels, confidence):
        - PartitionedCall:2 (int8[1,28,28,8], quantization: 0.13863390684127808 (q - 69))
        - PartitionedCall:1 (int8[1,7,7,8], quantization: 0.11222201585769653 (q - 80))
        - PartitionedCall:0 (int8[1,14,14,8], quantization: 0.1598438322544098 (q - 85))
- **No_NMS Export**: /Users/md/Developer/vespa_smart_trap/yolo26_models/yolo26n_vespa_allpx_224_no_nms_full_integer_quant_vela.tflite (same Netron outputs as NO_POST; no expected fixes from this).
- **POST Model**: 3.6 MB (too large for Grove Vision AI V2; avoid).

Use the NO_POST version, as YOLO26's NMS-free design aligns with no post-processing.

### Debugging Focus (Simplified for Non-Technical Users)

- **Multiple Boxes per Object**: Often from overlaps not filtered (low IoU threshold like <=0.45) or stale data in result slots. In YOLO26, since NMS-free, adjust candidate collection loop: derive boxes in top-left format from center-width-height, scale, apply thresholds (score >=0.25, IoU >0.45 for any manual filtering).
- **Mixed Classes per Object**: NMS (or equivalent) fails to pick the best class. In YOLO26, ensure class-agnostic handling selects highest-confidence class.
- **Causes & Safety Tips**: Old firmware, low thresholds, or outdated slots. Add error checks (e.g., validate output shapes before processing) and fallbacks (e.g., default to single-box mode if multiples detected).
- Debug Logging: Reference /Users/md/Developer/vespa_smart_trap/notes/yolo26_gv2_debug_flow_and_logging.md.
- Summary: /Users/md/Developer/vespa_smart_trap/notes/summary.md.

### What Was Done Before

- Copied /Users/md/Developer/vespa_smart_trap/himax_fork/EPII_CM55M_APP_S/app/scenario_app/tflm_yolo11_od to /Users/md/Developer/vespa_smart_trap/himax_fork/EPII_CM55M_APP_S/app/scenario_app/tflm_yolo26_od (multiple attempts, no effect).
- Executorch not available.
- No_NMS export tested, but outputs identical—no solution expected.

### Cursor.ai Plan (Step-by-Step for Safe Modifications)

Use Cursor.ai to implement changes incrementally. Start each step with safety validations (e.g., build/test on emulator before hardware). Document in README.md with simple explanations.

1. **Setup Fresh Clone**:
    - Copy /Users/md/Developer/vespa_smart_trap/himax_fork_backup to /Users/md/Developer/vespa_smart_trap/himax_fork_yolo26.
    - In Cursor.ai: Open the new folder, verify EPII_CM55M_APP_S exists. Add comment: "// Safety: Cloned fresh to avoid conflicts."
2. **Copy and Rename Base Directory**:
    - Copy EPII_CM55M_APP_S/app/scenario_app/tflm_yolov8_od to EPII_CM55M_APP_S/app/scenario_app/tflm_yolo26_od.
    - Rename files/references from "yolov8" to "yolo26". Cross-check with tflm_yolo11_od for no-post diffs (e.g., if YOLO11 skips NMS code, apply similar).
    - Safety: Add input validation in main.c (e.g., check model path exists or fallback to default model).
3. **Integrate Model**:
    - Create modelzoo/tflm_yolo26_od; copy NO_POST model there.
    - Update build scripts/makefile to include the new model (adjust paths, quantization params).
    - In inference code (e.g., tflm_interpreter.cpp): Modify output parsing for [1,x,x,8] tensors—decode boxes (cx,cy,w,h to top-left), apply dequantization, thresholds. Remove NMS calls (YOLO26 handles natively); if needed, add minimal class-agnostic filtering with IoU>0.45.
    - Cross-ref YOLO11: If it has no-post inference, borrow structure but note diffs in README.
    - Safety: Add error handling (e.g., if output shape mismatch, log error and exit gracefully).
4. **Adjust Build and Flash Steps**:
    - Update CMakeLists.txt/makefile for YOLO26: Set defines for 4 classes, 224x224 input, no NMS.
    - Build image: Run make/build commands; validate binary size <2MB limit.
    - Flash to device: Use provided tools; add pre-flash check (e.g., firmware version compatible).
    - Safety: Include fallback firmware load if flash fails.
5. **Debug and Optimize**:
    - Test for multiple/mixed issues: Run inference loop, log outputs (use debug.md notes).
    - If multiples: Increase threshold to 0.3; clear stale slots.
    - If mixed: Ensure highest-confidence class selected per group.
    - Optimize: Reduce latency with direct predictions; test on hardware.
    - If impossible: Document in README (e.g., "YOLO26 NMS-free may require firmware update; fallback to YOLO8").
6. **Documentation and Testing**:
    - Update README.md: Simple steps for users (e.g., "Run this command to build"), explain changes.
    - Test: Incremental builds, emulator first, then device. Add unit tests for box decoding.