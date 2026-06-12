# Mission: GCE VELA migration

## Why

Run the VELA export notebook on user-owned GCE before Colab runtime 2025.07 EOL (~2026-07). Training stays on Colab.

## Success

- `best_full_integer_quant_vela.tflite` ≤ 2.4 MB on GV2
- Parity with last Colab VELA run
- I can operate GCP (project, bucket, VM, stop/teardown) without hand-holding

## How I learn

- `@teach-me` + `notes/vst plan GCE VELA migration.md`
- One lesson per session; I run commands myself
- Agent explains, checkpoints, does not execute cloud ops unless I say apply

## Roadmap

Lesson track in plan file; update progress table after each session.
