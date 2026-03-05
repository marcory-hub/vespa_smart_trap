**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---



=====================================================
YOLO11 PyTorch vs TFLite (INT8) Detailed Comparison
=====================================================

PER-CLASS METRICS:
 Class  PT_mAP50  TFLite_mAP50  PT_mAP50-95  TFLite_mAP50-95  Delta_mAP50  Delta_mAP50-95
  amel    0.9742        0.9701       0.7919           0.7607      -0.0041         -0.0312
  vcra    0.9812        0.9807       0.8345           0.8003      -0.0005         -0.0342
vespsp    0.9736        0.9685       0.8130           0.7816      -0.0050         -0.0314
  vvel    0.9825        0.9731       0.7862           0.7517      -0.0094         -0.0345

OVERALL SUMMARY:
Metric          | PyTorch | TFLite  | Delta
----------------|---------|---------|--------
mAP50           | 0.9779  | 0.9731  | -0.0047
mAP50-95 (mean) | 0.8064  | 0.7736  | -0.0328

Validation Settings:
- Image Size: 224
- Confidence: 0.001
- Quantization: Full Integer (INT8)

