**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---

# Plan: GV2 confidence ratio and “not certain” (vvel safety)

  

**Goal:** On the GV2 (Grove Vision AI V2), for each detection (1) expose the **ratio** of second-highest to highest class confidence so we can see uncertainty, and (2) when the predicted class is **vvel** (exotic invasive), **flag or suppress** the detection if that ratio is above a threshold (“not certain”), so we do not act on vvel unless we are confident—avoid harming other species (e.g. vcra in difficult conditions).

  

**Class indices:** 0 = amel, 1 = vcra, 2 = vespsp, 3 = vvel.

  

---

  

## 1. Requirements (from user)

  
- **Scope:** GV2 firmware only (no “dark” condition in this plan).

- **Uncertainty:** Use **ratio** of second-highest to highest confidence (applies to **all** classes).

- **Safety:** Do not treat a detection as “vvel” when we are not certain (e.g. when another class, often vcra, is close in confidence). Only act on vvel when confident.

- **Output:** Expose **ratio** (highest vs second) per detection so we get a feeling for certainty; currently we only see the highest.

- **388 test / dataset work:** Deferred until after the 388-image test is done; no dataset or retraining in this plan.

  

---

  

## 2. Ratio definition

  

- For each detection we have 4 class scores (after sigmoid or softmax): one per class (0..3).

- **Highest:** `score_first` = max(scores), **first_class** = argmax.

- **Second-highest:** `score_second` = max over the other three.

- **Ratio:** `ratio = score_second / score_first` (in (0, 1]).

- High ratio (e.g. > 0.8) ⇒ “not certain” (second class is within 80% of first).

- Low ratio ⇒ confident (first class clearly dominates).

  

User suggested ~20% margin; expressed as ratio that means “second within 80% of first” ⇒ **ratio threshold ≈ 0.8** (tunable; no test results yet, may be too strict or too loose).

  

---

  

## 3. Where to compute ratio (firmware)

  

- **Place:** Post-processing in `cvapp_yolo11n_ob.cpp`, where we already have per-cell class scores and we pick the max class and score before NMS.

- **Today:** We only keep `maxScore` and `maxClassIndex` per cell, then push one box per cell (after threshold) with that class and confidence.

- **Change:** When we have the full set of class scores for that cell (e.g. 4 values for YOLO11, 4 for YOLO26), compute:

- `score_first` = max, `first_class` = argmax.

- `score_second` = max of the remaining three.

- `ratio = score_second / score_first` (guard against division by zero).

- **Use:** (a) Pass ratio (or second score) through to the result struct so it can be sent in the INVOKE output. (b) If `first_class == 3` (vvel) and `ratio >= threshold` (e.g. 0.8), mark the detection as “uncertain” or do not report it as vvel (see §5).

  

---

  

## 4. Output: expose ratio (highest vs second)

  

- **Current:** INVOKE `boxes` entries are e.g. `[x, y, w, h, score, target]` (target = class index). We only see the winning class and its confidence.

- **Desired:** Add one of:

- **Option A:** Extra field per box, e.g. `ratio` or `confidence_ratio` (second/first), so the UI or backend can show “vvel 85%, next 72% (ratio 0.85)”.

- **Option B:** Extra field `score_second` (and optionally `target_second`) so ratio can be computed off-device, or display “top: vvel 85%, second: vcra 72%”.

- **Implementation:** Extend the structure that holds one detection (e.g. `el_box_t` or the YOLO result struct) with `ratio` or `score_second` (and optionally `class_second`). In `send_result.cpp`, when building the INVOKE JSON for YOLO, add this field to each box entry (e.g. `[x, y, w, h, score, target, ratio]` or a named field). Ensure the web toolkit (or whatever consumes the JSON) can display it.

  

---

  

## 5. Safety: “not certain” when predicted class is vvel

  

- **Rule:** If the predicted class is **vvel (3)** and **ratio >= threshold** (e.g. 0.8), the detection is treated as **uncertain**.

- **Behaviour options (choose one or combine):**

- **Flag only:** Still send the box, but add a flag (e.g. `uncertain: true` or `vvel_uncertain: true`) so the trap logic or backend does **not** trigger a kill; only “confident vvel” triggers.

- **Suppress:** Do not add this box to the result list when predicted is vvel and ratio >= threshold (so it never triggers the trap).

- **Recommendation:** Flag (rather than drop) so we still see “vvel but uncertain” in the UI and can tune the threshold; trap logic must check the flag and only act when vvel and not uncertain.

- **Threshold:** Make it configurable (e.g. `UNCERTAIN_RATIO_THRESHOLD = 0.8f` in a header or config) so it can be adjusted after 388-test or real trap data (user said 20% might be too much; 0.8 is a starting value).

  

---

  

## 6. Apply to all classes (for “not certain” flag)

  

- Ratio is computed for **every** detection (all four classes).

- **Uncertainty flag** can be set for any detection where `ratio >= threshold` (so we see “not certain” for amel, vcra, vespsp, vvel when a second class is close).

- **Safety rule** is special only for **vvel**: when predicted is vvel and uncertain, do not act (trap). For other classes, the flag is informational only (or used later for analytics).

  

---

  

## 7. Implementation order

  

1. **Post-processing (cvapp_yolo11n_ob.cpp):**

For each cell that passes the score threshold, compute `score_first`, `first_class`, `score_second`, and `ratio`. Store ratio (and optionally `score_second` / `class_second`) in the box/result structure. Ensure this is done in both YOLO11 and YOLO26 paths (and single-output path if used).

  

2. **Result structure and send_result:**

Extend the struct used for each detection (e.g. `el_box_t` or equivalent) with `ratio` (and optionally second score/class). In `send_result.cpp`, add ratio (and optional second) to the INVOKE JSON for each box so the UI can show “highest vs second” and ratio.

  

3. **Uncertainty flag:**

In firmware, set a flag (e.g. `uncertain`) when `ratio >= UNCERTAIN_RATIO_THRESHOLD`. If predicted class is vvel and uncertain, set e.g. `vvel_uncertain` or ensure trap logic treats it as “do not act”. Include the flag(s) in the JSON if the trap or backend needs them.

  

4. **Config:**

Define `UNCERTAIN_RATIO_THRESHOLD` (e.g. 0.8f) in a single place; document that it may need tuning after 388-test or real camera data.

  

5. **UI/consumer:**

Update the consumer of INVOKE (e.g. Himax web toolkit or your trap controller) to display ratio (and optionally second class/score) and, if present, “uncertain” so you can get a feeling for it. Trap logic: only trigger on vvel when not uncertain.

  

---

  

## 8. Out of scope (for this plan)

  

- “Dark” condition or any brightness-based logic.

- Dataset collection or retraining (to be done later with real trap camera images).

- 388 slideshow or offline eval (handled in `PLAN_SLIDESHOW_388_TEST_CLASS_EVAL.md`; analysis of vcra/vvel confusion can follow after that test).

  

---

  

## 9. Summary

  

| Item | Choice |

|------|--------|

| Ratio | `score_second / score_first` per detection |

| Threshold | Configurable, e.g. 0.8 (second within 80% of first) |

| All classes | Yes; ratio and “uncertain” flag for any class |

| vvel safety | When predicted = vvel and ratio ≥ threshold ⇒ do not act (flag or suppress) |

| Output | Add ratio (and optional second score) to INVOKE so we see highest vs second |

| Class order | 0=amel, 1=vcra, 2=vespsp, 3=vvel |