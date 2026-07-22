**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---

int8_tflite to vela on mac mini m2

**One-line purpose:** Export int8 TFLite to Vela command for GV2.

**Source:** old notes from zzzArchive

---

## Where to run from

**All paths are relative to your current working directory.** If you are in `vela/`, then `scripts/pt_to_vela/...` does not exist there. Either:

- **Option A:** `cd` to repo root (`vespa_smart_trap/`), then use the commands below with `scripts/...`, or  
- **Option B:** Stay in `vela/` and use the "From `vela/`" block below.

## Config file

- Repo config: `scripts/pt_to_vela/himax_vela.ini`.
- From **repo root**: `--config scripts/pt_to_vela/himax_vela.ini`.
- From **`vela/`**: `--config ../scripts/pt_to_vela/himax_vela.ini`.

## Command (input file first)

Vela expects the **input .tflite as the first argument**, then options. `--output-dir` is relative to cwd unless you use an absolute path.

**From repo root** (venv with `vela` activated):

```bash
vela /Users/md/Downloads/best_saved_model/best_full_integer_quant.tflite \
  --accelerator-config ethos-u55-64 \
  --config scripts/pt_to_vela/himax_vela.ini \
  --system-config My_Sys_Cfg \
  --memory-mode My_Mem_Mode_Parent \
  --output-dir /Users/md/Downloads
```

Script (must run from repo root):

```bash
./scripts/pt_to_vela/run_vela.sh /Users/md/Downloads/best_saved_model/best_full_integer_quant.tflite /Users/md/Downloads
```

**From `vela/`** (e.g. you activated `vela/.venv` and stayed in `vela/`):

```bash
vela /Users/md/Downloads/best_saved_model/best_full_integer_quant.tflite \
  --accelerator-config ethos-u55-64 \
  --config ../scripts/pt_to_vela/himax_vela.ini \
  --system-config My_Sys_Cfg \
  --memory-mode My_Mem_Mode_Parent \
  --output-dir /Users/md/Downloads
```

Script from `vela/`: `../scripts/pt_to_vela/run_vela.sh ...` (script itself will `cd` to repo root, so this works).


## Why `vela` was not found in the first venv

After `pip install ethos-u-vela` in `vespa_smart_trap/.venv`, `vela` is installed in that venv’s `bin/`. You must have that venv activated in the shell where you run `vela` (e.g. `source .venv/bin/activate` from repo root). In your log you ran `vela` before activating the venv in that shell, so the shell used the system PATH and didn’t find `vela`. In the separate `vela/` folder you created a new venv, activated it, installed ethos-u-vela again, and then `vela` worked — but the config path was wrong because `himax_vela.ini` is not in `vela/`.

---

## Troubleshooting: TRANSPOSE warnings and Vela crash

If Vela runs but then fails:

1. **TRANSPOSE warnings**  
   Many “TRANSPOSE … is not supported on the NPU. Placing on CPU instead” messages, with permutations like `[0 1 3 2]`, `[0 3 1 2]`, `[0 2 3 1]`, `[3 1 2 0]`, are expected for **YOLO11n** int8 TFLite. Vela only supports a subset of 4D transposes; the rest are run on CPU. See [[himax_vela]] § Vela compatibility (YOLO11n).

2. **Crash: `TypeError: only 0-dimensional arrays can be converted to Python scalars`**  
   Failure inside Vela’s graph optimiser: `tflite_graph_optimiser.py` → `rewrite_split_ops` → `operation.py` `get_split_inputs_axis()` at `axis = int(axis_tens.values)`. The model’s graph (likely from standard YOLO11n export) triggers this; the current int8 TFLite is not compatible with this Vela version/pipeline.

3. **What to do**  
   - Re-export for Vela-friendly graph: use **YOLOv8n** export, or **YOLO11n** with `nms=False` and `simplify=True`, or the **YOLO11_on_WE2** / **YOLOv8_on_WE2** flow (export + transpose handling). See [[himax_vela]] § Vela compatibility and § Reproduction pipeline, and [[himax vela]] for ONNX-simplify → onnx2tf → TFLite.  
   - The 2025-09-01 working model (`yolo11n_2025-09-01_224_e300_full_integer_quant_vela.tflite`) was produced from a Colab export that is not in this repo; reproducing it requires the same export/WE2 or transpose-handling steps.

---
