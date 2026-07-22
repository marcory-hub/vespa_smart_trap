# GV2 YOLO Model Test Plan

## Objective

Build `experiments/gv2_yolomodel_test` with `slideshow_server.py`, `benchmark_runner.py`, and `requirements.txt` to benchmark deployed GV2 YOLO model outputs from serial-only data against filename-derived ground truth.

## The Plan

- Create folder and file skeleton under `experiments/gv2_yolomodel_test`.
    
- Implement `slideshow_server.py`:
    
    - Serve a minimal local webpage that displays one image from `data/test/images/` at approximately 10 cm width (`~378px`) with a clear in-page note `[to be verified by user]`.
        
    - Expose a simple localhost HTTP endpoint to switch active image (`POST /show` with image path or filename).
        
    - Expose a small status endpoint (`GET /current`) so runner can verify what is shown.
        
- Implement `benchmark_runner.py`:
    
    - Prompt user for model name string.
        
    - Load all images from `data/test/images/`, enforce deterministic random order (`seed=42`), target expected count 388 with graceful warning if count differs.
        
    - For each image: call slideshow endpoint to display image; first image wait 30s; all next images wait 1s; then read serial stream from `/dev/tty.usbmodem58FA1047631` at `921600`.
        
    - Parse serial safely: extract valid JSON objects from mixed stream; keep only objects with `"name": "INVOKE"`; ignore other messages and large `image` fields.
        
    - From `data.boxes`, choose highest-score box using second-to-last value as score and last value as class_id; if missing/empty or below optional threshold, mark `No Detection`.
        
    - Parse filename ground truth: view token (`top`, `sid`, `oth`) and class token mapping (`amel=0`, `vcra=1`, `vesp=2`, `vvel=3`).
        
    - Write `results_{model_name}.csv` with `Image_Path, Ground_Truth, Predicted, Score, Result`.
        
    - Print 4x4 class confusion table and class metrics (accuracy/precision/recall) plus view metrics (`top/sid/oth`).
        
    - Handle unplugged serial device with clear exit message and non-crashing shutdown.
        
- Implement `requirements.txt` with only required helper libraries.
    
- Keep code simple/safe (small functions, explicit errors, no firmware writes).
    

## Safety/Verification Check

- `[to be verified]` Confirm first displayed image on monitor is physically ~10 cm wide after browser scaling/zoom; CSS pixel estimate is approximate.
    
- `[to be verified]` Confirm confidence threshold behavior and default value (apply none by default vs default=50).
    
- `[to be verified]` Confirm whether serial stream already continuously emits INVOKE messages or whether runner should send a startup invoke command; current plan assumes read-only monitoring and no control commands.
    
- `[to be verified]` Confirm all test filenames strictly follow `<view>_<label>_<id>.jpg` pattern for robust parsing.
    
- Warning: benchmark is read-only over serial and must not flash firmware or alter deployed model.

Here we hear a remarkable specimen: the Stoney Eagle. Sleeping at daytime, at night the uses his artificial companions as slaves to build his codebase.

!narrator Here we hear a remarkable specimen: the @Stoney_Eagle. Sleeping at daytime, at night the uses his artificial companions as slaves to build his codebase.