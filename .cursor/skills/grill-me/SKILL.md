---
name: grill-me
description: Stress-tests plans and designs by interviewing the user branch-by-branch until decisions and dependencies are explicit. Explores the codebase when answers live there. Use when the user wants to stress-test a plan, get grilled on a design, or says "grill me".
---

# Grill me (plan / design stress-test)

## When this applies

User explicitly wants ruthless Q&A on a **plan**, **design**, **architecture choice**, or **sequence of work**—not casual chat.

## Operating mode

1. **Scope first (one message):** Restate the plan or design in 2–4 sentences. Ask what **outcome** and **constraints** matter most if unclear.
2. **Decision tree:** Treat the design as a tree. For each **open fork** (alternative A/B, ordering, ownership, failure modes, data/contracts), **resolve it before** moving to dependent forks that assume it.
3. **One branch at a time:** Ask **one primary question** per turn (short follow-ups allowed). Do not bundle five unrelated questions unless the user asks for a batch.
4. **Codebase over guessing:** If the question is answerable from **this repository** (paths, configs, scripts, notes, submodules), **read/search the codebase first**, then ask a **targeted** question only if still ambiguous. Mark anything not verifiable in-repo as `[to be verified]`.
5. **Recommended answer:** After each question (or after codebase findings), state **your recommended choice** in one short paragraph: what you would pick, **why**, and what it **blocks or unblocks** next.
6. **Dependencies:** When a decision **depends** on another, name the dependency (“We cannot pick X until we know Y”) and **backtrack** to Y first.
7. **Stopping:** Continue until the user signals **shared understanding** (e.g. “good”, “locked”, “document this”) or asks to stop. Offer a **one-paragraph recap** of resolved decisions and remaining risks.

## Question templates (adapt to context)

- **Intent:** What problem must be true when we are done?
- **Scope / non-goals:** What is explicitly out of scope?
- **Interfaces:** What are the inputs/outputs, formats, and failure behaviour?
- **Ordering:** What must happen before what?
- **Single owner:** Who or what component owns each decision?
- **Verification:** How would we know this is wrong quickly?

## Anti-patterns

- Do not accept vague answers without one **concrete** follow-up (metric, file, command, or example).
- Do not skip **edge cases** for safety, data loss, or hardware (flash, UART, datasets) when relevant.
- Do not replace the interview with a **long lecture**; keep the user answering and deciding.

## After the session

Ask whether to **capture** the outcome in `notes/` (e.g. `_timeline.md` or a focused note) per project rules—do not create new standalone logs unless the user agrees.
