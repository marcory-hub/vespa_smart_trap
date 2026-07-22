**One-line purpose:** comparison of changes made in the first clone with the upstream clone from himax
**Short summary:** 
**Agent:** AI generated
**Main Index:** [[_himax sdk]]

---

no_post_224 will give better accuracy than post_192
The absence of a 224×224 post model here is a deployment/memory trade-off choice, not a theoretical limitation of YOLO11. `[to be verified]`

[[himax forks yolo11 changes online]]
# himax_fork vs himax_test Comparison

Comparison of **himax_fork** with **himax_test/Seeed_Grove_Vision_AI_Module_V2** (aligned SDK structure). Only files not excluded by `himax_fork/.gitignore` are considered. No code was modified.

**Ignored (per himax_fork/.gitignore):** `*.d`, `*.o`, `*.obj`, `*.slo`, `*.lo`, `*.gch`, `*.pch`, `*.so`, `*.dylib`, `*.dll`, `*.mod`, `*.smod`, `*.lai`, `*.la`, `*.lib`, `*.exe`, `*.out`, `*.app`, `*.elf`, `*.map`, `*.img`, `EPII_CM55M_APP_S/obj_*/**`, `we2_image_gen_local/output_*/**`, `we2_image_gen_local/Images*.txt`, `.vscode/`, `.venv/`. Also excluded from this comparison: `.git/`, `.DS_Store`.

---

## 1. Summary

| Aspect | himax_fork | himax_test (Seeed_Grove_Vision_AI_Module_V2) |
|--------|-------------|----------------------------------------------|
| Build target | `APP_TYPE = allon_sensor_tflm` | `APP_TYPE = tflm_yolo26_od` |
| YOLO scenario | tflm_yolo11_od only | tflm_yolo11_od + **tflm_yolo26_od** (new) |
| cvapp_yolo11n_ob.cpp | YOLO11-only, `#if YOLO11_NO_POST_SEPARATE_OUTPUT` | Unified YOLO11 + YOLO26, single binary (3-out + 1-out), class names for vespa |
| main.c | No TFLM_YOLO26_OD | Adds `#ifdef TFLM_YOLO26_OD` branch |
| .gitignore | Includes `.venv/` | No `.venv/` entry |
| xmodem_send.py | Handles “end file transmission and reboot?” prompt | No prompt handling (removed block) |
| CMSIS-CV | Submodule (reference only in fork) | Full tree present under library/cmsis_cv/CMSIS-CV |
| Docs / artifacts | — | YOLO11_TO_WE2_REPRODUCTION.md, extra .tflite in model_zoo |

---

## 2. File-by-file changes

### 2.1 `.gitignore`

- **himax_fork:** Contains a “Local venv” section with `.venv/`.
- **himax_test:** Same file but **without** the `.venv/` entry (and trailing newline).

**Why it matters:** Fork keeps the project venv out of version control; test either relies on a parent .gitignore or does not ignore `.venv/` at this level.

---

### 2.2 `EPII_CM55M_APP_S/app/main.c`

- **himax_test adds** (after the `TFLM_YOLO11_OD` block, before `TFLM_YOLOV8_POSE`):

```c
#ifdef TFLM_YOLO26_OD
#include "tflm_yolo26_od.h"
/** main entry */
int main(void)
{
	board_init();
	tflm_yolo11_od_app();
	return 0;
}
#endif
```

**Why it works:** When the build defines `TFLM_YOLO26_OD` (via makefile `APP_TYPE = tflm_yolo26_od`), this `main()` is compiled. It still calls `tflm_yolo11_od_app()`, so the YOLO26 scenario reuses the same app entry point as YOLO11; the actual model and post-processing are selected at runtime in `cvapp_yolo11n_ob.cpp` (see below).

**USER:** I think we should not include this in himax_fork. We first focus on yolo11. No priority: yolo26, we will do that later. 

**TODO:** a lot of forks added the yolo11_od no_post. Compare what they did and why

---

### 2.3 `EPII_CM55M_APP_S/makefile`

- **himax_fork:** `APP_TYPE = allon_sensor_tflm`
- **himax_test:** Comment line `# tflm_yolo26_od` added in the scenario list; `APP_TYPE = tflm_yolo26_od`

**Why it works:** `APP_TYPE` drives which scenario is built and which `main()` is used. `tflm_yolo26_od` selects the YOLO26 scenario (and the `TFLM_YOLO26_OD` branch in `main.c`), so the firmware runs the shared app that supports both YOLO11 and YOLO26 via runtime detection in post-processing.

**USER:** makefile: change `APP_TYPE = tflm_yolo11_od`. Later we will add `APP_TYPE = tflm_yolo26_od`

---

### 2.4 `EPII_CM55M_APP_S/app/scenario_app/tflm_yolo11_od/cvapp_yolo11n_ob.cpp`

