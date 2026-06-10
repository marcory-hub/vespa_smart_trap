---
name: flash-gv2
description: Decides when to flash GV2, how to verify the model, and when to escalate. Use when flashing GV2, verify model flashed, or @flash-gv2.
---

# Flash GV2 (judgment)

**Run steps:** `@flash-gv2` command. **Operator SoT:** `README.md` flash section (paths, hex, xmodem log). Do not duplicate bash blocks here.

Read `notes/_hardware_vst.md` via `.cursor/skills/read-notes/SKILL.md` before stating pin or SRAM facts.

## When to flash

- New `int8_vela.tflite` after Colab train/quant (`.cursor/skills/train-colab-vela/SKILL.md`)
- Firmware rebuild with new `APP_TYPE` or model path in `gv2_firmware/`
- Not for UART-only debug (`.cursor/skills/uart-debug/SKILL.md`)

## Verify (flash succeeded vs model wrong)

| Signal | Meaning |
| :--- | :--- |
| xmodem 100% on expected `.tflite` | Image and model slot written |
| No INVOKE on serial | Wrong firmware build, wrong model path, or UART issue: escalate `@uart-debug` |
| INVOKE but bad classes | `@model-test` or retrain; flash may be fine |

## After success

Offer: run `@model-test` on a known image. If user logs milestones, suggest 1 to 2 bullets for `notes/_timeline_vst.md` (user writes in Obsidian).

## Git

Submodule changes: `@security-audit` then `@push-submodule`. User provides exact commit message.

## Do not

- Invent flash offsets or model filenames
- Push to upstream Himax
