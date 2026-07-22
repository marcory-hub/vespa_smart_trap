**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---

**One-line purpose:** debugging of int8.tflite dropping to 0mAP
**Short summary:** fixed with correct folderstructure of the dataset
**Agent:** caused by a wrong folder structure
**Main Index:** [[himax from pt to flash]]

---

Old ultralytics has a different folder structure
- images
    - train
    - val
- labels
    - train
    - val

New ultralytics needs
- train
	- images
	- labels
- valid
	- images
	- labels