---
name: set-threshold
description: Set the confidence thresholds used for LED triggering from GV2 detections over I2C. Use when the user asks to change threshold, confidence cutoff, reduce false positives, or tune when red/green LEDs turn on/off.
---

# Set threshold (GV2 -> ESP32 I2C LEDs)

## Goal
Update the GV2 firmware so low-confidence detections do not trigger LEDs, by adjusting confidence thresholds for:
- Class 3 (Asian hornet) → red LED
- Any other class → green LED

This project currently uses a 1-byte I2C status protocol from GV2 to ESP32 at I2C address `0x63`.

## Source of truth (files to edit)
- GV2: `gv2_firmware/EPII_CM55M_APP_S/app/scenario_app/tflm_yolo11_od/tflm_yolo11_od.c`
- ESP32: `experiments/gv2_esp32_sd/src/main.cpp` (only if I2C address changes)

## How to implement
1. In `tflm_yolo11_od.c`, locate `update_i2c_detection_state_from_algo_result()`.
2. Use **separate thresholds** but default both to `0.60`:
   - `kMinConfidenceHornet = 0.60f`
   - `kMinConfidenceOther = 0.60f`
3. Apply logic:
   - Ignore any box with `confidence < min_threshold_for_that_class`.
   - If any qualifying box has `class_idx == 3`, set state byte to `0x01`.
   - Else if any qualifying box exists (any other class), set state byte to `0x02`.
   - Else set state byte to `0x00`.
4. Keep I2C address at `0x63` unless explicitly requested otherwise.

## Build + flash workflow (GV2)
Follow the repo’s existing GV2 build steps to generate and flash `output.img`, then power-cycle GV2.

## Quick verification checklist
- ESP32 I2C scan shows `0x63`.
- With no object: LEDs off.
- With class 3 confidently detected: red on.
- With other class confidently detected: green on.
- With low-confidence noise: LEDs remain off.

