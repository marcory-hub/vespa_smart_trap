**One-line purpose:** git commands used
**Short summary:** branch workflow and safety
**SoT:** never suggest items under #avoid
**Agent:** ask user to update after user aske a question about github, explain the how, why and risks
**Main Index:**[[_cli_vst]]

---

# quick copy-paste with submodule gv2_firmware
When start working
```
cd ~/Developer/vespa_smart_trap
git pull origin main
git submodule update --init --recursive
```
if gv2_firmware end up in detached head but will change firmware
```
cd ~/Developer/vespa_smart_trap/gv2_firmware
git checkout yolo11-vespa
git pull origin yolo11-vespa
```

- Order matters: 
- **submodule commit + push first**, 
- then parent commit + push with `git add gv2_firmware`

end work after changes in **gv2_firmware**
- submodule commit + push first
- then parent commit + push with `git add gv2_firmware`.
```
cd ~/Developer/vespa_smart_trap/gv2_firmware
git status
git checkout yolo11-vespa
git add -u
# or: git add <specific files>
git commit -m "Describe firmware change"
git push origin yolo11-vespa

cd ~/Developer/vespa_smart_trap
git status
git add gv2_firmware
git commit -m "Bump gv2_firmware submodule"
git push origin main
```


end work after changes in parent **vespa_smart_trap**
```
cd ~/Developer/vespa_smart_trap
git status
git add -u
# or: git add <specific files>
git commit -m "Describe change"
git push origin main
```



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

# Assume unchanged
to avoid accidentally staging it
```
cd /Users/md/Developer/vespa_smart_trap/himax_fork
git update-index --assume-unchanged EPII_CM55M_APP_S/makefile
```
and to undo it
```
git update-index --no-assume-unchanged EPII_CM55M_APP_S/makefile
```

