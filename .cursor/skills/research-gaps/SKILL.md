---
name: research-gaps
description: Resolve unknown GCE, Colab migration, hardware vendor behavior, or other gaps before @build-prompt. Use only when user invokes @research-gaps. Separate chat; deliverable goes to Obsidian first.
disable-model-invocation: true
---

# Research Gaps (vespa_smart_trap)

Close factual gaps before `@build-prompt`. **Separate chat**; paste deliverable into Obsidian.

## When to run

- GCE, migration, or vendor behavior not in `notes/` or repo
- User says `@research-gaps` or "research gaps"
- `@build-prompt` blocked on unknown infra

## VST preflight

1. Read `.cursor/rules/project-context.mdc` for SoT paths and stack constraints.
2. Read `notes/` paths from project-context (`notes/` is gitignored but indexed via `.cursorignore`).
3. Read [vst-topics.md](vst-topics.md) for common research patterns.
4. Search `scripts/`, `gv2_firmware/`, `notebooks/` (read-only) for existing code.

## Workflow

1. State the blocking question in one line.
2. Search repo and notes first; cite `(file:line)` or mark `[to be verified]`.
3. Web or vendor docs only when repo/notes lack answers; cite URL and date.
4. Produce recommendation table with confidence (high / medium / `[to be verified]`).
5. Fill [deliverable-template.md](deliverable-template.md) for Obsidian paste.

## VST research topics

See [vst-topics.md](vst-topics.md). Default **needs research**: GCE (no repo SoT), Colab → GCE migration, new hardware without datasheet in notes.

## Out of scope

- Implementation or file edits (plan/research only)
- Inventing pinouts, cell contents, or GCP resource IDs

## Next step

New chat → `@build-prompt` with Obsidian deliverable attached or pasted.
