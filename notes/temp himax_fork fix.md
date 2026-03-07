**Role:** Embedded Systems Engineer / AI Deployment Specialist **Objective:** Develop a high-fidelity plan to synchronize `himax_fork` with the verified YOLO11 logic found in `himax_test`. The goal is to produce identical bounding box outputs for a 224x224 YOLO11 model with zero post-processing differences.

---

### **CRITICAL CONSTRAINTS (Read First)**
- **Target Model:** YOLO11 only.
- **Scope Control:** Prohibit the migration of any YOLO26-specific logic or experimental code found in `himax_test`.
- **Data Integrity:** Do not use `rm -rf` or destructive overwrites on the base `himax_fork` until a verified backup is confirmed.
- **Code Style:** Remove all conditional pre-processor checks (`#ifdef`, etc.) for the YOLO11 implementation to ensure a deterministic execution path.

---

### **PHASE 1: Workspace & Environment Setup**

1. **Safety Backup:** Create a full recursive copy of `himax_fork` to `himax_fork_backup`.
    - _Warning:_ Proceeding without a backup risks permanent loss of the original repository state.
2. **Notes**: **CAVE** only read them and use them to check the list below. Information in these notes might be wrong!  
3. **Build Configuration:** * Locate `himax_fork/EPII_CM55M_APP_S/makefile`.
    - Verify/Set `APP_TYPE = tflm_yolo11_od`.
    - [to be verified]: Confirm if any other flags in the makefile conflict with the YOLO11 memory map.
### **PHASE 2: Core Logic Alignment (cvapp_yolo11n_ob.cpp)**

_Target File:_ `himax_fork/EPII_CM55M_APP_S/app/scenario_app/tflm_yolo11_od/cvapp_yolo11n_ob.cpp`

3. **Memory & Global Definitions:**
    - Set tensor arena/memory size to exactly `1061*1024`.
    - Standardize output grouping: Define `yolo11n_ob_output[6]` as a single contiguous array.
    - Declare `dim_total_size`, `stride_756_1`, and `anchor_756_2` as standard globals. **Strip all conditional logic surrounding these declarations.**
4. **Initialization Sequence:**
    - Hardcode the anchor matrix generation for strides 8, 16, and 32.
    - Ensure `dim_total_size` is initialized to 0 before the stride calculation loop.
    - Bind the 6 outputs in a direct loop (0-5) without conditional guards.
5. **Function Pruning:**
    - Identify and "un-gate" the Anchor Matrix and Softmax helper functions. They must be compiled in by default for this APP_TYPE.
    - **Anti-Hallucination Check:** Ensure no YOLO26 logic (e.g., different stride counts or larger anchor shapes) is pulled from `himax_test`.

### **PHASE 3: Post-Processing & Shape Verification**
6. **Tensor Mapping:**
    - Verify the processing loop strictly handles three output scales based on shapes (28x28, 14x14, 7x7).
    - Match the ordering and pointer arithmetic exactly to the `himax_test` reference.
### **PHASE 4: Build, Deploy & Validate**
7. **Clean Build:**
    - Navigate to `himax_fork/EPII_CM55M_APP_S`.
    - Execute `make clean` followed by the specific build command for the Grove V2.
    - [to be verified]: Confirm the exact compiler toolchain path is in the environment variables.
8. **Deployment:**
    - Generate the flash image.
    - Flash the model to `0xB7B000` and the App to `0x00000`.
    - _Warning:_ Incorrect addresses can brick the current application state. Double-check the memory map.
9. **Comparison Test:**
    - Run the inference using the standard 224x224 test image.
    - Compare raw bounding box coordinates against `himax_test` logs.
    - If a discrepancy exists, perform a `diff` specifically on the `cvapp` file logic.

---

### **Safety & Verification Summary**
- **[to be verified]:** Does the current `himax_test` use any specific compiler optimization flags (`-O3`, etc.) that need to be mirrored in the fork?

---
Verified:  the **flash addresses** (`0xB7B000`) are consistent with the latest Grove Vision AI V2 firmware