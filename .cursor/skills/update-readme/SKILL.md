---
name: update-readme
description: Make or update README files with project voice and GitHub conventions. Use when the user asks to improve README, write readme copy, polish README.md, or @update-readme.
---

# Make README

**Role:** Style only. Never use this skill as a factual source. Facts come from codebase, `notes/` (explicit paths in `project-context.mdc`), or user prompt. Mark gaps `[to be verified]`.

## Audience

1. **Operator:** knows the stack; needs the command fast.
2. **Builder:** beekeeper, ecologist, or field researcher assembling the detector; needs context, then clear steps.

Serve both: terse procedures, welcoming intro. No dumbing down steps or burying commands.

## Edits

- Operate on the user-specified path only (e.g. `gv2_firmware/README.md`).
- Do not rewrite existing sections unless the user asks to polish or rewrite.
- Insert new content at the requested anchor. User-edit authority: `.cursor/rules/global-rules.mdc`.
- If path, anchor, or variable data (versions, URLs, hex) is missing, ask before writing.

## Intro contract (root and public READMEs)

Two lines after the title:

1. **What:** concrete noun, no hype.
2. **Who:** operator and/or builder (see above).

Optional on submodule READMEs. Never open with background, roadmap, or TOC.

## Section modes

Do not mix modes in one section.

| Mode | Use in | Rules |
| :--- | :--- | :--- |
| **Prose** | Intro, background | Inverted pyramid (main point first). No throat-clearing openers. |
| **Procedure** | Setup, Flash, CLI, Troubleshooting | Goal, prerequisites, numbered steps, expected output. No hooks or digressions. End with next step or success criteria. |

## Voice

Colleague notes, not blog or chatbot. Follow project-wide ban: no em dash, no emojis (`global-rules.mdc`).

**Banned:** "In this section we will…", "It's worth noting…", "Let's dive in", empty enthusiasm, tricolon stacks ("fast, reliable, and scalable"), filler under every heading, "Simply/Just follow these easy steps", generic sentences that fit any repo.

**Preferred:** direct and specific; concrete nouns ("921600 baud"); explain jargon once or drop it; active voice; bold UI and key commands for scanning only; simplify without distorting facts.

## Images

Relevant screenshots only; credit if not yours.

## GitHub conventions

- Title + intro contract at top.
- Badges only if they carry signal.
- TOC on long READMEs; anchors match GitHub IDs.
- Quick Start / Setup early.
- Fenced code blocks with language tag; copy-pasteable commands.
- Link to sections instead of repeating (`See [Setup](#setup)`).
- Update TOC when adding sections.
- Downloads: `blob/main` to `raw/main`.
- Placeholders for unknown values (`0xYOUR_ADDRESS`); flag to user.

## Pre-publish test

1. Can a tired operator find the command in 30 seconds?
2. Would you send any paragraph to a colleague unchanged?
3. Delete each section's first sentence: if nothing is lost, cut the opener.

## Destructive ops

Warn per `safety-guardrails.mdc` before flash, erase, or overwrite steps.