This file has the largest set of changes.

#### 2.4.1 Tensor arena and build variant

- **himax_fork:** Uses `#if YOLO11_NO_POST_SEPARATE_OUTPUT` to choose either 442K (3-output) or 1061K (single-output) tensor arena and different globals (`yolo11n_ob_output` vs `yolo11n_ob_output[6]`).
- **himax_test:** Single configuration: `tensor_arena_size = 1061*1024` and unconditional `yolo11n_ob_output[i]` for up to 6 outputs. Comment states: “Max of 3-output (442K) and single-output (1061K) so one binary supports all model types.”

**Why it works:** One binary can run both 3-output (YOLO11/YOLO26 no-post) and single-output (YOLO11/YOLO26 with post) models by always reserving the larger arena. No compile-time switch is needed per model type.

#### 2.4.2 Class names (COCO → vespa)

- **himax_fork:** `coco_classes[]` starts with COCO classes (e.g. `"person","bicycle","car",...`).
- **himax_test:** First four entries replaced with vespa-specific labels: `"amel","vcra","vespsp","vvel"`; rest unchanged.

**Why it works:** Detection results use `class_idx` into this array. For a 4-class vespa model, only indices 0–3 are used; the new names match the project’s class set (e.g. Asian hornet, Vespula crabro, Vespa species, Vespula velutina or similar).

**USER:** Check if this change is needed for himax ai webtoolkit or that a change is needed in the webtoolkit

#### 2.4.3 Init: stride/anchor allocation

- **himax_fork:** Stride/anchor allocation and `anchor_stride_matrix_construct()` are inside `#if YOLO11_NO_POST_SEPARATE_OUTPUT`.
- **himax_test:** Unconditional at the start of `cv_yolo11n_ob_init`: set `dim_total_size = 0`, loop over strides 8/16/32, compute `dim_total_size`, allocate `stride_756_1` and `anchor_756_2`, then call `anchor_stride_matrix_construct()`.

**Why it works:** Both YOLO11 and YOLO26 3-output paths need the same grid (28²+14²+7²) and stride/anchor data. Doing it unconditionally ensures one binary works for both.

**USER:** Check netron outputs

#### 2.4.4 Output tensor order (3-output)

- **himax_fork:** Fixed mapping: `output[0]=interpreter->output(0)`, `output[1]=interpreter->output(2)`, `output[2]=interpreter->output(1)` (assumes a fixed Vela/export order).
- **himax_test:** Order is determined by spatial size: interpreter outputs are inspected (e.g. `dims->data[1]` for rows); assigned so that `output[0]` = 28×28, `output[1]` = 14×14, `output[2]` = 7×7 (stride 8, 16, 32).

**Why it works:** Vela/export can emit the three tensors in any order. Mapping by shape makes the same binary correct regardless of output order from the runtime.

#### 2.4.5 Post-processing dispatch (YOLO11 vs YOLO26)

- **himax_fork:** Single `yolo11_ob_post_processing`; 3-output path uses the fixed output order and YOLO11-style decoding.
- **himax_test:**  
  - Forward declarations for: `yolo11_nopost_three_output_processing`, `yolo11_single_output_processing`, `yolo26_nopost_three_output_processing`, `yolo26_single_output_processing`.  
  - `yolo11_ob_post_processing` dispatches at runtime:  
    - If 3 outputs: check channel count (e.g. 68/144 → YOLO11 3-out, 8 → YOLO26 3-out) and call the matching nopost function.  
    - If 1 output: check dimensions (e.g. 8×1029 → YOLO26 single-out) and call the matching single-output function.  
  - New implementations: `yolo11_nopost_three_output_processing`, `yolo11_single_output_processing`, `yolo26_nopost_three_output_processing`, `yolo26_single_output_processing` (YOLO26 uses 4 classes and dist2bbox-style decoding).

**Why it works:** One app binary supports YOLO11 (3-out and 1-out) and YOLO26 (3-out and 1-out) by detecting output shape and channel count and calling the correct decoder, so no separate firmware is needed per model variant.

#### 2.4.6 Output binding (interpreter → globals)

- **himax_fork:** Under `#if YOLO11_NO_POST_SEPARATE_OUTPUT`, loops over `numOutputs` to fill `yolo11n_ob_output[i]`; under `#else`, single `yolo11n_ob_output = ... output(0)`.
- **himax_test:** Single loop: `for(int i = 0; i < numOutputs && i < 6; i++)` assigning `yolo11n_ob_output[i] = ... output(i)`.

**Why it works:** Matches the unified globals and supports both 3-output and single-output models with one code path.

---

### 2.5 `xmodem/xmodem_send.py`

- **himax_fork:** After `xmodem_send_bin()`, a loop reads serial lines; when the line equals the prompt `"Do you want to end file transmission and reboot system? (y)"`, it sends `'y'` and breaks.
- **himax_test:** That prompt-handling block is **removed** (no automatic reply to the reboot prompt).

