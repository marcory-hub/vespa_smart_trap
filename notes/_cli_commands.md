**One-line purpose:** CLI commands
**Short summary:** sync obsidian, git workflow
**Agent:** CLI commands for user
**Main Index:** [[__vespa_smart_trap]]
**Quick links:** [[github cli commands]] [[himax flash command firmware]]

---
**Sync from Obsidian to Cursor (1:1 mirror into `notes/`)**
```bash
rsync -av --delete "/Users/md/Library/Mobile Documents/iCloud~md~obsidian/Documents/notes/400 computer vision/vespa_smart_trap/" "/Users/md/Developer/vespa_smart_trap/notes/"
```

---
**Before git add ask agent:**
- Run a security audit for this project following @security-audit
- from the root
```sh
pip-audit
```

git status 

git commit -m ""
first push to the branch
-u: sets the upstream (original repo) so Git remembers “this branch tracks `origin/yolo11-vespa`”.
```sh
git push -u origin yolo11-vespa
```

---

**Source of truth for project notes:** Obsidian vault. User edits in Obsidian; sync to repo via these commands (see `project-context.mdc`).

Makes `notes/` an exact copy of the vault folder: same structure, and removes files in `notes/` that no longer exist in the vault.

**WARNING: Irreversible operation. Files in `notes/` that are not in the Obsidian folder will be deleted.**

---
**Sync from Cursor to Obsidian vault (update changed files, never remove)**

```bash
rsync -av --include='*/' --include='*.md' --exclude='*' "/Users/md/Developer/vespa_smart_trap/notes/" "/Users/md/Library/Mobile Documents/iCloud~md~obsidian/Documents/notes/400 computer vision/vespa_smart_trap/"
```
Copies only `.md` files and directory structure from `notes/` into the Obsidian vault.  
Updates changed files and adds new ones, but **never removes** any existing files in the Obsidian vault (no `--delete`).

---



---

- [[zip command on mac zonder metadata en DS_Store]]
- [[himax flash command firmware]] to flash new model 