**One-line purpose:** see if all quantified and conversion to vela have the same tensor
**Short summary:** 
**Agent:** 
**Index:** [[himax from pt to flash]][[_model]]

---
yolo11n_full_integer_quant_vela_imgz_224_kris_nopost_241230.tflite --> model works on GV2
![[yolo11n_full_integer_quant_vela_imgz_224_kris_nopost_241230.tflite netron.png]]


yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite --> model works on gv2
![[yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite netron.png]]

quantized and converted to vela in 2026 (runtimme 2025.07)
# YOLO11-on-WE2 workflow – reproduction guide

  

This document lists **every change** to the Seeed/Himax YOLO11-on-WE2 (Grove Vision AI V2) firmware and tooling so you can fork the repo and reproduce the same behaviour. Do the steps in this order.

  

**Base:** Fork of [HimaxWiseEyePlus/YOLO11_on_WE2](https://github.com/HimaxWiseEyePlus/YOLO11_on_WE2) or the Seeed Grove Vision AI Module V2 SDK that contains `EPII_CM55M_APP_S` with `tflm_yolo11_od`.

  

**Paths:** All paths below are relative to the repo root (e.g. `Seeed_Grove_Vision_AI_Module_V2/` or `YOLO11_on_WE2/`). `EPII_CM55M_APP_S` is the main app build directory.

  

---

  

## Phase 1: Shared post-processing (YOLO11 + YOLO26)

  

All edits in this phase are in **one file** used by the YOLO11 scenario. Later, when you add the YOLO26 scenario, you will **copy** this scenario (including this file), so the same logic is used for both.

  

**File:** `EPII_CM55M_APP_S/app/scenario_app/tflm_yolo11_od/cvapp_yolo11n_ob.cpp`

  

### 1.1 Tensor arena size

  

Support both 3-output (smaller) and single-output (larger) models with one binary.

  

**Find (around line 76):**

```cpp

constexpr int tensor_arena_size = 442*1024; // or similar

```

  

**Replace with:**

```cpp

/* Max of 3-output (442K) and single-output (1061K) so one binary supports all model types */

constexpr int tensor_arena_size = 1061*1024;

```

  

---

  

### 1.2 Globals for stride/anchor (unconditional)

  

Ensure `dim_total_size`, `stride_756_1`, and `anchor_756_2` are always declared and used for 3-output post-processing.

  

**Find** the block that declares these (e.g. inside `#if YOLO11_NO_POST_SEPARATE_OUTPUT` or similar):

```cpp

int dim_total_size = 0;

static float* stride_756_1;

static float** anchor_756_2;

```

  

**Ensure** they are **unconditional** (no `#if` around them). If they are inside a preprocessor block, move them out so they are always declared at file scope.

  

---

  

### 1.3 Init: reset `dim_total_size` and allocate stride/anchor for 3-output

  

In `cv_yolo11n_ob_init`, stride and anchor must be allocated for the 3-level grid (28² + 14² + 7²) every time, so both YOLO11 and YOLO26 3-output paths work.

  

**Find** the start of `cv_yolo11n_ob_init` (around line 439). Ensure the following is at the **very beginning** of the function (before any other logic):

  

```cpp

int cv_yolo11n_ob_init(bool security_enable, bool privilege_enable, uint32_t model_addr) {

/* Allocate stride/anchor for 3-output paths (YOLO11 and YOLO26 no_post=True) */

dim_total_size = 0;

int dim_stride = 8;

for(int i = 0; i < 3;i++)

{

if(i==0) dim_stride = 8;

else if(i==1) dim_stride = 16;

else dim_stride = 32;

dim_total_size += pow((YOLO11_OB_INPUT_TENSOR_WIDTH/dim_stride),2);

}

stride_756_1 = (float*)calloc(dim_total_size, sizeof(float));

anchor_756_2 = (float**)calloc(dim_total_size, sizeof(float *));

for(int i=0;i<dim_total_size;i++)

anchor_756_2[i] = (float*)calloc(2, sizeof(float));

anchor_stride_matrix_construct();

// ... rest of init (tensor_arena, NPU, model load, etc.)

```

  

Remove or replace any **conditional** allocation that only ran for one model type; allocation must be unconditional so both YOLO11 and YOLO26 3-output use it.

  

---

  

### 1.4 Deinit: free stride and anchor unconditionally

  

In `cv_yolo11n_ob_deinit`, always free the stride and anchor arrays.

  

**Find** `cv_yolo11n_ob_deinit` and set its body to:

  

```cpp

int cv_yolo11n_ob_deinit()

{

free(stride_756_1);

for(int i = 0; i < dim_total_size; i++)

free(anchor_756_2[i]);

free(anchor_756_2);

return 0;

}

```

  

Ensure there is no `#if` that skips this when building for single-output only.

  

---

  

### 1.5 Dispatcher and YOLO26 stubs (forward declarations)

  

Add forward declarations for the four processing functions so the dispatcher can call them.

  

**Find** the line where `yolo11_ob_post_processing` is **defined** (the function that does the post-processing switch). **Immediately before** it, add:

  

```cpp

static void yolo11_nopost_three_output_processing(tflite::MicroInterpreter* static_interpreter, float modelScoreThreshold, float modelNMSThreshold, struct_yolov8_ob_algoResult *alg, std::forward_list<el_box_t> &el_algo);

static void yolo11_single_output_processing(tflite::MicroInterpreter* static_interpreter, float modelScoreThreshold, float modelNMSThreshold, struct_yolov8_ob_algoResult *alg, std::forward_list<el_box_t> &el_algo);

static void yolo26_nopost_three_output_processing(tflite::MicroInterpreter* static_interpreter, float modelScoreThreshold, float modelNMSThreshold, struct_yolov8_ob_algoResult *alg, std::forward_list<el_box_t> &el_algo);

static void yolo26_single_output_processing(tflite::MicroInterpreter* static_interpreter, float modelScoreThreshold, float modelNMSThreshold, struct_yolov8_ob_algoResult *alg, std::forward_list<el_box_t> &el_algo);

```

  

---

  

### 1.6 Replace single `yolo11_ob_post_processing` with dispatcher

  

Replace the **existing** `yolo11_ob_post_processing` implementation with a dispatcher that chooses by output count and tensor shape.

  

**Remove** the old body of `yolo11_ob_post_processing` and use **exactly**:

  

```cpp

static void yolo11_ob_post_processing(tflite::MicroInterpreter* static_interpreter, float modelScoreThreshold, float modelNMSThreshold, struct_yolov8_ob_algoResult *alg, std::forward_list<el_box_t> &el_algo)

{

int numOutputs = static_interpreter->outputs_size();

if (numOutputs == 3) {

int channels = static_interpreter->output(0)->dims->data[3];

if (channels == 68 || channels == 144)

yolo11_nopost_three_output_processing(static_interpreter, modelScoreThreshold, modelNMSThreshold, alg, el_algo);

else if (channels == 8)

yolo26_nopost_three_output_processing(static_interpreter, modelScoreThreshold, modelNMSThreshold, alg, el_algo);

else

yolo11_nopost_three_output_processing(static_interpreter, modelScoreThreshold, modelNMSThreshold, alg, el_algo);

} else if (numOutputs == 1) {

TfLiteTensor* out0 = static_interpreter->output(0);

int d1 = out0->dims->data[1], d2 = out0->dims->data[2];

if (d1 == 8 && d2 == 1029)

yolo26_single_output_processing(static_interpreter, modelScoreThreshold, modelNMSThreshold, alg, el_algo);

else

yolo11_single_output_processing(static_interpreter, modelScoreThreshold, modelNMSThreshold, alg, el_algo);

}

}

```

  

- **3 outputs:** channels 68 or 144 → YOLO11; channels 8 → YOLO26; else YOLO11.

- **1 output:** shape `[1,8,1029]` → YOLO26; else YOLO11.

  

---

  

### 1.7 YOLO11 three-output: dynamic output order (28→14→7)

  

Vela/TFLite can emit the three detection tensors in any order. Map them by spatial size so `output[0]` = 28×28, `output[1]` = 14×14, `output[2]` = 7×7.

  

**Find** in `yolo11_nopost_three_output_processing` the place where the three interpreter outputs are assigned (e.g. `output[0] = static_interpreter->output(0);` etc. or a fixed order).

  

**Replace** that block with:

  

```cpp

TfLiteTensor* output[numOutputs];

/***

* Map interpreter outputs to fixed order: output[0]=28x28, output[1]=14x14, output[2]=7x7 (stride 8,16,32).

* Vela/export can emit the three tensors in any order; assign by spatial size so all orderings work.

***/

{

TfLiteTensor* out0 = static_interpreter->output(0);

TfLiteTensor* out1 = static_interpreter->output(1);

TfLiteTensor* out2 = static_interpreter->output(2);

int r0 = out0->dims->data[1];

int r1 = out1->dims->data[1];

int r2 = out2->dims->data[1];

if (r0 == 28) { output[0] = out0; output[1] = (r1 == 14) ? out1 : out2; output[2] = (r1 == 14) ? out2 : out1; }

else if (r1 == 28) { output[0] = out1; output[1] = (r0 == 14) ? out0 : out2; output[2] = (r0 == 14) ? out2 : out0; }

else { output[0] = out2; output[1] = (r0 == 14) ? out0 : out1; output[2] = (r0 == 14) ? out1 : out0; }

}

```

  

Keep the rest of `yolo11_nopost_three_output_processing` unchanged (DFL decode, NMS, scaling).

  

---

  

### 1.8 Add YOLO26 three-output processing (no_post, ltrb decode)

  

Add a **new** function `yolo26_nopost_three_output_processing` **after** `yolo11_nopost_three_output_processing` (and before `yolo11_single_output_processing`). It should:

  

1. Map the three outputs by spatial size (same 28→14→7 logic as in 1.7).

2. Build `out_dim_total` and `out_dim_size[]` from the three tensors.

3. Use `stride_756_1` and the same per-cell index math as YOLO11 to get `(dims_cnt_1, dims_cnt_2, output_data_idx)` for each linear index `j`.

4. For each cell: read 8 channels (4 bbox + 4 class) via `yolo11_nopost_dequant_value`, get `stride_cur = stride_756_1[j]`.

5. Decode bbox with **Ultralytics ltrb** (dist2bbox): anchor = (grid + 0.5), 4 channels = (left, top, right, bottom) in grid units:

- `anchor_x = dims_cnt_2 + 0.5f`, `anchor_y = dims_cnt_1 + 0.5f`

- `left = v[0], top = v[1], right = v[2], bottom = v[3]`

- `cx = (anchor_x + (right - left) * 0.5f) * stride_cur`

- `cy = (anchor_y + (bottom - top) * 0.5f) * stride_cur`

- `w = (left + right) * stride_cur`, `h = (top + bottom) * stride_cur`

- If `w <= 0` or `h <= 0`, skip the cell.

6. Class scores: channels 4..7, sigmoid, max score and argmax; threshold by `modelScoreThreshold`.

7. Push box (xy top-left and wh), class index, confidence; then call `yolo11_NMSBoxes`; then scale to image size and fill `alg->obr` and `el_algo`.

  

**Reference implementation** (paste and adjust to your naming/style):

  

```cpp

static void yolo26_nopost_three_output_processing(tflite::MicroInterpreter* static_interpreter, float modelScoreThreshold, float modelNMSThreshold, struct_yolov8_ob_algoResult *alg, std::forward_list<el_box_t> &el_algo)

{

uint32_t img_w = app_get_raw_width();

uint32_t img_h = app_get_raw_height();

int numOutputs = static_interpreter->outputs_size();

TfLiteTensor* output[3];

TfLiteTensor* out0 = static_interpreter->output(0);

TfLiteTensor* out1 = static_interpreter->output(1);

TfLiteTensor* out2 = static_interpreter->output(2);

int r0 = out0->dims->data[1], r1 = out1->dims->data[1], r2 = out2->dims->data[1];

if (r0 == 28) { output[0] = out0; output[1] = (r1 == 14) ? out1 : out2; output[2] = (r1 == 14) ? out2 : out1; }

else if (r1 == 28) { output[0] = out1; output[1] = (r0 == 14) ? out0 : out2; output[2] = (r0 == 14) ? out2 : out0; }

else { output[0] = out2; output[1] = (r0 == 14) ? out0 : out1; output[2] = (r0 == 14) ? out1 : out0; }

int out_dim_total = 0;

int out_dim_size[3];

for (int out_num = 0; out_num < numOutputs; out_num++) {

out_dim_total += (output[out_num]->dims->data[1] * output[out_num]->dims->data[2]);

out_dim_size[out_num] = out_dim_total;

}

std::vector<uint16_t> class_idxs;

std::vector<float> confidences;

std::vector<box> boxes;

const int num_classes = 4;

for (int j = 0; j < out_dim_total; j++) {

int output_data_idx;

int dims_cnt_1, dims_cnt_2, idx;

if (j < out_dim_size[0]) {

output_data_idx = 0;

dims_cnt_1 = j / output[0]->dims->data[1];

dims_cnt_2 = j % output[0]->dims->data[2];

} else if (j < out_dim_size[1]) {

output_data_idx = 1;

idx = j - out_dim_size[0];

dims_cnt_1 = idx / output[1]->dims->data[1];

dims_cnt_2 = idx % output[1]->dims->data[2];

} else {

output_data_idx = 2;

idx = j - out_dim_size[1];

dims_cnt_1 = idx / output[2]->dims->data[1];

dims_cnt_2 = idx % output[2]->dims->data[2];

}

TfLiteTensor* out = output[output_data_idx];

float v[8];

for (int c = 0; c < 8; c++)

v[c] = yolo11_nopost_dequant_value(dims_cnt_1, dims_cnt_2, c, out);

float stride_cur = stride_756_1[j];

/* Ultralytics dist2bbox (tal.py): 4 channels = (left, top, right, bottom) in grid units; anchor = (grid + 0.5). */

const float anchor_x = (float)dims_cnt_2 + 0.5f;

const float anchor_y = (float)dims_cnt_1 + 0.5f;

float left = v[0], top = v[1], right = v[2], bottom = v[3];

/* If export uses exp(ltrb) for positivity, use: left=expf(v[0]); top=expf(v[1]); right=expf(v[2]); bottom=expf(v[3]); */

float cx = (anchor_x + (right - left) * 0.5f) * stride_cur;

float cy = (anchor_y + (bottom - top) * 0.5f) * stride_cur;

float w = (left + right) * stride_cur;

float h = (top + bottom) * stride_cur;

if (w <= 0.f || h <= 0.f) continue;

float maxScore = 0;

uint16_t maxClassIndex = 0;

for (int c = 0; c < num_classes; c++) {

float s = sigmoid(v[4 + c]);

if (s > maxScore) { maxScore = s; maxClassIndex = (uint16_t)c; }

}

if (maxScore >= modelScoreThreshold) {

box bbox;

bbox.x = cx - 0.5f * w;

bbox.y = cy - 0.5f * h;

bbox.w = w;

bbox.h = h;

boxes.push_back(bbox);

class_idxs.push_back(maxClassIndex);

confidences.push_back(maxScore);

}

}

std::vector<int> nms_result;

yolo11_NMSBoxes(boxes, confidences, modelScoreThreshold, modelNMSThreshold, nms_result);

for (size_t i = 0; i < nms_result.size(); i++) {

if (!(MAX_TRACKED_YOLOV8_ALGO_RES - (int)i)) break;

int idx = nms_result[i];

float scale_factor_w = (float)img_w / (float)YOLO11_OB_INPUT_TENSOR_WIDTH;

float scale_factor_h = (float)img_h / (float)YOLO11_OB_INPUT_TENSOR_HEIGHT;

alg->obr[i].confidence = confidences[idx];

alg->obr[i].bbox.x = (uint32_t)(boxes[idx].x * scale_factor_w);

alg->obr[i].bbox.y = (uint32_t)(boxes[idx].y * scale_factor_h);

alg->obr[i].bbox.width = (uint32_t)(boxes[idx].w * scale_factor_w);

alg->obr[i].bbox.height = (uint32_t)(boxes[idx].h * scale_factor_h);

alg->obr[i].class_idx = class_idxs[idx];

el_box_t temp_el_box;

temp_el_box.score = confidences[idx] * 100;

temp_el_box.target = class_idxs[idx];

temp_el_box.x = (uint32_t)(boxes[idx].x * scale_factor_w);

temp_el_box.y = (uint32_t)(boxes[idx].y * scale_factor_h);

temp_el_box.w = (uint32_t)(boxes[idx].w * scale_factor_w);

temp_el_box.h = (uint32_t)(boxes[idx].h * scale_factor_h);

el_algo.emplace_front(temp_el_box);

}

}

```

  

If your model has a different `num_classes`, change the constant and the loop over `v[4 + c]` accordingly.

  

---

  

### 1.9 Add YOLO26 single-output processing stub

  

Add a function `yolo26_single_output_processing` that handles one output of shape `[1, 8, 1029]` (decoded/no_post=False style). You can implement it by parsing the 8 rows (4 bbox + 4 class) and 1029 columns, then running NMS and filling `alg` and `el_algo`. If you only use 3-output no_post models, a stub that does nothing (or calls a minimal path) is enough so the linker is satisfied.

  

**Minimal stub:**

  

```cpp

static void yolo26_single_output_processing(tflite::MicroInterpreter* static_interpreter, float modelScoreThreshold, float modelNMSThreshold, struct_yolov8_ob_algoResult *alg, std::forward_list<el_box_t> &el_algo)

{

(void)static_interpreter;

(void)modelScoreThreshold;

(void)modelNMSThreshold;

(void)alg;

(void)el_algo;

/* TODO: decode [1,8,1029] format if needed */

}

```

  

Replace with full decode/NMS/scaling if you use single-output YOLO26.

  

---

  

## Phase 2: Main entry for YOLO26 scenario

  

So that building with `APP_TYPE=tflm_yolo26_od` has a valid `main()`.

  

**File:** `EPII_CM55M_APP_S/app/main.c`

  

**Find** the block:

  

```c

#ifdef TFLM_YOLO11_OD

#include "tflm_yolo11_od.h"

/** main entry */

int main(void)

{

board_init();

tflm_yolo11_od_app();

return 0;

}

#endif

```

  

**Immediately after** that `#endif`, add:

  

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

  

Note: the function name stays `tflm_yolo11_od_app()`; the YOLO26 scenario implements it in its own `tflm_yolo26_od.c`.

  

---

  

## Phase 3: YOLO26 scenario (copy and adapt)

  

Create a second scenario so you can build a firmware image that loads a YOLO26 model from a dedicated flash address, without changing the YOLO11 flow.

  

### 3.1 Copy scenario directory

  

From `EPII_CM55M_APP_S/app/scenario_app/`:

  

```bash

cp -R tflm_yolo11_od tflm_yolo26_od

```

  

All Phase 1 changes are now in `tflm_yolo26_od/cvapp_yolo11n_ob.cpp` as well.

  

### 3.2 Rename scenario files (in `tflm_yolo26_od/`)

  

- `tflm_yolo11_od.c` → `tflm_yolo26_od.c`

- `tflm_yolo11_od.h` → `tflm_yolo26_od.h`

- `tflm_yolo11_od.mk` → `tflm_yolo26_od.mk`

- `TFLM_yolo11_od_S_only.ld` → `TFLM_yolo26_od_S_only.ld`

- `TFLM_yolo11_od_S_only.sct` → `TFLM_yolo26_od_S_only.sct`

  

### 3.3 `tflm_yolo26_od.mk`

  

- Set `APPL_DEFINES` for this scenario: replace `-DTFLM_YOLO11_OD` with `-DTFLM_YOLO26_OD`.

- Set linker script to the new names:

- `LINKER_SCRIPT_FILE := .../TFLM_yolo26_od_S_only.sct` (arm)

- `LINKER_SCRIPT_FILE := .../TFLM_yolo26_od_S_only.ld` (gnu)

  

Example:

  

```makefile

APPL_DEFINES += -DTFLM_YOLO26_OD

# ... rest same as yolo11 ...

ifeq ($(strip $(TOOLCHAIN)), arm)

override LINKER_SCRIPT_FILE := $(SCENARIO_APP_ROOT)/$(APP_TYPE)/TFLM_yolo26_od_S_only.sct

else

override LINKER_SCRIPT_FILE := $(SCENARIO_APP_ROOT)/$(APP_TYPE)/TFLM_yolo26_od_S_only.ld

endif

```

  

### 3.4 `common_config.h` (in `tflm_yolo26_od/`)

  

- Change include guard to something like `SCENARIO_TFLM_YOLO26_OD_COMMON_CONFIG_H_`.

- Replace YOLO11 model address with YOLO26 (same slot, different define name):

  

```c

#define YOLO26_OBJECT_DETECTION_FLASH_ADDR 0x3AB7B000

```

  

Remove or keep `YOLO11_OBJECT_DETECTION_FLASH_ADDR` depending on whether you use it elsewhere in this scenario.

  

### 3.5 `tflm_yolo26_od.c`

  

- Include `"tflm_yolo26_od.h"` instead of `"tflm_yolo11_od.h"`.

- In the branch that runs object detection (e.g. `g_use_case == 0`):

- Print something like `"YOLO26 object detection\n"`.

- Call `cv_yolo11n_ob_init(true, true, YOLO26_OBJECT_DETECTION_FLASH_ADDR);`

- Keep calling `app_start_state(APP_STATE_ALLON_YOLO11N_OB);` so the same event/datapath logic runs.

  

### 3.6 `tflm_yolo26_od.h`

  

- Use a unique include guard, e.g. `SCENARIO_TFLM_YOLO26_OD_PL_`.

- Keep the same `APP_STATE_E` and `APP_STATE_ALLON_YOLO11N_OB` so the rest of the app still compiles.

- Declare `int tflm_yolo11_od_app(void);` (the YOLO26 scenario implements this symbol).

  

### 3.7 `send_result.cpp` (in `tflm_yolo26_od/`)

  

- Change `#include "tflm_yolo11_od.h"` to `#include "tflm_yolo26_od.h"`.

  

### 3.8 Linker scripts `TFLM_yolo26_od_S_only.ld` and `.sct`

  

- Inside the files, replace any reference to `TFLM_yolo11_od` or yolo11-specific section names with `TFLM_yolo26_od` (or the same names as in the YOLO11 linker scripts if layout is identical). This is so the build uses the correct script for the YOLO26 scenario.

  

### 3.9 Makefile comment (root `EPII_CM55M_APP_S/makefile`)

  

- Where `APP_TYPE` is listed (e.g. commented options), add a line for the new scenario:

  

```makefile

# tflm_yolo11_od

# tflm_yolo26_od (YOLO26 model flashing; same flash slot 0xB7B000)

```

  

Do **not** change the default `APP_TYPE` in the doc; the user sets it to `tflm_yolo11_od` or `tflm_yolo26_od` when building.

  

### 3.10 Optional: `README_YOLO26.md` in `tflm_yolo26_od/`

  

Add a short README describing:

  

- Set `APP_TYPE = tflm_yolo26_od`, build, copy ELF to `we2_image_gen` input, run image gen, flash `output.img`, and optionally send a YOLO26 model to `0xB7B000` (same slot as YOLO11).

- Model address: `YOLO26_OBJECT_DETECTION_FLASH_ADDR` = `0x3AB7B000`.

  

---

  

## Phase 4: Web toolkit class labels (Himax AI web toolkit)

  

So the flasher/UI shows your class names instead of the default COCO labels.

  

**File:** `Himax_AI_web_toolkit/assets/index-legacy.51f14f00.js` (or the main JS bundle that defines the class list for object detection).

  

- Search for the variable that holds class names (e.g. `h=` or an array of strings like `"person","car","bicycle","motorcycle"`).

- Ensure it is a **valid JavaScript array**, e.g.:

  

```js

h=["amel","vcra","vespsp","vvel"]

```

  

If it was broken to something like `h="amel","vcra",...` (no leading `[`), the page can go blank or throw a syntax error. Fix by making it an array literal as above.

- Replace the strings with your model’s class names in the same order as in training (index 0, 1, 2, 3, …).

  

---

  

## Summary checklist

  

| Phase | What |

|-------|------|

| 1.1 | `cvapp_yolo11n_ob.cpp`: tensor_arena_size = 1061*1024 |

| 1.2 | Same file: stride/anchor globals unconditional |

| 1.3 | Same file: init allocates stride/anchor for 3 levels, dim_total_size reset |

| 1.4 | Same file: deinit frees stride/anchor |

| 1.5 | Same file: forward declarations for 4 processing functions |

| 1.6 | Same file: dispatcher `yolo11_ob_post_processing` by outputs and shape |

| 1.7 | Same file: YOLO11 three-output dynamic 28/14/7 mapping |

| 1.8 | Same file: add `yolo26_nopost_three_output_processing` (ltrb decode, NMS) |

| 1.9 | Same file: add `yolo26_single_output_processing` (stub or full) |

| 2 | `app/main.c`: add `#ifdef TFLM_YOLO26_OD` main block |

| 3.1 | Copy `tflm_yolo11_od` → `tflm_yolo26_od` |

| 3.2 | Rename .c, .h, .mk, .ld, .sct in `tflm_yolo26_od` |

| 3.3 | `tflm_yolo26_od.mk`: TFLM_YOLO26_OD, linker scripts |

| 3.4 | `tflm_yolo26_od/common_config.h`: YOLO26_OBJECT_DETECTION_FLASH_ADDR |

| 3.5 | `tflm_yolo26_od.c`: include yolo26 header, init with YOLO26 addr, message |

| 3.6 | `tflm_yolo26_od.h`: guard, declare tflm_yolo11_od_app |

| 3.7 | `tflm_yolo26_od/send_result.cpp`: include tflm_yolo26_od.h |

| 3.8 | Linker scripts: rename references to yolo26 |

| 3.9 | Root makefile: comment tflm_yolo26_od |

| 3.10 | Optional README_YOLO26.md |

| 4 | Web toolkit JS: class list array syntax and names |

  

After this, building with `APP_TYPE = tflm_yolo11_od` gives the YOLO11 workflow (with robust output order and shared arena); building with `APP_TYPE = tflm_yolo26_od` gives the YOLO26 workflow using the same post-processing code and ltrb decode.