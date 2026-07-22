
**One-line purpose:** 
**Short summary:** 
**Agent:** 

---

vela = Ethos-U55 compiler

**Run Vela locally (macOS):** Vela does not work in Colab. On Mac: `pip install ethos-u-vela`, then run the `vela` CLI on your int8 TFLite. Full steps (config, command, output dir): [[himax_2025]] section 8 "Run Vela locally (macOS)".

In order to be accelerated by the Ethos-U NPU the network operators must be quantised to either 8-bit (unsigned or signed) or **16-bit (signed)**. [bron](https://github.com/HimaxWiseEyePlus/Edge-Impulse-model-on-Himax-AI)

[vela config file](https://files.seeedstudio.com/sscma/configs/vela_config.ini)

```
vela_config = "/content/drive/MyDrive/himax_vela.ini"
```

## Potential YOLO11n "Component 4" Removal

**Note: User mentioned a GitHub discussion about removing "component 4" from YOLO11n for Vela compatibility**

### Possible References:
1. **Class 4 removal** - Removing 4th class from multi-class model
2. **Layer/Component index 4** - Specific architectural component
3. **Model architecture modification** - Removing problematic operations

### GitHub Issue Reference:
- "Remove/add class from yolo11n.pt" - [GitHub Issue #17459](https://github.com/ultralytics/ultralytics/issues/17459)
- Focuses on modifying class definitions in configuration files
- May not directly address Vela compatibility issues

### Potential Investigation:
```python
# Analyze model structure to identify "component 4"
import tensorflow as tf

interpreter = tf.lite.Interpreter(model_path="yolo11n_int8.tflite")
interpreter.allocate_tensors()

# List all tensors to identify problematic components
for i, detail in enumerate(interpreter.get_tensor_details()):
    print(f"Tensor {i}: {detail['name']} - Shape: {detail['shape']}")
```

**TODO: Find the specific GitHub discussion about "component 4" removal**

## Vela Compatibility Issues with YOLO11n

### Problem: TRANSPOSE Operations Not Supported
YOLO11n contains TRANSPOSE operations that don't match Vela's supported patterns:
- `[1, 4, 16, 756]` with permutation `[0 1 3 2]` ❌
- `[1, 24, 24, 68]` with permutation `[0 3 1 2]` ❌
- `[1, 128, 6, 6]` with permutation `[0 2 3 1]` ❌

**Vela only supports:**
- 4D: `1xHxWxC -> 1xWxHxC`, `1x1xWxC -> 1x1xCxW`, `1xHx1xC -> 1xCx1xW`

### Problem: Non-constant Weight Tensors
```
FULLY_CONNECTED operations with non-constant weight tensors
- Weight tensor must be constant for NPU acceleration
```

### Problem: IndexError in Graph Optimization
```
IndexError: invalid index to scalar variable
```
Occurs during Vela's graph rewriting phase.

### Problem: Vela completes but 100% CPU (0% NPU)
Vela runs without crashing but reports:
- `CPU operators = 345 (100.0%), NPU operators = 0 (0.0%)`
- Many warnings: "Op has tensors with missing quantization parameters", "Tensor ... has data type: float32"

**Cause:** The TFLite fed to Vela is not fully integer-quantized. Some subgraphs (often YOLO11n backbone/head, C2f/attention, DFL) remain float32 or lack quantization parameters, so Vela cannot place them on the Ethos-U NPU and falls back to CPU. The export step (Ultralytics .pt → int8 TFLite) did not produce a true full-integer model.

**Fix:** Ensure the export uses full integer quantization and that all ops get quantized: `fraction=1.0`, sufficient calibration data, and a calibration dataset that exercises all branches. If Ultralytics still emits hybrid float/int8 for YOLO11n, try the YOLOv8n export (Solution 1 below) or the Himax YOLO11_on_WE2 / YOLOv8_on_WE2 export flow that produces NPU-compatible TFLite.

## Solutions

### Solution 1: Use YOLOv8n (Recommended)
YOLOv8n has better Vela compatibility:
```python
model = YOLO("yolov8n.pt")
model.export(
    format="tflite",
    int8=True,
    imgsz=192,
    data="data.yaml",
    fraction=1.0,
    simplify=True
)
```

### Solution 2: Simplified YOLO11n Export
```python
model = YOLO("yolo11n.pt")
model.export(
    format="tflite",
    int8=True,
    imgsz=192,
    data="data.yaml",
    fraction=1.0,
    simplify=True,
    nms=False  # Disable NMS for better compatibility
)
```

### Solution 3: ONNX Simplification Pipeline
```python
# Export to ONNX
model = YOLO("yolo11n.pt")
onnx_path = model.export(format="onnx", opset=17)

# Simplify ONNX model
!pip install onnx-simplifier
import onnxsim
onnx_model = onnx.load(onnx_path)
simplified_model, check = onnxsim.simplify(onnx_model)
onnx.save(simplified_model, "yolo11n_simplified.onnx")

# Convert to TFLite
!pip install onnx2tf
import onnx2tf
onnx2tf.convert(
    input_onnx_file="yolo11n_simplified.onnx",
    output_folder="tflite_simplified",
    quantization=True,
    int8=True
)
```

## Vela Conversion Commands

### Standard Vela Conversion
```bash
vela input.tflite \
    --accelerator-config ethos-u55-64 \
    --config himax_vela.ini \
    --system-config My_Sys_Cfg \
    --memory-mode My_Mem_Mode_Parent \
    --output-dir output/
```

### Alternative Vela Config
```ini
[System_Config.Alternative_Cfg]
core_clock=400e6
axi0_port=Sram
axi1_port=OffChipFlash
Sram_clock_scale=1.0
Sram_burst_length=32
Sram_read_latency=16
Sram_write_latency=16

[Memory_Mode.Alternative_Mem_Mode]
const_mem_area=Axi1
arena_mem_area=Axi0
```

