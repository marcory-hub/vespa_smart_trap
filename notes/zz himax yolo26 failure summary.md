**One-line purpose:** tests and results of yolo26 model on gv2
**Short summary:** technical failures, process and debugging gaps, chronological test summary
**Agent:** comprehensive reference for future YOLO26n deployment attempts
**Main Index:** [[_himax sdk]] 

---
### Primary Technical Failures

**1. Output Shape Incompatibility**
- YOLO26 single-output (post) models produce `[1,1029,8]` tensors but GV2 firmware expects `[1,8,1029]`
- Firmware dispatcher hits "branch=none" path leading to empty detection arrays
- Shape transposition attempts were made but never fully validated on-device

**2. Score Threshold Issues**
- Three-output (nopost) models produce `numOutputs=3` with correct grid dimensions `[28,28,8]`, `[14,14,8]`, `[7,7,8]`
- All candidate detections fail the 0.25 confidence threshold (`candidates=0`)
- Indicates either incorrect dequantization, wrong channel interpretation, or model producing low confidence logits

**3. Model Architecture Mismatch**
- YOLO26 firmware was derived from YOLO11 OD app, not YOLO8
- Despite YOLO26's advertised "NMS-free" capability, exported models still require traditional decode + NMS
- Current `*_nopost.tflite` models behave like one-to-many heads, not the expected end-to-end NMS-free format

### Secondary Issues
**4. NMS and Detection Quality**
- When detections were produced (earlier builds), multiple overlapping boxes per object persisted despite NMS tuning (IoU 0.45→0.35→0.25)
- Mixed class predictions on single objects (vcra/vvel/vespsp confusion)
- Class-agnostic NMS insufficient for multi-class accuracy

**5. Initialization and State Issues**
- `g_use_case != 0` condition caused interpreter initialization to be skipped
- Model loading issues indicated by `MODEL?` returning `0xFFFFFFFF`
- VER? timestamp issues requiring full clean builds

### Process and Debugging Gaps
Critical debugging steps were incomplete:
- Never confirmed which model path actually executes via `numOutputs` logging
- Post (single-output) path may have never been properly tested end-to-end
- No systematic channel layout verification between export and firmware decode
- Insufficient validation of score calculation and dequantization formulas

The root cause appears to be **incompatible tensor formats** between Ultralytics YOLO26 export and Himax/Seeed firmware expectations, compounded by **unvalidated model loading paths** and **inadequate confidence score processing**.

## Chronological Testing Summary
### Phase A: Initial YOLO26 Integration (Mar 7-8, 2026)
- Created `vespa-yolo26` branch from YOLO11 OD baseline
- Copied `scenario_app/tflm_yolo11_od` → `tflm_yolo26_od` and `model_zoo` directories
- Fixed single-output shape mismatch `[1,1029,8]` vs expected `[1,8,1029]` with indexing `c*8+ch`
- Resolved initialization skip bug with `g_use_case = 0` force
- **Result**: Firmware compiles but produces empty detection arrays

### Phase B: NMS Tuning and Debugging (Mar 8, 2026 - 18:04:11 build)
- Added configurable thresholds: `YOLO26_SCORE_THRESH` (0.25f), `YOLO26_NMS_IOU_THRESH` (0.45f→0.35f→0.25f)
- Implemented debug logging with pre-NMS sample boxes (indices 0, n/4, n/2, 3n/4, n-1)
- Added `YOLO26_BBOX_EXP_WH` option for exponential width/height decode
- Updated VER? timestamp handling to use build time instead of source mtime
- **Result**: INVOKE had 6-8 boxes per frame with multiple overlapping boxes and mixed classes (vcra/vespsp/vvel)

### Phase C: Empty Detection Debug (Mar 8, 2026 - 18:41:02 build)
- Created diagnostic logging to distinguish empty boxes vs wrong output format
- Documented model export differences: 3-output vs 1-output .tflite files
- Researched Seeed/Himax YOLO11 reference implementations and channel layouts
- Investigated ExecuTorch/Vela compilation pipeline compatibility
- **Result**: Serial logs show `numOutputs=3, candidates=0` - all scores below threshold, empty detection arrays

### Phase D: Display Fixes and Final Attempts (Mar 9, 2026 - 13:36:46 build)
- Attempted fixed-position bounding boxes at (0,0) for class display debugging
- Implemented top-2 class detection with 20% confidence rule
- Reverted to real bounding boxes for toolkit compatibility
- Final NMS parameter tuning with score threshold 0.35f and IoU threshold 0.30f
- **Result**: Toolkit display functional but underlying detection failure remains

