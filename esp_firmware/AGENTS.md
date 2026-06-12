# ESP firmware (agent)

Host-side ESP32-S3 firmware (UART receiver, LED tests). GV2 runs inference.

- Style: Google C++ Style (Arduino/ESP32).
- Hardware facts: `notes/_hardware_vst.md` via read-notes skill.
- After substantive edits: invoke `gv2-embedded-reviewer` subagent.
- Flash GV2 models: `@flash-gv2` command + `.cursor/skills/flash-gv2/SKILL.md` (not esptool on ESP32 here).
