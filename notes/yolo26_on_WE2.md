**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---

**TASK: Port YOLO26n int8 to Grove Vision AI V2 (Himax WE2 / Ethos-U55)**

**Context:**

- **Hardware:** Grove Vision AI V2 (Cortex-M55 + Ethos-U55).
    
- **Baseline:** `tflm_yolo11_od` firmware.
    
- **Model:** YOLO26n TFLite (Vela-optimized).
    
- **Issue:** 18000 FPS (NPU is skipping execution), 0 detections.
    

**Constraint: [2026-02-10] Prevent hallucination. State verified facts. Answer only from context.**

**Phase 1 — Structural Audit**

1. **Model Specs:** YOLO26n is `int8[1, 8, 1029]`.
    
    - Scale: `0.0043815`, ZP: `-128`.
        
    - 8 channels = 4 box (xywh) + 4 classes.
        
2. **Post-Process Implementation:**
    
    - Locate the YOLO11 post-process. It expects `[1, 84, 756]`.
        
    - **Crucial:** YOLO11 uses DFL (Distribution Focal Loss). YOLO26 does **not**. Identify where the firmware performs softmax/integration on box coordinates and mark it for removal.
        
3. **Hardware Sanity:** Check `model_setup.cpp`. Verify the `tensor_arena` is large enough for the YOLO26 graph.
    

**Phase 2 — Numeric Validation**

1. Add a debug hook to print the first 16 bytes of the raw output tensor after `Invoke()`.
    
2. Compare these raw bytes against the expected `int8` range. If all bytes are `0` or `-128`, the NPU/Vela graph is failing at the hardware level.
    

**Phase 3 — Minimal Compatibility Layer**

1. **Update Offsets:** Change the loop from `756` (anchors) to `1029`.
    
2. **Remove DFL Logic:** Replace the complex YOLO11 box decoding with a direct dequantization: `(val - zero_point) * scale`.
    
3. **Layout Mapping:** Ensure you aren't reading the tensor "sideways" (transpose check).
    
4. **NMS Bypass:** Since YOLO26 is NMS-free, check if the firmware's NMS can be set to a `0.99` IoU threshold to prevent it from stripping valid detections.
    

**Deliverables:**

- Explanation of why the FPS was 18000.
    
- A `diff` for the post-processing C++ file.
    
- Updated constants for `SCALE`, `ZERO_POINT`, and `NUM_ANCHORS`.