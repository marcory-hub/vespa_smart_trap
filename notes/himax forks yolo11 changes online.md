**One-line purpose:** what other forks changes with respect to yolo11 object detection and no_post 224 imgsz
**Short summary:** 
**Agent:** tasks are after Agent:
**Main Index:** [[_000]]

---
**Forks and commits reviewed**
- scotty9000 (kris-himax): commit `3c7cf77` “add yolo11n od no post-proccessing inference example”; commit `db2d508` “Update xmodem_send.py”.
- harry123180: commit `ea67f23` “Update CLAUDE.md”.
- wildlifeai: main branch commits (list from GitHub).
- vienkmt, Seeed-Studio/sscma-example-we2: quick install readme; sscma image only.

##  Himax upstream commits in the context of YOLO11 post / no_post and 224 vs 192

From the upstream commit list and the diffs fetched, this is what matters for YOLO11 OD and 192/224:

|Commit|Date|Relevance to YOLO11 post/no_post and 224 vs 192|
|---|---|---|
|e5d8008|2024-12-23|Initial tflm_yolo11_od. Post-only: single output, 192×192 input, 1061K arena. README and model: `yolo11n_full_integer_quant_192_241219_batch_matmul_vela.tflite`. No no_post path yet.|
|aa422ee|2024-12-24|tflm_yolo11_od fixes. (1) Fixes call `cv_yolo11_ob_run` → `cv_yolo11n_ob_run`. (2) Wraps all UART/JSON algo result sending in `#ifdef UART_SEND_ALOGO_RESEULT` in `send_result.cpp`/`send_result.h`. If that macro is not defined, the firmware does not send detection results over UART — terminal may show no inference output while Himax AI webtoolkit (if it uses another path) can still work. Very relevant to “inference not on terminal but works in webtoolkit.” Also removes unused TFLM hexdump/static_vector.|
|3c7cf77|2025-02-20|Adds no_post path. `YOLO11_NO_POST_SEPARATE_OUTPUT`: no_post = 224×224, 442K arena, 3 outputs, DFL+dist2bbox in C; post = 192×192, 1061K. Adds `yolo11n_full_integer_quant_vela_imgz_224_kris_nopost_241230.tflite`. So 224 is no_post, 192 is post in upstream.|
|dbef489|2025-11-13|xmodem_send.py: add “without wait press 'y'”. Adds the block that detects the “Do you want to end file transmission and reboot system? (y)” prompt and sends `'y'` and breaks. So the script no longer waits for the user to press ‘y’ manually.|
|db2d508|2025-11-13|xmodem_send.py: Indentation/formatting only; same logic as dbef489.|
|933810c|2025-12-24|“update image resize function”. Only `lib_img_proc.a` (prebuilt) changed; no source. Affects how camera frames are resized to model input (could matter for 192 vs 224 pipelines).|

Summary for 224 vs 192 and post vs no_post:

- Upstream started with post + 192 only (e5d8008).
- no_post + 224 was added in 3c7cf77; since then upstream has both: no_post ⇒ 224, post ⇒ 192.
- For “terminal vs webtoolkit” behaviour, aa422ee (`UART_SEND_ALOGO_RESEULT`) is the most relevant: if your build doesn’t define that macro, UART result sending is disabled and terminal won’t show inference even if webtoolkit does.

---
[scotty9000](https://github.com/scotty9000/Seeed_Grove_Vision_AI_Module_V2/commit/3c7cf771b84c83b34a21879abce06ef911cdc9ee) `3c7cf77` – what changed, why, what it does

- What: Adds YOLO11 no_post support behind `#define YOLO11_NO_POST_SEPARATE_OUTPUT 1`.
    - Input size: no_post → 224×224 (`YOLO11_OB_INPUT_TENSOR_WIDTH/HEIGHT`), post → 192×192.
    - Arena: no_post 442K, post 1061K; no_post uses `yolo11n_ob_output[6]`, post uses single `yolo11n_ob_output`.
    - Init: Stride/anchor and `anchor_stride_matrix_construct()` only when `YOLO11_NO_POST_SEPARATE_OUTPUT`; `dim_total_size` = 28²+14²+7² = 756 for 224.
    - 3-output order: Fixed mapping `output[0]=out(0)` (28×28), `output[1]=out(2)` (14×14), `output[2]=out(1)` (7×7).
    - Post: New path: dequant + DFL (16-bin softmax) + dist2bbox in C, then NMS; `print_model_info()` called at init.
    - Model: Adds `yolo11n_full_integer_quant_vela_imgz_224_kris_nopost_241230.tflite` to model_zoo; README documents no_post (224) vs post (192) and which .tflite to use.
- Why: Smaller tensor arena for 3-output no_post (442K vs 1061K) and support for 224×224 no_post models.
- 192 vs 224: In this fork, no_post = 224, post = 192 (explicit in the `#if YOLO11_NO_POST_SEPARATE_OUTPUT` defines). So “no_post_224” vs “post_192” is exactly how scotty9000 encodes it.
https://github.com/scotty9000/Seeed_Grove_Vision_AI_Module_V2/commit/3c7cf771b84c83b34a21879abce06ef911cdc9ee
“Can we run a post.tflite by changing `#define YOLO11_NO_POST_SEPARATE_OUTPUT` to 0?”
- Yes. scotty9000 README says: set the define to `0` in `cvapp_yolo11n_ob.cpp` (line 38) and flash the post model `yolo11n_full_integer_quant_192_241219_batch_matmul_vela.tflite`. Build and flash firmware with that define and model to run post (192) instead of no_post (224).

---

[https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/forks](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/forks?include=active&page=1&period=2y&sort_by=last_updated)
Forks sorted on recently updated
Agent: can you check for these links to see if any usefull commit with respect to yolo11 object detection post and no_post. If you find any add it to the information below. Also explain what is changes, why it is changed and what is does.

https://github.com/wildlifeai/Seeed_Grove_Vision_AI_Module_V2
updated 1 hr ago

add yolo11n od no post-proccessing inference example
https://github.com/scotty9000/Seeed_Grove_Vision_AI_Module_V2/commit/3c7cf771b84c83b34a21879abce06ef911cdc9ee
Agent: 
1. check if yolo11 no_post.tflite is not already in himax_fork. 
2. check if we can run a post.tflite by changing `#define YOLO11_NO_POST_SEPARATE_OUTPUT 1`
Update xmodem_send.py
https://github.com/scotty9000/Seeed_Grove_Vision_AI_Module_V2/commit/db2d50889baf047ae0dd781393d82fa3b146d4db
Agent: user tested it, behavior old version: after flashing the gv2 and pressing reset the inference starts on the terminal. Behavior new version: after flashing the gv2 the inference is not starting on the terminal, but inference is present when using himax ai webtoolkit. Explain to user what is changed in the code and how this changes the behavior of the gv2

https://github.com/harry123180/Seeed_Grove_Vision_AI_Module_V2/commit/ea67f23636f65dd86248e5cb52819cc336fcc1e7
Agent: this is a page written for an other agent (Claude). Can we use any of this?

https://github.com/vienkmt/Seeed_Grove_Vision_AI_Module_V2
Nice readme on quick install
Agent: seems nothing here for yolo11 object detection

https://github.com/Seeed-Studio/sscma-example-we2
only an image of the yolo11_od

