# MISSION.md format

Every teaching decision traces back here.

## Template

```md
# Mission: {Topic}

## Why
{1-3 sentences. Concrete real-world goal. What changes when they have this skill?}

## Success looks like
- {Observable capability}
- {Another observable capability}

## Constraints
- {Time, budget, gear, learning preferences}

## Out of scope
- {Topics to defer; protects zone of proximal development}
```

## Rules

- **One mission per `teaching/` workspace.** Unrelated topics: separate workspace or mission swap with user confirm.
- **Concrete over abstract.** "Flash YOLO11n to GV2 without bricking the board" beats "understand embedded AI."
- **Push back on vagueness.** Interview before writing; bad mission worse than none.
- **Revise when reality shifts.** Update file; add learning record (see `LEARNING-RECORD-FORMAT.md`).
- **Keep short.** Past one screen it is a plan, not a compass.

Project trap facts (pinouts, model versions) stay in `notes/` via `read-notes`; mission is why the user learns, not hardware SoT.