**Why it works (fork):** Automates the post-flash reboot so the script can finish without user input.  
**Why it works (test):** Without the block, the script does not send `'y'`; the user may answer the prompt manually or another process may handle it. So test keeps a simpler, non-automated behaviour.

---

### 2.6 New in himax_test only

#### 2.6.1 Scenario `tflm_yolo26_od`

Directory **`EPII_CM55M_APP_S/app/scenario_app/tflm_yolo26_od/`** exists only in himax_test. It contains the YOLO26 app scenario (e.g. `tflm_yolo26_od.c`, `tflm_yolo26_od.h`, `tflm_yolo26_od.mk`, `cvapp_yolo11n_ob.cpp`, `yolo_postprocessing.cc`, linker script, CIS config, etc.). This scenario is what the makefile builds when `APP_TYPE = tflm_yolo26_od`; it reuses the same shared post-processing logic as in `tflm_yolo11_od` (via the unified `cvapp_yolo11n_ob.cpp`).

#### 2.6.2 `YOLO11_TO_WE2_REPRODUCTION.md`

Root-level doc in himax_test that describes the full YOLO11-on-WE2 (and YOLO26) workflow: shared post-processing edits, tensor arena, stride/anchor init, output order, adding the YOLO26 scenario, and reproduction steps. It matches the changes observed in `cvapp_yolo11n_ob.cpp`, `main.c`, and makefile.

#### 2.6.3 CMSIS-CV under `library/cmsis_cv/CMSIS-CV`

himax_fork has this as a submodule (or reference); himax_test has the full CMSIS-CV tree checked out (Include, Source, Examples, Documentation, etc.). Functionally the build may use the same headers/libs; the difference is only in how the repo stores the dependency (submodule vs in-tree copy).

#### 2.6.4 `model_zoo/tflm_yolo11_od/` (extra files in test)

Only in himax_test: `_temp_model_0_preamble_data.bin`, `yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite`, `yolo11n_vespa_2026-02v1_allpx__full_integer_quant_vela_tflite_imgsz224.tflite`, `yolo11n_vespa_2026-02v1_allpx_full_integer_quant_vela_nopost.tflite`, `yolo26n_vespa_2026-02v1_allpx_imgsz224_full_integer_quant_vela.tflite`. These are built/quantized models and temp data for the vespa pipeline; they are not in the fork (or are stored elsewhere).

---

### 2.7 Prebuilt libraries (`EPII_CM55M_APP_S/prebuilt_libs/gnu/*.a`)

The following archives **differ** between fork and test (binary):  
`lib_cmsis_nn_7_0_0.a`, `libcommon.a`, `libtflmtag2209_u55tag2205_cmsisnn_gnu.a`, `libtflmtag2412_u55tag2411_cmsisnn_gnu.a`, `libtrustzone_cfg.a`.  

They are not listed in `himax_fork/.gitignore` (only `*.lib`, `*.la`, `*.lai` are). The difference is likely due to different build dates or toolchain/config (e.g. for YOLO26/TFLM or CMSIS-NN version). No source-level comparison was done; treat as build artifacts.

---

### 2.8 Secureboot / image-gen artifacts (differ)

These paths **differ** between the two trees (and are not excluded by `himax_fork/.gitignore`):

- `we2_image_gen_local/secureboot_tool/cert/ICVSBContent.crt`
- `we2_image_gen_local/secureboot_tool/cert/ICVSBContent_Cert.txt`
- `we2_image_gen_local/secureboot_tool/sb_content_cert.log`

`we2_image_gen_local/Images*.txt` is ignored by .gitignore; other cert/log files are generated by the secure boot or image-gen process and will differ per build/signing environment. No functional comparison was performed; they are listed only for completeness.

---

## 3. Rationale overview

- **Single binary for YOLO11 and YOLO26:** One tensor arena size, one set of globals, and runtime dispatch by output shape/channels avoid multiple firmware images and simplify deployment.
- **Vespa-specific classes:** The 4-class array matches the project’s model and reporting (Asian hornet, etc.).
- **Output-order agnostic:** Mapping 3-output tensors by spatial size (28², 14², 7²) keeps the same binary correct across different TFLite/Vela export orders.
- **YOLO26 scenario:** The new `tflm_yolo26_od` scenario and `TFLM_YOLO26_OD` in `main.c` allow building a firmware target that uses the shared app and post-processing for YOLO26 models.

---

## 4. Reference

- **Comparison scope:** `himax_fork` vs `himax_test/Seeed_Grove_Vision_AI_Module_V2`.
- **Ignore rules:** As in `himax_fork/.gitignore`; `.git` and `.DS_Store` excluded from this note.
- **Date:** 2025-03-05.
