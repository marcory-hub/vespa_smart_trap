---
name: make-skill
description: Create or update Cursor Agent Skills with proper structure and repo placement. Use when the user asks to make a skill, add a workflow skill, convert repeated prompts into .cursor/skills/, or @make-skill.
---

# Make a skill

## Where things go

| Add to | When |
| :--- | :--- |
| `.cursor/skills/` | Judgment, format, read order (composable) |
| `.cursor/commands/` | Deterministic `@` runbooks with gates (flash, git sync) |
| `.cursor/rules/` | Always-on invariants and SoT pointers |

Never create skills in `~/.cursor/skills-cursor/` (Cursor internal).

**Skill vs command:** fixed shell steps with warnings → `@command` runs them; skill decides when/whether/verify and points to the command.

## Process

1. **Gather** (ask if unclear): task/domain, specific triggers, scripts vs instructions only, reference paths (notes, README, existing command).
2. **Draft:** `.cursor/skills/<name>/SKILL.md`; add `REFERENCE.md` only if body would exceed 100 lines.
3. **Review with user:** covers use cases? missing pieces? too long? Then add one pointer row to `.cursor/rules/project-context.mdc`.

## Folder layout

```
skill-name/
├── SKILL.md        # required
├── REFERENCE.md    # optional; rare domains or long tables
└── EXAMPLES.md     # optional; sample prompts/outputs
```

Do not add `scripts/` under a skill; use `scripts/` at repo root or a `@command`.

## Description (discovery)

The YAML `description` is what Cursor uses to pick a skill. Max ~1024 chars. Third person.

- Sentence 1: what it does
- Sentence 2: `Use when ...` with concrete keywords

**Good:** `Runs GV2 model benchmarks with deployment threshold from notes. Use when testing a model, benchmark inference, image_slider_web, or @model-test.`

**Bad:** `Helps with models.`

No stale versions, hex, or thresholds in YAML; point to `notes/` or README.

## SKILL.md template

```markdown
---
name: skill-name
description: What it does. Use when [triggers].
---

# Skill name

Follow `.cursor/skills/read-notes/SKILL.md` for note facts (do not duplicate topic tables).

## Quick start
[Minimal path: one command or 3-step checklist]

## Workflow
[Numbered steps; link README/command for bash]

## Out of scope
[Point to other skills/commands]
```

## Body rules

- Under 100 lines in `SKILL.md`
- One SoT per topic (README, command, or note); no duplicate bash blocks
- Note paths: only via `read-notes`
- Command wins on execution; skill wins on judgment

## Review checklist

- [ ] Description has `Use when` triggers
- [ ] `SKILL.md` under 100 lines
- [ ] No time-sensitive pins in YAML
- [ ] Terminology matches `project-context.mdc`
- [ ] References one level deep (no chains of nested docs)
- [ ] Overlap with existing skill/command resolved or cross-linked
- [ ] Deprecated aliases deleted (no `make-documentation`-style stubs)

## Anti-patterns

- Long essays competing with rules
- Duplicating `project-context` tables inside skills
- Skill that only repeats a command verbatim
