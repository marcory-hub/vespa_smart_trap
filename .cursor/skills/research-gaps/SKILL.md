---
name: research-gaps
description: VST overlay for research-gaps. Resolve unknown GCE, Colab migration, hardware vendor behavior, or other gaps before @build-prompt. Use only when user invokes @research-gaps. Separate chat; deliverable goes to Obsidian first.
disable-model-invocation: true
---

# Research Gaps (vespa_smart_trap)

Read the generic skill at `~/.cursor/skills/research-gaps/SKILL.md`, then apply this overlay.

## VST preflight (adds to generic)

1. Read `.cursor/rules/project-context.mdc` for SoT paths and stack constraints.
2. Read `notes/` paths from project-context (`notes/` is gitignored but indexed via `.cursorignore`).
3. Read [vst-topics.md](vst-topics.md) for common research patterns and examples.

## VST research topics

See [vst-topics.md](vst-topics.md). Default **needs research**: GCE (no repo SoT), Colab → GCE migration, new hardware without datasheet in notes.

## Deliverable

Use [deliverable-template.md](deliverable-template.md). User pastes into Obsidian, then **new chat** → `@build-prompt`.
