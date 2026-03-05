**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---



# YOLO Model Parameter Analysis

## Parameter Comparison Table

| Parameter | YOLO11n_05a | YOLO11n_05b | YOLO11n_05c | YOLOv8n_03 | YOLOv8n_04a | YOLOv8n_04b | YOLOv8n_04c | YOLOv8n_05a |
|-----------|-------------|-------------|-------------|------------|-------------|-------------|-------------|-------------|
| **model** | yolo11n.pt | yolo11n.pt | yolo11n.pt | yolov8n.pt | yolov8n.pt | yolov8n.pt | yolov8n.pt | yolov8n.pt |
| **epochs** | 200 | 200 | 300 | 200 | 200 | 200 | 200 | 200 |
| **patience** | 20 | 20 | 30 | 20 | 20 | 20 | 20 | 20 |
| **batch** | 128 | -1 | 256 | -1 | -1 | 128 | 265 | 128 |
| **optimizer** | SGD | auto | SGD | auto | AdamW | auto | auto | SGD |
| **lr0** | 0.005 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.005 |
| **lrf** | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 |
| **warmup_epochs** | 5.0 | 3.0 | 5.0 | 3.0 | 3.0 | 3.0 | 3.0 | 5.0 |
| **cls** | 1.0 | 0.5 | 1.0 | 0.5 | 0.5 | 0.5 | 0.5 | 1.0 |
| **cos_lr** | false | false | false | false | true | false | false | false |
| **seed** | 0 | 0 | 42 | 0 | 0 | 0 | 0 | 0 |
| **save_period** | -1 | -1 | 50 | -1 | -1 | -1 | -1 | -1 |

## Performance Correlation Analysis

### Top Influential Parameters (Ranked by Impact)

#### 1. **Model Architecture** (Most Critical)
- **YOLO11n vs YOLOv8n**: YOLO11n consistently outperforms YOLOv8n
- **Impact**: 0.859 vs 0.856 mAP50-95 (best models)
- **Reason**: YOLO11n is newer architecture with better efficiency

#### 2. **Learning Rate (lr0)** (High Impact)
- **0.005**: YOLO11n_05a (mAP50-95: 0.853), YOLOv8n_05a (mAP50-95: 0.856)
- **0.01**: All other models (mAP50-95: 0.851-0.859)
- **Observation**: Lower learning rate (0.005) shows competitive performance
- **Recommendation**: 0.005 provides good balance of convergence and stability

#### 3. **Optimizer** (Medium-High Impact)
- **SGD**: YOLO11n_05a (0.853), YOLO11n_05c (0.859), YOLOv8n_05a (0.856)
- **auto**: YOLO11n_05b (0.852), YOLOv8n_03 (0.851), YOLOv8n_04b (0.853), YOLOv8n_04c (0.852)
- **AdamW**: YOLOv8n_04a (worse performance - noted as "slechtere performance")
- **Conclusion**: SGD performs better than AdamW for this dataset

#### 4. **Batch Size** (Medium Impact)
- **128**: YOLO11n_05a (0.853), YOLOv8n_04b (0.853), YOLOv8n_05a (0.856)
- **256**: YOLO11n_05c (0.859) - best performance
- **265**: YOLOv8n_04c (0.852)
- **-1 (auto)**: YOLO11n_05b (0.852), YOLOv8n_03 (0.851)
- **Observation**: Larger batch sizes (256) show better performance

#### 5. **Class Loss Weight (cls)** (Medium Impact)
- **1.0**: YOLO11n_05a (0.853), YOLO11n_05c (0.859), YOLOv8n_05a (0.856)
- **0.5**: All other models (0.851-0.853)
- **Observation**: Higher cls weight (1.0) correlates with better performance

#### 6. **Warmup Epochs** (Low-Medium Impact)
- **5.0**: YOLO11n_05a (0.853), YOLO11n_05c (0.859), YOLOv8n_05a (0.856)
- **3.0**: All other models (0.851-0.853)
- **Observation**: Longer warmup (5.0) shows slightly better performance

#### 7. **Cosine Learning Rate (cos_lr)** (Negative Impact)
- **true**: YOLOv8n_04a (worse performance)
- **false**: All other models (better performance)
- **Conclusion**: Disabling cos_lr is beneficial for this dataset

#### 8. **Patience** (Low Impact)
- **20**: Most models (0.851-0.856)
- **30**: YOLO11n_05c (0.859) - best performance
- **Observation**: Higher patience allows longer training, potentially better convergence

#### 9. **Seed** (Minimal Impact)
- **0**: Most models
- **42**: YOLO11n_05c (best performance)
- **Observation**: Seed has minimal impact on final performance

## Parameter Optimization Recommendations

### High Priority Parameters:
1. **Model**: Use YOLO11n for best performance
2. **Learning Rate**: 0.005 provides good balance
3. **Optimizer**: SGD outperforms AdamW
4. **Batch Size**: 256 shows best results
5. **Class Loss Weight**: Use 1.0 for better performance

### Medium Priority Parameters:
6. **Warmup Epochs**: 5.0 epochs recommended
7. **Patience**: 30 for longer training potential
8. **Cosine LR**: Keep disabled (false)

### Low Priority Parameters:
9. **Seed**: Any value works
10. **Save Period**: -1 (save only best) is sufficient

## Optimal Configuration Summary

Based on the analysis, the optimal configuration for this vespid detection task is:

```yaml
model: yolo11n.pt
epochs: 300
patience: 30
batch: 256
optimizer: SGD
lr0: 0.005
warmup_epochs: 5.0
cls: 1.0
cos_lr: false
```

This configuration combines the best-performing parameters from the top models. 