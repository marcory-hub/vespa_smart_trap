---
name: push-submodule
description: Safely add, commit, and push changes in a git submodule before committing and pushing the parent repo pointer. Use when updating `gv2_firmware` (submodule), when the user says "submodule", or when preparing GitHub pushes that include submodule changes.
---

# Push submodule (before parent repo)

## Goal
When `gv2_firmware/` is a git submodule, **push the submodule commit first**, then **commit and push the parent repo** which records the updated submodule SHA.

## Workflow (do in this order)

## Commit message rules
- The user must provide the commit message.
- Use the exact message the user provides.
- Do not add or change capitalization.
- Do not add or change characters.
- Do not include the word "cursor" in the commit message.

### 0) Inspect current state
- In the **parent repo**:
  - `git status`
  - `git diff`
- In the **submodule** (`gv2_firmware/`):
  - `git -C gv2_firmware status`
  - `git -C gv2_firmware diff`
  - `git -C gv2_firmware log -1 --oneline`

### 1) Commit inside the submodule first
- Ensure you are on the intended submodule branch:
  - `git -C gv2_firmware branch --show-current`
- Stage and commit changes in the submodule:
  - `git -C gv2_firmware add -A`
  - `git -C gv2_firmware commit -m "<message>"`
- Push the submodule commit:
  - `git -C gv2_firmware push -u origin HEAD`

**If submodule push is blocked** (no permissions / wrong remote / protected branch):
- Stop and report the error.
- Do **not** proceed to committing the parent pointer, because that would reference a submodule SHA that doesn’t exist on the remote.

### 2) Commit the updated submodule pointer in the parent repo
After the submodule commit is pushed, the parent repo will show `gv2_firmware` as modified (the SHA pointer changed).

- In the parent repo:
  - `git add gv2_firmware`
  - `git commit -m "<message referencing submodule update>"`

### 3) Push the parent repo commit
- `git push -u origin HEAD`

## Common pitfalls to avoid
- **Committing parent first**: creates a parent commit pointing at a submodule SHA that’s not on GitHub yet.
- **Forgetting to commit in submodule**: parent shows “modified submodule” but the submodule has no commit.
- **Detached HEAD in submodule**: check branch and create a branch if needed before committing/pushing.
- **Dirty submodule after parent commit**: always ensure the submodule is clean after pushing.

## Quick verification checklist (end state)
- `git -C gv2_firmware status` shows clean.
- `git status` in parent shows clean.
- `git submodule status` shows the new SHA.
- GitHub has the submodule commit (push succeeded) before the parent commit references it.

