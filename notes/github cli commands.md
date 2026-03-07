**One-line purpose:** git commands used
**Short summary:** branch workflow and safety
**SoT:** never suggest items under #avoid
**Agent:** ask user to update after user aske a question about github, explain the how, why and risks
**Main Index:**[[_cli_commands]]

---
# Remotes
- origin: my fork
- upstream: HimaxWiseEyePlus
---
# Branch workflow
- main: stays in sync with upstream
- yolo11-vespa: **work branch** to get yolo11n 224imgsz nopost working
---
# Daily commands
git status
git branch -a
git add file

**what would be committed**
git diff --cached

**first time push to a new branch**
git push -u origin demo

---
# Sync with upstream
to get latest from original repo
```sh
cd /path/to/himax_fork
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
# Then bring updates into your work branch:
git checkout yolo11-vespa
git merge main
# fix conflicts if any, then:
git push origin yolo11-vespa
```

---
# Avoid
|Command|Why it’s not “professional” default|
|---|---|
|`git add .`|Stages everything; easy to commit wrong files. Prefer `git add <file>`.|
|`git reset --hard HEAD~1`|Deletes last commit and uncommitted changes; can’t recover. Only use when you’re sure. Prefer `git revert HEAD` to undo a commit safely.|
|`git push --force`|Overwrites remote history. Use only when you know why (e.g. after reset and you’re the only one using the branch).|
