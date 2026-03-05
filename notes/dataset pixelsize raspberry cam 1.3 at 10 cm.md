**One-line purpose:** 
**Short summary:**
**Agent:** 
**SoT:**
**Main Index:**


---
# Camera Specs (Raspberry Pi Cam v1.3)

Raspberry Pi Camera Module v1.3 uses:
- Sensor: OV5647
- Resolution: 2592×1944
- Horizontal FOV ≈ 53°
- Vertical FOV ≈ 41°


---

**Step 1 — Scene Width at 10 cm**

Formula: scene_width = 2 × distance × tan(FOV/2)
Distance = 10 cm  
FOV = 53°

So: tan(26.5°) ≈ 0.5
scene_width ≈ 2 × 10 × 0.5  
scene_width ≈ **10 cm** [to be verified]

**Step 2 — mm per Pixel at 224 Resolution**

If 224 pixels represent 10 cm (100 mm):

100 mm / 224 pixels ≈ **0.45 mm per pixel**

So: 1 pixel ≈ 0.45 mm

|Insect|Length|
|---|---|
|Honeybee|12–15 mm|
|Wasp|15–20 mm|
|European hornet|25–35 mm|
|Asian hornet|25–32 mm|
**Step 4 — Convert to Pixels**

pixels = length_mm / 0.45

### Honeybee (13 mm avg)

13 / 0.45 ≈ **29 pixels**

### Wasp (18 mm avg)

18 / 0.45 ≈ **40 pixels**

### European hornet (30 mm avg)

30 / 0.45 ≈ **67 pixels**

### Asian hornet (28 mm avg)

28 / 0.45 ≈ **62 pixels**
