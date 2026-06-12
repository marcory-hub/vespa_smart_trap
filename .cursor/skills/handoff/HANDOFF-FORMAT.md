# Handoff file format

Filename: `yyyy-mm-ddTHHmm-<slug>.md` (ISO 8601 local time, slug = lowercase hyphenated topic).

Also write/overwrite: `sessions/latest.md` (same content; entry point for `@handoff`).

## Template

```markdown
# Handoff: <title>

**Created:** yyyy-mm-ddTHHmm
**Status:** active | blocked | done
**Branch:** <git branch or n/a>
**Mission:** <one sentence goal>

## Done this session

- [x] item

## Next step (single)

One executable step for the next agent or chat.

## Todo

- [ ] item
- [ ] item

## Blockers / failed attempts

- What was tried and why it failed (prevents repeat loops)

## Environment (if relevant)

| Key | Value |
| :--- | :--- |
| Machine | Mac vs vst-vela-01 |
| Services | Jupyter up/down, tunnel port |

## Pointers

- Plan: `.cursor/plans/<file>.md` (if any)
- Teaching: `docs/teaching/MISSION.md`
- Notes: `notes/<plan>.md`
- Artifacts: paths, bucket URIs (no secrets)

## Fresh-chat opener

```text
@handoff
Continue from latest handoff. Mode: teach | apply.
```

## Rules

- No API keys, tokens, or passwords in handoff files.
- Facts that belong in Obsidian go in `notes/`; handoff is session state only.
- One **Next step** only; queue extras under **Todo**.
```