## Untested Options (Additional Analysis)

### Critical Missing Tests
- **End-to-end post model validation**: Never confirmed single-output path actually executes with `numOutputs=1`
- **Channel layout verification**: No systematic check of LTRB vs w,h channel ordering between export and decode
- **Quantization parameter validation**: TFLite quantization scales/zero-points never cross-referenced with firmware dequant
- **Model loading verification**: Never confirmed .tflite file integrity or correct model address loading

### Export and Model Issues
- **True end-to-end YOLO26 export**: Never attempted explicit `(1,300,6)` single-head NMS-free export
- **Alternative export formats**: No testing of different YOLO26 head configurations or export parameters
- **Vela compilation validation**: Never verified Ethos-U55 optimization applied correctly to YOLO26 architecture
### Firmware Architecture Tests
- **YOLO8 vs YOLO11 baseline comparison**: Never tested YOLO26 adaptation from YOLO8 instead of YOLO11 foundation
- **Isolated tensor shape testing**: No standalone verification of tensor reshape and indexing operations
- **Score calculation debugging**: Never validated sigmoid vs clamp operations or channel-specific scoring
### System Integration Gaps
- **Host vs firmware box count correlation**: Never systematically compared `read_one_invoke_boxes.py` output to firmware logs
- **Memory and timing validation**: No verification of <2.4MB SRAM constraints or inference timing
- **Clean build validation**: Insufficient testing of VER? updates and complete firmware refresh cycles
## References
### Notes Files
- **`notes/yolo26_gv2_debug_flow_and_logging.md`**: Full flow analysis, diagnostic logging, and critical path code snippets
- **`notes/yolo26_three_output_flow.md`**: Export layout, bbox formula, and NMS configuration tables
- **`notes/yolo26_post_vs_nopost_vela_and_run_data.md`**: Model export differences, canonical PyTorch shapes, and YOLO8/YOLO11→YOLO26 strategy (§6)
- **`notes/post_vs_nopost_seeed_himax_gv2_research.md`**: Seeed/Himax reference implementations, channel layouts (LTRB vs ch 2,3 = w,h), scotty9000 commit analysis (§9.3)
- **`notes/executorch_why_how_vela_research.md`**: ExecuTorch background and Ethos-U/Vela compilation pipeline (TOSA → ethos-u-vela)

### Agent Transcripts (3-Day Period)
- [**YOLO26 Integration**](1d852d12-509a-4ea0-b5e7-15e3b18d5af2): Initial YOLO11→YOLO26 app creation, branch setup, single-output shape fixes
- [**YOLO26 Integration continued**](a2f8cee0-23c9-4eca-aed0-fecbf2126fce): Dispatcher branch implementation, g_use_case initialization fixes
- [**YOLO26n GV2 NMS and deployment**](e832d8de-8fa1-4d0e-87b2-3ce538656c71): NMS threshold tuning (0.45→0.35→0.25), debug logging, VER? timestamp issues
- [**YOLO26 Ethos‑U55 and Vela**](d7c583e9-25d3-4762-a975-7667427bce5d): Final debugging session (Mar 9, 13:36:46), NMS-free vs traditional decode analysis, Ethos-U55 compatibility verification
- [**YOLO26n Processing**](ceea1c26-3734-4be9-b654-f0cbd8776f11): Additional processing attempts and debugging
- [**GV2 Configuration**](59039441-2769-4be3-bd92-1b58d685fd55): Hardware configuration and final parameter tuning
### Key Files Modified
- **Firmware**: `himax_fork/EPII_CM55M_APP_S/app/scenario_app/tflm_yolo26_od/cvapp_yolo26_ob.cpp` (main post-processing)
- **Build System**: `himax_fork/EPII_CM55M_APP_S/app/scenario_app/tflm_yolo26_od/tflm_yolo26_od.c` (initialization fixes)
- **Debug Scripts**: `scripts/gv2_invoke_check/read_one_invoke_boxes.py` (box count verification)
### External Research
- **Ultralytics Issues**: #9150 (NMS IoU thresholds), #6429 (overlapping boxes), #18638 (TFLite dequant matching)
- **Reference Implementations**: HimaxWiseEyePlus/YOLO11_on_WE2, scotty9000/Seeed_Grove_Vision_AI_Module_V2 (commit 3c7cf77)
---

