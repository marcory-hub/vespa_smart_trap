---
name: read-notes
description: Load facts from gitignored notes/ with mandatory Read verification before answering. Use when hardware, timeline, model, datasets, pinouts, roadmap, flash steps, read notes, or @read-notes.
---

# Read notes first

`notes/` is gitignored. **Read** on an exact path is the only trusted source; Glob/Grep alone are not enough.

## Workflow

1. Pick path from the table below (broad topic: start `notes/__vespa_smart_trap.md`).
2. **Read** full path string with Read tool.
3. If Read fails or file empty: stop; point to `notes/_cli_vst.md`. Do not invent paths.
4. Cite `(notes/_file_vst.md:line)`. Do not paste large blocks into git-tracked files unless asked.

## Topic to path (single router)

| Topic | Read first |
| :--- | :--- |
| Index | `notes/__vespa_smart_trap.md` |
| CLI / Obsidian sync | `notes/_cli_vst.md` |
| Roadmap / milestones | `notes/_timeline_vst.md` |
| Hardware / GPIO / UART | `notes/_hardware_vst.md` |
| Datasets | `notes/_datasets_vst.md` |
| Training / swift-yolo | `notes/swift-yolo documentation.md`, `notes/_model_vst.md` |
| Model versions | `notes/_model_vst.md` |
| Layout | `notes/_project_layout_vst.md` |
| Meetings (not SoT) | `notes/_meetings_vst.md` |

Matrix pointer: `.cursor/rules/project-context.mdc`.

## Roadmap edits

When user logs a win: suggest 1 to 3 past-tense bullets under `yyyy-mm-dd` for `_timeline_vst.md`. User writes in Obsidian unless apply to file.

## Do not

- Answer from memory or prior chat without successful Read
- Wrong paths (`_hardware_stack.md`; use `_hardware_vst.md`)
