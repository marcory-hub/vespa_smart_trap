# VST prompt template (paste into new chat, plan mode)

---

## Task

{imperative one-liner}

## Work type

- [ ] Code
- [ ] Hardware
- [ ] Environment
- [ ] Migration

## Mode

**Plan only. No file edits.**

## Background

- **Why:**
- **Success criteria:**
- **Non-goals:**
- **Research deliverable (Obsidian):** {summary or "none"}

## Hardware (optional)

- **Boards:** {GV2 / T-SIM / both}
- **New/changed:** {or none}
- **UART / GPIO / camera / SRAM:**
- **Bring-up / firmware:**

## Software (optional)

- **Path:** `scripts/{task}/` | `gv2_firmware/` | runbook only
- **Runtime / model / deps:**

## Colab / training (optional)

- **Notebook / dataset / artifacts / runtime:**

## Environment / migration / GCE (optional)

- **Source → target / scope / parity / rollback:**
- **GCE (from research deliverable):**

## Agent behavior

- **Persona:** per `agent-persona.mdc`
- **Rules:** see attachments (do not restate)

## Context attachments

**Required:**

```
@.cursor/rules/project-context.mdc
@.cursor/rules/safety-guardrails.mdc
{minimal topic set}
```

**If needed:**

```
@notes/_hardware_vst.md
@notes/_model_vst.md
@notes/_datasets_vst.md
@notes/_timeline_vst.md
@scripts/{script}.py
```

## Constraints

Follow attached `.cursor/rules/*.mdc`. Do not restate verbatim.

## Verification

- **Automated:**
- **Hardware / env / migration:**
- **Must not break:**

## Instruction to agent

Read attached SoT before proposing architecture. Step-by-step plan with risks and file touch list. No file edits.

---

## Open questions

- {[to be verified]}

## After this chat

Save plan to Obsidian → new chat → `@grill-me` on plan → use refined prompt/plan for implementation.
