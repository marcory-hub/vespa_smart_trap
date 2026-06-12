# Scripts (agent)

- Index: `scripts/script-index.md` (read before proposing new tools).
- Layout: `scripts/[task_name]/` only.
- Activate: `source .venv/bin/activate`
- Extend existing scripts when possible; avoid duplicate utilities.
- Dataset edits: delegate review to `dataset-guard` subagent when labels or splits change.
- Never rename paired `.jpg` / `.txt` label files.