## Technical Debugging Details (Preserved from Cursor Notes)

### YOLO26 Firmware Flow and Code Snippets

**End-to-end Detection Pipeline:**

tflm_yolo26_od.c → cv_yolo26_ob_run() → yolo26_ob_post_processing() → yolo26_three_output_processing()

**Critical Path Selection Logic** 
```cpp
(`cvapp_yolo26_ob.cpp` ~909–956):
```cpp
static void yolo26_ob_post_processing(...) {
    int numOutputs = static_interpreter->outputs_size();
    if (numOutputs == 1) { ... single-output ... return; }
    if (numOutputs == 3) {
        if (out0->dims->data[3] == 8 && ... && r0 != r1 && r1 != r2 && r0 != r2) {
            yolo26_three_output_processing(o28, o14, o7, ...);
            return;
        }
        yolo26_zero_all_obr(alg);
        return;
    }
    yolo26_zero_all_obr(alg);
}
```

Score Calculation and Threshold (`cvapp_yolo26_ob.cpp` ~382–399):
```cpp
float max_score = vals[4];
uint16_t max_class = 0;
for (int k = 5; k < 8; k++)
    if (vals[k] > max_score) { max_score = vals[k]; max_class = (uint16_t)(k - 4); }
float score = (max_score <= 1.f && max_score >= 0.f) ? max_score : sigmoid(max_score);
if (score < modelScoreThreshold) continue;  // 0.25
```

Class Mapping: 0 = amel, 1 = vcra, 2 = vespsp, 3 = vvel (vals[4..7] → classes 0..3)

Critical Exit Condition: When no cell has score ≥ 0.25, `boxes` stays empty and we return before NMS. The log `yolo26_three NMS pre=%d post=%d filled=%d` is only reached when `!boxes.empty()`.

### Original YOLO26 Task Specification

Hardware: Grove Vision AI V2 (Cortex-M55 + Ethos-U55) Baseline: `tflm_yolo11_od` firmware  
Model: YOLO26n TFLite (Vela-optimized) Issue: 18000 FPS (NPU skipping execution), 0 detections

Model Specs: YOLO26n is `int8[1, 8, 1029]`

- Scale: `0.0043815`, ZP: `-128`
- 8 channels = 4 box (xywh) + 4 classes
- Crucial difference: YOLO11 uses DFL (Distribution Focal Loss), YOLO26 does not

Key Debugging Phases:

1. Structural Audit: Verify post-process implementation, check tensor_arena size
2. Numeric Validation: Debug hook to print raw output tensor bytes
3. Minimal Compatibility Layer: Update offsets from 756 to 1029, remove DFL logic, layout mapping

### Debugging Scripts

Box Count Verification Script (`scripts/gv2_invoke_check/read_one_invoke_boxes.py`):

- Purpose: Compare host box count with firmware debug log (yolo26_three NMS post=/filled=)
- Usage: `python read_one_invoke_boxes.py --port PORT --timeout SECONDS`
- Default port: `/dev/tty.usbmodem58FA1047631` (921600 baud)
- Output format: `[x, y, w, h, score, target]` for each detected box

### Hypotheses for Empty Boxes

1. Three-output path not taken – numOutputs ≠ 3 or dims don't match (grid sizes not exactly 28, 14, 7 or channels ≠ 8)
2. All scores below 0.25 – Wrong dequant/scale, wrong channel interpretation, or model not producing confident logits
3. Model not loaded – MODEL? returning 0xFFFFFFFF suggests invalid model address
4. Input preprocessing – Resize or int8 shift (-128) making input unsuitable

### Diagnostic Logging Strategy

In `yolo26_ob_post_processing()`:

- Log `numOutputs` at start
- Log output grid dims `r0,r1,r2` when entering three-output branch
- Log unsupported layout cases

In `yolo26_three_output_processing()`:

- Log `yolo26_three candidates=%d` before `if (boxes.empty()) return;`
- This distinguishes: (a) path taken but scores below threshold vs (b) path not taken

Expected serial output patterns:

- `yolo26 post_processing numOutputs=3 r0=28 r1=14 r2=7` + `yolo26_three candidates=0` → path taken, no valid scores
- `yolo26 post_processing numOutputs=1` or `unsupported` → wrong path
- `yolo26_three candidates=N` + `yolo26_three NMS pre=N post=...` → normal flow

