---
name: project-pitch
description: Draft elevator pitches and stakeholder summaries from verified project sources. Use when project pitch, explain the whole project, elevator pitch, or @project-pitch.
---

# Project pitch

Facts only from `.cursor/skills/read-notes/SKILL.md`, `README.md`, and `.cursor/rules/project-context.mdc`. Mark gaps `[to be verified]`. No em dash, no emojis.

README procedures: `.cursor/skills/update-readme/SKILL.md`.

## Read first

Run `read-notes` for hardware, model, and recent roadmap (`_hardware_vst.md`, `_model_vst.md`, `_timeline_vst.md` recent entries only). Add `README.md` for public-facing stack summary.

## Deliver

| Request | Output |
| :--- | :--- |
| Elevator pitch | 3 to 5 sentences: problem, on-device GV2 inference, T-SIM SMS, solar/off-grid |
| Stakeholder summary | Short prose or bullets; gloss jargon once |
| External talk draft | Offer `@grill-me` before finalizing |

**Must state:** GV2 runs inference; T-SIM handles LTE/SMS; training is dev-time (Colab); deployed trap runs offline.

## Do not

- Invent pipeline steps, counts, or paths
- Publish note content to git unless user asks
- Edit `presentations/*.md` unless user explicitly requests slide file changes
