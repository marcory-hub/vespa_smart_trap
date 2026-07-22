**One-line purpose:** 
**Short summary:**
**Agent:** 
**SoT:**
**Main Index:**

---

## Colab and Swift YOLO (after datasets)

- Merge local dataset/work; get Colab run working to train Swift YOLO.
- Use Option B (train/valid folders on Drive) to avoid heavy unzip. After any crash: re-run with `--resume` from last checkpoint on Drive.

## Current problems / risks

- **Colab disconnects:** Colab sessions disconnect; need to solve (e.g. Option B: train/valid on Drive, resume from checkpoint;
- **Roboflow images:** Verify whether getting images from Roboflow and using extracted images causes problems; check notes for what we have done so far.
- **Colab data source:** Test whether training with dataset via Roboflow API vs dataset unzipped in Colab makes a difference (OOM, credits, stability); 
- **Summary:** OOM is mitigated by Option B (train/valid on Drive, no large unzip); unzip can trigger runtime kill; Roboflow API would stream per batch (see [[colab_crash_prevention]]).
- **Other:** Review notes for other known issues before starting a run.
- **Solve later:** Python `imp` module (removed in 3.12); legacy Colab notebooks that depended on it are deprecated. See [[swift_yolo_imp_module]]. Colab runtime is Python 3.11; current Swift-YOLO notebook does not use imp.