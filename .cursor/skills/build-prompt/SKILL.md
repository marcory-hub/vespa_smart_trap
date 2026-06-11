---
name: build-prompt
description: VST overlay for build-prompt. Interview for a plan-mode agent prompt when user says build prompt, make prompt, or advise about prompt. New project phase only; full path. Requires @research-gaps when infra unknown. Constraints from .cursor/rules/*.mdc only.
disable-model-invocation: true
---

# Build Prompt (vespa_smart_trap)

Read generic skill at `~/.cursor/skills/build-prompt/SKILL.md`, then this overlay and [vst-sections.md](vst-sections.md).

## Invoke only when user says

`build prompt`, `make prompt`, `advise about prompt`, or `@build-prompt`.

Not for bugfixes, small edits, or mid-task tweaks. **Full path only** (no triage).

## Prerequisites

- Unknown GCE/migration/vendor topics: `@research-gaps` completed; deliverable in Obsidian (paste or attach).
- If research needed but missing: stop → send user to `@research-gaps` in a **new chat**.

## Preflight

1. Read `.cursor/rules/project-context.mdc`.
2. Read user's research deliverable from Obsidian if provided.
3. Search `scripts/`; read `scripts/script-index.md` if present.
4. Read `notes/` paths from project-context.
5. Note applicable `.cursor/rules/`, `.cursor/skills/`, `.cursor/commands/`.

## Constraints

**Do not hardcode** veto lists. Delivered prompt must say: follow attached `@project-context`, `@safety-guardrails`, `@global-rules`, `@agent-persona`.

## Interview

Use sections in [vst-sections.md](vst-sections.md). Max 3 questions per turn. Default delivered prompt mode: **plan only**.

| Type | Primary sections |
| :--- | :--- |
| Code | software, files, verification |
| Hardware | hardware, verification |
| Environment | colab, GCE, env/migration, verification |
| Migration | colab, GCE, env/migration + research deliverable |

## Done when

Filled [prompt-template.md](prompt-template.md), attachment tiers, `[to be verified]` list, next-chat instructions.

## Pipeline (separate chats)

```
A  @research-gaps   → deliverable → Obsidian
B  @build-prompt   → prompt      → Obsidian
C  paste prompt    → plan only   → Obsidian
D  @grill-me       → refined plan/prompt (use after grill-me finishes)
E+ implementation  → operator mode only when user requests
```

## Assembly

1. First line: **Plan only. No file edits.**
2. Embed research summary from Obsidian if present.
3. Constraints: point to `.mdc` only ([prompt-template.md](prompt-template.md)).
4. Required `@` attachments: minimal set from project-context.
5. End: "Read attached SoT before proposing architecture."
