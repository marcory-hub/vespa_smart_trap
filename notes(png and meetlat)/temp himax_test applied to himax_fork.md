# Prompt: Apply himax_test changes to himax_fork step by step (YOLO11 224 no_post)

## Context
- **himax_fork:** My fork of Seeed_Grove_Vision_AI_Module_V2 at `vespa_smart_trap/himax_fork/`. This is the repo I push to GitHub (origin). I build and flash from here.
- **himax_test:** A separate clone/reference at `vespa_smart_trap/himax_test/Seeed_Grove_Vision_AI_Module_V2/`. Detection works correctly here (correct bounding boxes). It is my reference; I do not push it to GitHub.
- **Goal:** Apply only the minimal changes from himax_test into himax_fork so that YOLO11 224 no_post detection in himax_fork also shows correct box positions. No new logic—only copy or adapt what exists in himax_test.
- **Constraint:** One logical change at a time. After each step I will build, flash, and test (Himax AI webtoolkit) before proceeding. Do not suggest committing until I confirm it works.

## Source of truth for “what to apply”
- Comparison note: `notes/himax fork and himax test comparison.md`.
- Reproduction guide: `notes/yolo11_to_WE2.md`.
- Code reference: `himax_test/Seeed_Grove_Vision_AI_Module_V2/EPII_CM55M_APP_S/app/scenario_app/tflm_yolo11_od/cvapp_yolo11n_ob.cpp` and same path under `himax_fork/`.

## Task for the agent

1. **Identify the minimal set of changes** in `cvapp_yolo11n_ob.cpp` that are required for YOLO11 224 no_post to work (correct boxes) in himax_fork, using himax_test as reference. Ignore changes that are only for YOLO26, unified binary, or cosmetic (e.g. class names can be done later). Focus on:
   - Init: `dim_total_size = 0` at start of `cv_yolo11n_ob_init` (if not already there).
   - 3-output post-processing: shape-based output order (28→14→7) and the block that sets `out_dim_total` and `out_dim_size` (must be present and correct so the loop does not use uninitialized values).
   - Any other difference in the same file that directly affects the 3-output no_post path (decode, scaling, or loop indices). Do not add debug prints or NCHW handling unless the model actually requires it.

2. **Produce a step-by-step plan** with exactly:
   - Step number and short title.
   - File path (always under `himax_fork/`).
   - What to add, replace, or delete (with enough context: e.g. “after line X”, “replace the block that does Y with the following”).
   - Exact code block(s) to insert or the exact old_string / new_string for a search-replace, so I can apply it myself or the agent can apply it.
   - One sentence “How to verify”: e.g. “Build, flash, run webtoolkit; boxes should align with insects.”

3. **Order the steps** so that:
   - The first step is the smallest, self-contained change (e.g. `dim_total_size = 0` or the out_dim_total/out_dim_size block).
   - Each step leaves the project buildable and testable.
   - No step depends on a later step.

4. **Do not** in this prompt:
   - Suggest `git add .` or committing before I have tested.
   - Suggest changes to other repos (himax_test) or to files outside himax_fork.
   - Add features not present in himax_test (e.g. new debug logs) unless they are necessary to verify the fix.

5. **Output format:** For each step, output:
   - **Step N: [Title]**
   - **File:** `himax_fork/...`
   - **Action:** [Add | Replace | Delete]
   - **Context:** [where in the file]
   - **Code / diff:** [exact block or old_string → new_string]
   - **Verify:** [one sentence]

After all steps are listed, add a short “Testing and commit” reminder: build → flash → test in webtoolkit → only then `git add <file>`, `git commit`, `git push origin yolo11-vespa`.