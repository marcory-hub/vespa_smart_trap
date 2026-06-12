---
name: teach-me
description: Teaches concepts over multiple sessions using a teaching/ workspace. Use when user says teach me, learn about, explain step by step to learn, or @teach-me.
---

# Teach me

Adapted from [mattpocock/teach](https://github.com/mattpocock/skills/blob/main/skills/productivity/teach/SKILL.md). **Only when invoked**; default chats stay direct.

Stateful across sessions. Ground in mission, glossary, learning records, and resources.

## Workspace (`teaching/`)

| Path | Role | Format |
| :--- | :--- | :--- |
| `teaching/MISSION.md` | Why user learns | [MISSION-FORMAT.md](MISSION-FORMAT.md) |
| `teaching/GLOSSARY.md` | Canonical terms | [GLOSSARY-FORMAT.md](GLOSSARY-FORMAT.md) |
| `teaching/RESOURCES.md` | Trusted sources | [RESOURCES-FORMAT.md](RESOURCES-FORMAT.md) |
| `teaching/NOTES.md` | User preferences | freeform |
| `teaching/learning-records/` | ADR-style insight | [LEARNING-RECORD-FORMAT.md](LEARNING-RECORD-FORMAT.md) |
| `teaching/lessons/` | One concept per file | `0001-slug.md`, increment |
| `teaching/reference/` | Cheat sheets, pinouts | revisit often |

Create on disk when user says apply to file or agrees to persist; else teach in chat.

## Start

1. Read `teaching/MISSION.md` if present; else interview for why (one question at a time; use `MISSION-FORMAT.md`).
2. Read `teaching/learning-records/` and `teaching/GLOSSARY.md` for zone of proximal development.
3. **vespa_smart_trap facts:** `.cursor/skills/read-notes/SKILL.md` only; never invent hardware or model data.

## Lesson

One tight concept; tied to mission; markdown in `teaching/lessons/`. Flow: minimal why → practice → check understanding. Cite `RESOURCES.md` entries. Use `GLOSSARY.md` terms in lessons once promoted. Hardware/flash: `safety-guardrails.mdc` warnings. No em dash or emojis in files.

## Feedback

User tries step or answers → specific feedback → next lesson. Prior knowledge or corrected misconception → learning record per `LEARNING-RECORD-FORMAT.md`.

## Mission or glossary changes

Confirm with user; update file; learning record if mission shifts.

## After session

If project facts changed, ask user to update `notes/` (`project-context.mdc`).

## Out of scope

- Default chat without `@teach-me`
- Replacing `read-notes` SoT
