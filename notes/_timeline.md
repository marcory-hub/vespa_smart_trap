**One-line purpose:** what is done and what move to todays tasklist
**Short summary:** 
**Agent:** 
**Main Index:** [[__vespa_smart_trap]]

---

[[_inbox]]


- [[temp next session]]
	- [[temp 388_test]]
	- [[temp gv2 conf ratio]]
- [[zz himax_yolo26 plan mode]]
2026-03-11
- [[himax gv2 sd jpeg image storage after detection]]

2026-03-10
- **ZIPPED HIMAX_YOLO26** (not on git, deployment failed)
- bijwerken yolo26 notes [[zz himax yolo26 failure summary]]
- **YOLO26 Critical Validation Tests Implementation COMPLETE**
  - Systematic diagnosis identified root causes: size constraints + tensor format mismatch
  - 67% model compatibility confirmed (2/3 models deployment-ready)  
  - Complete validation framework: 6 test scripts + comprehensive reporting
  - **Next**: Hardware validation on compatible models (high success probability)
  - **Strategic decision**: Focus on multi-output models, abandon oversized single-output
  - Validation framework: scripts/validation/ (tests 1-4 addressing summary.md lines 78-82)

2026-03-09
- 8+ hours debugging yolo26 with yolo8
	- no boxes
	- only vespa velutina alert
2026-03-08
- debugging yolo26 with yolo11
	- use nopost model
	- issue: more than 1 bounding box
	- issue: different classes for one object
- ExecuTorch not documented yet for gv2

2026-03-07
- install `live server` so we can open himax ai webtoolkit from cursor

2026-03-06
- [[himax forks yolo11 changes online]] limited commits
- [[himax fork exploring]]
- [[temp himax_test applied to himax_fork]]

2026-03-05
- cleanup of git history
- private repo vespa_smart_trap
- checked forks of HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2: some have yolo11 fixes
- [[clone HimaxWiseEyePlus-Seeed_Grove_Vision_AI_Module_V2]]
- [[himax fork and himax test comparison]]

2026-03-04
- new install of himax
- after changing back to the [old xmodem_send.py](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2/commit/db2d50889baf047ae0dd781393d82fa3b146d4db) it works after pressing the reset button
- [[yolo11_to_WE2]] output tensor comparison
- new install of himax [[himax installation on MacOS environment]]
- adjusted yolo11 pipeline [[yolo11_to_WE2]]

2026-03-03
- sensecraft.ai: imgsz224 has same screen size as 192 imgsz
- flash of yolo11n model does not work with himax. AI generated changes?

2026-03-02
- yolo26n allpx imgsz 192

2026-03-01
- NULL images added to datasets

2026-02-28
Beschikbaar: 145.46 rekeneenheden
Cursor: 17.1%
[[YOLOv11n exported to INT8 TFLite dropping to 0 mAP 2026-02-28]]


2026-02-27
[[himax from pt to flash]] fresh install of HimaxWiseEye
[[himax makefile]] adjustment
remember not to do step 7 from linux, but from macOS
make sure xmodem is installed in the .venv
netron.app showed a differnce between the old working model architecture and current one although output heads are the same (in different order)
https://github.com/HimaxWiseEyePlus/YOLOv8_on_WE2?tab=readme-ov-file#how-to-use-himax-config-file-to-generate-vela-model
[[plan2026-02-27]]
Cursor: 17.1%

2026-02-24
- old notes 2025 about himax and vela from git stored in [[himax_2025]] and [[himax_vela]]

2026-02-23
- After pruning almost 0 recognition

2026-02-22
Beschikbaar: 66.9 rekeneenheden
- yolo8n model imgsz 192 6.6GB best model, larger than yolo11n
- model naar int8

2026-02-21
Beschikbaar: 67.3 rekeneenheden
YOL11 pt to vela
- nieuwe runtime werkt niet
- 2025.07 runtime werkt ook niet
- ultralytics library gebruikt
- https://docs.ultralytics.com/modes/export/

2026-02-20
- Models trained on colab [yolo11n_training_2026-02-18](https://github.com/marcory-hub/yolo11n-on-grove-vision-ai-v2/blob/main/YOLO11n_training_2026_02_18.ipynb)
- Remove images with object annotation smaller than 16%, 21% dan 31% (in 19imgsz 30, 40 and 60px)
		16 34303/38847 kept
		21% 31581/38847 kept
		31% 25547/38847 kept
```
python3 merge_vespa_to_merged.py

python3 filter_by_bbox_size.py

python3 split_size_filtered_to_train_valid_test.py
```
- yolo11n batch=64 and lr=0.005 and e=500
- continue backup to ssd
	- [[dataset_vespa_2026-02v1_nopre_noaug]]
	- [[dataset_vespa_2026-02v2_pre_noaug]]
	- [[dataset_vespa_2026-02v3_nopre_aug]]
	- [[dataset_vespa_2026-02 versions]]
	(224 also needed? not yet, v1 training is in a accepable time)

2026-02-19
- yolo11n imgsz 192 --> drops a lot
- ![[yolo11n_v1_e300_b395_imgsz192.png]]
- yolo26n model with dataset_2026-02v1 --> not as good as yolo11n, slightly overtrained
- yolo11n model with dataset_2026-02v3 --> starts strong, but dips
- ![[vespa_v3_e300_b395_imgsz224.png]]

- yolo11n imgsz 192 to compare it with 224
- reorganize datasets because of diskspace and cp time

2026-02-18 
[[yolo11n_2026-02-18_vespa_2026-02v1_e300_b395_imgsz224]]
v1-4 datasets

2026-02-17 datasets
1. made coco datasets in swift yolo format (not tested, roboflow bug)
2. merge yolo26 dataset_vespa_2026-02v3 and v4
scripts/dataset_yolo_to_coco
```
cd scripts/dataset_yolo_to_coco

# For v3
python3 merge_original_class_folders.py --dataset-root ../../dataset_vespa_2026-02v3_train_val_test_yolo
python3 match_labels_to_split.py --dataset-root ../../dataset_vespa_2026-02v3_train_val_test_yolo

# For v4
python3 merge_original_class_folders.py --dataset-root ../../dataset_vespa_2026-02v4_train_val_test_yolo
python3 match_labels_to_split.py
 --dataset-root ../../dataset_vespa_2026-02v4_train_val_test_yolo
```
cursor 9,1%

2026-02-15
Beschikbaar: 111.52 rekeneenheden
Na installatie sessie onderbreken en opnieuw opstarten (in code block toevoegen)
batch size testen
workers testen


2026-02-14 test cvat [[dataset cvat yolo format]]
moved dataset.zip to gdrive
Beschikbaar: 112.02 rekeneenheden van 21:42 tot 22:10 nog niet voorbij install -> sessie onderbreken en opnieuw starten

2026-02-12 [[colab 2026-02-12]] test with dataset in roboflow
Beschikbaar: 116.62 rekeneenheden
Result: json corrupt
Roboflow request: storage space for 35000

2026-02-12 made [[dataset_vespa_2026-02_10000]] 4 versions to test colab