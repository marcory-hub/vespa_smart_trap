**One-line purpose:** CLI commands
**Short summary:** sync obsidian, git workflow
**Agent:** CLI commands for user
**Main Index:** [[__vespa_smart_trap]]

---
**daily cli**
	**start**
- [[#Sync from Obsidian to Cursor M2]]
- [[#Sync from Obsidian to Cursor M5]]
	**end**
- [[github_cli_commands_vst]] 
	- submodule commit + push first
	- then parent commit + push with `git add gv2_firmware`.

- ---

**GV2**
- [[himax build firmware image]]
- [[himax flash command firmware]]

---

**ESP32**
- [[#ESP32]]
	- [[#serial monitor ESP32]]
	- [[#flash ESP32]]

---

**dataset**
- [[#zip only jpg, txt, yaml]]
- [[#copy files from image labels format to train, valid, test]]
---

**python scripts**
- [[#run test yolo models with slider]] (run_all_models.py)
- [[#test swift-yolo]]
- [[#copy files from image labels format to train, valid, test]]
- [[#local detector from root]]
- [[#local detector from repo]]
- 
---
# Sync from Obsidian to Cursor M2
## 1:1 mirror into `notes/`
```bash
rsync -av --delete "/Users/md/Library/Mobile Documents/iCloud~md~obsidian/Documents/notes/400 computer vision/vespa_smart_trap/" "/Users/md/Developer/vespa_smart_trap/notes/"
```
[[github_cli_commands_vst]] submodule commit + push first, then parent commit + push with `git add gv2_firmware`

## sync without remove
```bash
rsync -av --include='*/' --include='*.md' --exclude='*' "/Users/md/Developer/vespa_smart_trap/notes/" "/Users/md/Library/Mobile Documents/iCloud~md~obsidian/Documents/notes/400 computer vision/vespa_smart_trap/"
```
Updates changed files and adds new ones, but **never removes** any existing files in the Obsidian vault (no `--delete`).
---
# Sync from Obsidian to Cursor M5
(1:1 mirror into `notes/`)
```bash
rsync -av --delete "/Users/md5/Library/Mobile Documents/iCloud~md~obsidian/Documents/notes/400 computer vision/vespa_smart_trap/" "/Users/md5/Developer/vespa_smart_trap/notes/"
```
[[github_cli_commands_vst]] submodule commit + push first, then parent commit + push with `git add gv2_firmware`

---
# ESP32
## serial monitor ESP32
```sh
pio device monitor --filter printable -b 115200
```

## flash ESP32
```sh
pio run -t upload
```

---
# git
## security audit
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
# dataset
## zip only jpg, txt, yaml
```sh
rm -f dataset.zip

find . -type f \( -name '*.jpg' -o -name '*.txt' -o -name '*.yaml' \) -print | zip -rX dataset.zip -@
```

---
# python scripts
## run test yolo models with slider
first check if port is available again
```
lsof -iTCP -sTCP:LISTEN -P -n
kill <PID>
or
kill -9 <PID>
```

```python
source .venv/bin/activate
python3 scripts/experiment_set_match/run_all_models.py \
  --model-name "yolo11n_vespa_2026-02v1_30px" \
  --serial-port /dev/tty.usbmodem58FA1047631 \
  --slider-port 8018 \
  --expected-count 388 \
  --locked-benchmark \
  --sampled-avg-threshold 0.30 \
  --sampled-F1-threshold 0.34 \
  --sampling-start-offset-s 2.5 \
  --sampling-event-stride 5 \
  --sampling-event-count 3 
```
## test swift-yolo
```
source .venv/bin/activate
python3 scripts/gv2_swift_yolo_test/run_swift_yolo_experiment.py \
  --model-name swift_yolo_vespa_2026_full \
  --serial-port /dev/tty.usbmodem58FA1047631 \
  --expected-count 388 \
  --locked-benchmark \
  --invoke-result-only 0
```

## copy files from image labels format to train, valid, test
```sh
source .venv/bin/activate
python3 scripts/dataset_top_copy/copy_images_labels_to_train_valid_test.py --dry-run
python3 scripts/dataset_top_copy/copy_images_labels_to_train_valid_test.py
```
## local detector from root
```
cd Developer/vespa_smart_trap/
source .venv/bin/activate
python3 /Users/md/Developer/vespa_smart_trap/experiments/gv2_home/detect_chime_save.py --port /dev/cu.usbmodem58FA1047631 --baudrate 921600
```
## local detector from repo
```
python3 /experiments/gv2_home/detect_chime_save.py --port /dev/cu.usbmodem58FA1047631 --baudrate 921600
```

# make dataset with only vvel vcra null
and updates yaml files
```sh
source .venv/bin/activate

# Preview (default)
python3 scripts/dataset_filter_classes/filter_vvel_vcra_null.py

# Execute — WARNING: irreversible; deletes image/label pairs
python3 scripts/dataset_filter_classes/filter_vvel_vcra_null.py --apply
```
