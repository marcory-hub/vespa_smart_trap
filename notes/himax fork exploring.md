**One-line purpose:** 
**Short summary:** 
**SoT:**
**Agent:** 
**Main Index:** [[_himax sdk]]

---

**Makefile**: what gets build
changed to tflm_yolo11_od
```
# PS: As follow are scenario_app app name should be the same as directory name
APP_TYPE = tflm_yolo11_od
```
(Agent: not needed for yolo11 project, but for yolo26 project: make new tflm_yolo26_od folder and change APP_TYPE yo APP_TYPE = tflm_yolo26_od)

**PII_CM55M_APP_S/app/main.c**: if APP_TYPE = tflm_yolo11_od 


**cvapp_yolo11n_ob.cpp**:
input size
```C#
#if YOLO11_NO_POST_SEPARATE_OUTPUT
#define YOLO11_OB_INPUT_TENSOR_WIDTH   224
#define YOLO11_OB_INPUT_TENSOR_HEIGHT  224
#else
#define YOLO11_OB_INPUT_TENSOR_WIDTH   192
#define YOLO11_OB_INPUT_TENSOR_HEIGHT  192
#endif
#define YOLO11_OB_INPUT_TENSOR_CHANNEL INPUT_IMAGE_CHANNELS

#define YOLO11N_OB_DBG_APP_LOG 0
```
class names
```C#
#if YOLO11N_OB_DBG_APP_LOG

std::string coco_classes[] = {"person","bicycle","car","motorcycle","airplane","bus","train","truck","boat","traffic light","fire hydrant","stop sign","parking meter","bench","bird","cat","dog","horse","sheep","cow","elephant","bear","zebra","giraffe","backpack","umbrella","handbag","tie","suitcase","frisbee","skis","snowboard","sports ball","kite","baseball bat","baseball glove","skateboard","surfboard","tennis racket","bottle","wine glass","cup","fork","knife","spoon","bowl","banana","apple","sandwich","orange","broccoli","carrot","hot dog","pizza","donut","cake","chair","couch","potted plant","bed","dining table","toilet","tv","laptop","mouse","remote","keyboard","cell phone","microwave","oven","toaster","sink","refrigerator","book","clock","vase","scissors","teddy bear","hair drier","toothbrush"};

int coco_ids[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 31,

32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,

57, 58, 59, 60, 61, 62, 63, 64, 65, 67, 70, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 84, 85,

86, 87, 88, 89, 90};

  

#endif
```
- Input size: Search for `YOLO11_OB_INPUT_TENSOR_WIDTH` and `YOLO11_OB_INPUT_TENSOR_HEIGHT`. They are typically 224 for no_post and 192 for post (see notes).
- Build variant: Search for `YOLO11_NO_POST_SEPARATE_OUTPUT`. One build uses 3 outputs (no_post, 224, smaller arena); the other uses 1 output (post, 192, larger arena).
- Tensor arena: Search for `tensor_arena_size` (e.g. 442_1024 vs 1061_1024).
- Init: Function `cv_yolo11n_ob_init` – where stride/anchor are allocated (e.g. 28²+14²+7² for 224).
- Output order: Where interpreter outputs are assigned to `output[0..2]`. Your notes say: fork uses fixed order; “test”/improved version uses shape-based order (28×28, 14×14, 7×7) so 224 works regardless of Vela’s output order.
- Post-processing: `yolo11_ob_post_processing` and the 3-output vs 1-output paths (and any YOLO26 dispatch if present).
