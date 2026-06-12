---
name: uart-debug
description: Debug GV2 USB serial at 921600 and mixed INVOKE JSON streams. Use when serial blocked, no inference, or @uart-debug.
---

# UART debug

Follow `.cursor/skills/read-notes/SKILL.md` for `notes/_hardware_vst.md` (pinouts, GV2-T-SIM UART).

**Escalation ladder** (stop at first fix): flash verify (`@flash-gv2`) → port conflict → INVOKE parse → `@model-test`.

## Loop (diagnose-style)

1. **Reproduce:** read user's terminal capture; confirm symptom matches (no bytes vs garbled vs no INVOKE).
2. **Minimise:** one client on one port; close Himax AI web toolkit; stop PIO monitors and `benchmark_runner.py`.
3. **Hypothesise:** rank 3 falsifiable causes before changing baud or re-flashing.
4. **Fix:** one change at a time; re-run minimal read test.
5. **Regression:** `@model-test` or known INVOKE on hornet image.

## Defaults

- **Baud:** `921600`
- **Interactive port (macOS):** `/dev/cu.usbmodem*` (`ls /dev/cu.usbmodem*`)
- **Scripts** may use `/dev/tty.usbmodem*`; same device, different API
- **INVOKE:** mixed text + JSON; parsers keep `name == "INVOKE"` (`scripts/gv2_yolomodel_test/benchmark_runner.py`)

## Bench vs trap

- **Bench (this skill):** GV2 USB debug serial for INVOKE during model test
- **Field trap:** detections to T-SIM over PCB UART per `_hardware_vst.md`; not the USB port

## Quick fixes

- After flash: press reset; reseat USB-C if inference never starts
- xmodem fails: unplug ESP32 from GV2 Grove socket (`README.md`)
- `pyserial` in `.venv`

**WARNING: Irreversible operation. Data loss/Overwrite risk.** before re-flashing only after port and parse checks fail.
