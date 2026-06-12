---
name: handoff
description: Writes timestamped session handoff markdown for the next Cursor chat. Use when ending a session, starting fresh chat, @handoff, session continuity, or agent handoff.
disable-model-invocation: true
---

# Handoff

Persist **session state on disk** so the next chat does not rely on memory or long paste. Complements Cursor `@Past Chats` ([agent best practices](https://cursor.com/blog/agent-best-practices)) and `.cursor/plans/` (Plan Mode).

## When to run

- User says `@handoff`, "write handoff", or "end session"
- Before starting a **new chat** after long/noisy thread
- After a lesson block (`@teach-me`) or multi-step ops (GCE, flash, train)

Start a **new conversation** when scope changes or agent quality drops; load this skill in the new chat.

## Where files go

| Path | Role |
| :--- | :--- |
| `.cursor/skills/handoff/sessions/yyyy-mm-ddTHHmm-<slug>.md` | Immutable snapshot |
| `.cursor/skills/handoff/sessions/latest.md` | Overwritten; open with `@handoff` |
| [HANDOFF-FORMAT.md](HANDOFF-FORMAT.md) | Template |

`sessions/` is gitignored (may contain VM URLs). Skill + format stay tracked.

## Write workflow (agent)

1. Gather from chat: mission, done, **one** next step, todos, blockers, branch, environment.
2. Slug from mission (e.g. `gce-vela`, `flash-gv2`). Time: ISO `yyyy-mm-ddTHHmm` (local).
3. Write **both** timestamped file and `sessions/latest.md` using [HANDOFF-FORMAT.md](HANDOFF-FORMAT.md).
4. If Plan Mode file exists in `.cursor/plans/`, link it under **Pointers** (do not duplicate the plan).
5. If `@teach-me`: link `docs/teaching/MISSION.md` and lesson in `notes/` plan file; tell user to update Obsidian status table.
6. Confirm paths written; paste **Fresh-chat opener** for user to copy.

## Read workflow (new chat)

1. Read `sessions/latest.md` first; read timestamped file only if user names it.
2. Read pointers (notes, plans, teaching) before acting.
3. Honor **Mode** in opener: `teach` = user runs commands; `apply` = agent may edit/run.

## Layering (do not duplicate)

| Layer | Use for |
| :--- | :--- |
| **Handoff** | Session snapshot, next step, blockers, todos |
| `.cursor/plans/` | Feature implementation plan (Plan Mode) |
| `notes/` | Project facts, pinouts, roadmap |
| `docs/teaching/` | Learning mission and preferences |
| Rules / skills | Stable how-to |

## vespa_smart_trap defaults

- Label **Mac** (`md@m2`) vs **VM** (`vst-vela-01`) on every command in handoff.
- GCP IDs when relevant: `pt-vela`, `vst-vela-01`, `europe-west4-a`, `pt-vela-gce`.
- Never store Jupyter tokens or credentials in handoff.

## Out of scope

- Replacing `notes/` or `docs/teaching/` as SoT for hardware/model facts
- Auto-commit handoff files (user commits if they want history in git)
