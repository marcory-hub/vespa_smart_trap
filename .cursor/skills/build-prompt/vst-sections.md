# VST interview sections

## 1. Intent, work type, scope

- One-sentence goal, why now, success criteria, non-goals
- Work type: Code / Hardware / Environment / Migration
- Migration: source → target, parity requirements

## 2. Hardware

From `notes/_hardware_vst.md` when available.

- Boards: GV2, T-SIM7080G-S3, both
- Pinouts, UART baud, camera/resolution, SRAM (GV2 < 2.4MB)
- New hardware: datasheet, integration, bring-up, safety
- Firmware: `gv2_firmware/` branch if embedded

## 3. Software

- Runtime: GV2 embedded, host Python, web UI
- Python: local `.venv`; Colab 3.11 / 2025.07 for training
- Model: `int8_vela.tflite` (not raw `int8.tflite`); YOLO11n; resolution per hardware note
- Layout: `scripts/[task_name]/` unless firmware

## 4. Colab / training

Skip if N/A.

- Notebooks on `marcory-hub/Seeed_Grove_Vision_AI_Module_V2` `main`
- `@sync-colab-notebooks` → `colab-notebooks/`
- `notes/_datasets_vst.md`, outputs (`.pt`, `int8_vela.tflite`)
- Migration: which cells move off Colab

## 5. GCE

Skip if N/A. Requires `@research-gaps` deliverable unless user cites a note/runbook.

## 6. Persona, rules, skills, commands

| Attach | When |
| :--- | :--- |
| `project-context.mdc` | always |
| `safety-guardrails.mdc` | always |
| `agent-persona.mdc` | persona / edit gate |
| `global-rules.mdc` | code style |
| `@grill-me` | after plan in Obsidian |
| `@sync-colab-notebooks` | notebook sync |
| `@push-submodule` | firmware submodule |

## 7. Files and context

- Notes: hardware, model, datasets, timeline, layout (paths from project-context)
- Scripts to extend, `gv2_firmware/`, env var names (no secrets)
- Gitignored artifacts agent must know: datasets, `colab-notebooks/`, weights

## 8. Constraints

Read from `.mdc` at assembly; ask user only for **overrides** to timeline.

## 9. Verification

- Automated, hardware, env/migration parity, rollback
- Must not break existing scripts/firmware/Colab during parallel trial

## 10. Environment and migration

- Target: `.venv`, Colab, GCE, hybrid
- Cutover, reproducibility runbook location, rollback

## 11. Logistics

- Deadline, blockers, PR to `marcory-hub/vespa_smart_trap`, follow-up in `notes/_timeline_vst.md`
