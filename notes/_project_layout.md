**One-line purpose:** Single place that explains how my Vespa / GV2 / ESP32 projects fit together, for me and for agents. Only my own repos are listed.
**Short summary:** 
**Agent:** SoT - this is where code lives and dies, keep monorepo
**Main Index:** [[__vespa_smart_trap]]
**User:** start new task with @folder_name

---
workflow for gv2_sd
- use repo for code changes
- open gv2_sd in new window for platformIO build upload monitor

gv2 firmware fork [[submodule]]
[[submodule update]]

---

**vespa_smart_trap**: single monoreporoot contains all active work

**Top-level layout**
- **gv2_firmware**: builds GV2 image (Himax output.img). Only writable Himax forks; dead-end prototypes move to archive as read-only.
- **gv2_esp32_sd**: GV2 image adaptation + ESP32-S3 firmware for saving images to SD. Two parts: (1) adapted GV2 output.img, (2) ESP32-S3 (e.g. PlatformIO) firmware. Formerly gv2_sd.
- **data**: dataset, test images and labels. No production code here.
- **scripts**: small utilities, per prototype in one subfolder.
- **notes**: read-only, user updates in Obsidian. Stay private after publication; external brain and teacher.
- **experiments**: single repo, start subfolder with `yyyy-mm-dd-`. Dead-ends go to archive; distilled versions can promote to umbrella or focussed hardware repo.
- **tests:**
- **z_archive**: third-party repos and legacy, read-only.

**Release models and firmware**
- Curated .tflite and .img live in **gv2_firmware/model_zoo** (and firmware repo’s build output), not in a root-level artifacts/ directory.

**Subfolders in gv2_firmware**
- model (model_zoo): Vela-compiled, full quantized tflite models.
- experiments
	- feat/yolo11-sd-save
	- fix/uart1