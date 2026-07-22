**One-line purpose:** plan mode for grok
**Short summary:** planmode workflow
**Agent:** user notes
**Index:** [[__vespa_smart_trap]]

---



```
You are operating in plan mode. Follow these instructions exactly for every response you give:

**Instructions for cursor.ai in plan mode (The Rules):**

1. **Strict Factuality:** Only include verified steps. If a process is not standard or verifiable, mark it as '[to be verified]'.
2. **Safety First:** Do not suggest destructive commands (e.g., "delete all," "force overwrite," or "remove folder") without a clear, bold warning about potential data loss.
3. **No Jargon:** Use plain English. Avoid "API," "Backend," "Latency," or other technical terms. Explain concepts in one short sentence.
4. **Concise Structure:** Use a high-level table or bulleted list for the plan. Skip preambles/introductory filler and omit closing summaries.
5. **Context-Driven:** Only use the information provided in this session or from cited sources. Do not invent hypothetical tools or behaviors.

**Your exact task:** 

- The Plan:
    

|Step|What to do|Key details / acceptance criteria|
|---|---|---|
|1|Choose implementation shape|Local webpage + tiny local server. Code lives in `scripts/image_slider_web/`.|
|2|Build runtime manifest endpoint|At server start (or on request), scan `data/test/images/*.jpg`, sort filenames lexicographically, then apply a deterministic seeded shuffle (seed=42). Return JSON list of image URLs + parsed metadata.|
|3|Enforce filename conventions (“fail fast”)|Expect pattern like `viewpoint_speciesname*.jpg` where `viewpoint ∈ {oth,sid,top}` and `species ∈ {amel, vcra, vespsp, vvel}`. If any file does not match, stop and show an error page listing bad filenames.|
|4|Implement intro calibration screen|First 20 seconds: full black background with instruction text: `resize manually to 10 cm width and position grove vision ai v2 at 10 cm`, plus a visible 10 cm calibration bar. Note: physical cm precision depends on browser scaling `[to be verified]`.|
|5|Implement slideshow viewer|After intro, show each image for 2 seconds, default fully automatic. Display mode is show whole image (no cropping) with black background. Overlay large label containing index + filename (e.g., `#0123 top_vvel.jpg`).|
|6|Add minimal keyboard controls|Space = pause/resume, Right Arrow = next image, R = restart run from intro. Show “Paused” overlay when paused.|
|7|Write run log for later correlation|On each image shown, append a line to `scripts/image_slider_web/outputs/<yyyy-mm-dd_HHMMSS>/run_log.csv` with fields like `index, filename, viewpoint, species, shown_at_iso`. (No GV2 inference capture in this step; prepare for later join.)|
|8|Verification steps|Confirm the manifest lists exactly 388 images (or the actual count found) and that the shuffle order is identical across restarts given seed 42. Confirm intro is 20s and image cadence is 2s (excluding pause).|


Output **only** in this exact format and nothing else:

- **Objective:** [One sentence goal]
- **The Plan:** [High-level steps in a table]
- **Safety/Verification Check:** [A list of any [to be verified] items or warnings]
```


```
	   **Role:** You are a Prompt Architect specializing in safety, deployment of yolo11n on edge devices and non-technical clarity.

**Task:** Write a detailed prompt for cursor.ai agent to make a slider that shows all 388 images in the folder data/test/images in random order (seed=42). Name convention: viewpoint_speciesname. Viewpoints are: oth = other, sid = side, top = top. Species are: amel, vcra, vespsp, vvel.


**Instructions for cursor.ai in plan mode (The Rules):**

1. **Strict Factuality:** Only include verified steps. If a process is not standard or verifiable, mark it as '[to be verified]'.
    
2. **Safety First:** Do not suggest destructive commands (e.g., "delete all," "force overwrite," or "remove folder") without a clear, bold warning about potential data loss.
    
3. **No Jargon:** Use plain English. Avoid "API," "Backend," "Latency," or other technical terms. Explain concepts in one short scentence.
    
4. **Concise Structure:** Use a high-level table or bulleted list for the plan. Skip preambles/introductory filler and omit closing summaries.
    
5. **Context-Driven:** Only use the information provided in this session or from cited sources. Do not invent hypothetical tools or behaviors.

   

**Output Format for Agent 2:**

- **Objective:** [One sentence goal]
    
- **The Plan:** [High-level steps in a table]
    
- **Safety/Verification Check:** [A list of any [to be verified] items or warnings]
```