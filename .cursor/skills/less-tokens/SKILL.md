---
name: less-tokens
description: Reduces Cursor session token use via terse replies and efficient tool use. Use when user says less tokens, token efficiency, be brief, stop rambling, or @less-tokens.
---

# Less tokens (Cursor)

## Persistence

Active for the rest of the chat after trigger. Off when user says **normal mode** or **stop less tokens**.

## Chat output

- Answer the question first; no restating the prompt
- Lookup: cite path or `(file:line)` plus one short paragraph; no lecture
- Operator / `@command` / apply to file: steps and commands only; skip Why unless blocked
- No closing summaries, engagement bait, or "let me know if..."
- No mermaid or ascii unless user asks or logic is ambiguous
- Do not paste large note or file blocks; point to path
- Do not repeat content already in always-on rules or loaded skills

Teaching posture: only when `@teach-me` is active; otherwise skip theory unless blocked.

## Tool use (main Cursor savings)

| Do | Why |
| :--- | :--- |
| `Read` with `limit` / `offset` | Whole files inflate context |
| `Grep` with `head_limit` | Ripgrep output can be huge |
| Parallel independent tool calls | Fewer turns = less chat overhead |
| One targeted search before ask | Avoid broad `Task` / explore subagents for needle queries |
| Reuse prior read in same turn | Do not re-read the same file |
| `scripts/` + `script-index` before new util | Less generated code in diff |

Skip: reading all skills; loading skills not relevant to the request; dumping terminal logs when a 5-line summary plus path suffices.

## Skills and commands

- Read **only** the skill or `@command` the user invoked (plus `read-notes` when note facts needed)
- Command invoked: run it; do not narrate the whole command file

## Exceptions (full length required)

Pause less-tokens for:

- **WARNING** blocks (`safety-guardrails.mdc`, flash, erase, `rm`)
- Security audit failures or secret exposure
- User asks to clarify, `@teach-me`, or `@grill-me`
- Multi-step procedure where shortening risks wrong order

Resume terse mode after the exception block.

## Not in scope

- Shorter rules or skills on disk (that is a separate edit)
- Abbreviated identifiers in code or docs
- Dropping citations for factual claims
