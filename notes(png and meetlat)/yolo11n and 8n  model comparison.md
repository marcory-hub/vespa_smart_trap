**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---

# YOLO Model Training Results Comparison

## Model Performance Summary

| Model | Epochs | Training Time | Batch Size | Optimizer | Learning Rate | mAP50 | mAP50-95 | Precision | Recall | Best Epoch |
|-------|--------|---------------|------------|-----------|---------------|-------|----------|-----------|--------|------------|
| **YOLO11n_05a** | 159 | 1.902h | 128 | SGD | 0.005 | 0.974 | 0.853 | 0.949 | 0.956 | 139 |
| **YOLO11n_05b** | 200 | 2.359h | -1 (auto) | auto | 0.01 | 0.973 | 0.852 | 0.955 | 0.946 | 200 |
| **YOLO11n_05c** | 266 | 3.067h | -1 (auto) | auto | 0.01 | 0.975 | 0.859 | 0.954 | 0.946 | 266 |
| **YOLOv8n_03** | 177 | 2.013h | -1 (auto) | auto | 0.01 | 0.973 | 0.851 | 0.957 | 0.946 | 157 |
| **YOLOv8n_04a** | 164 | - | -1 (auto) | AdamW | 0.01 | - | - | - | - | 164 |
| **YOLOv8n_04b** | 184 | 2.164h | 128 | auto | 0.01 | 0.974 | 0.853 | 0.960 | 0.948 | 164 |
| **YOLOv8n_04c** | 193 | 2.221h | 265 | auto | 0.01 | 0.973 | 0.852 | 0.949 | 0.951 | 173 |
| **YOLOv8n_05a** | 200 | 2.294h | 128 | SGD | 0.005 | 0.974 | 0.856 | 0.951 | 0.953 | 200 |

## Per-Class Performance (Best Models)

### YOLO11n_05c (Best Overall mAP50-95: 0.859)
| Class | Precision | Recall | mAP50 | mAP50-95 |
|-------|-----------|--------|-------|----------|
| amel | 0.923 | 0.912 | 0.938 | 0.812 |
| vcra | 0.958 | 0.953 | 0.988 | 0.858 |
| vespsp | 0.970 | 0.959 | 0.988 | 0.890 |
| vvel | 0.966 | 0.959 | 0.987 | 0.875 |

### YOLOv8n_05a (Best YOLOv8n mAP50-95: 0.856)
| Class | Precision | Recall | mAP50 | mAP50-95 |
|-------|-----------|--------|-------|----------|
| amel | 0.908 | 0.924 | 0.929 | 0.799 |
| vcra | 0.968 | 0.963 | 0.988 | 0.858 |
| vespsp | 0.963 | 0.964 | 0.989 | 0.895 |
| vvel | 0.966 | 0.962 | 0.990 | 0.873 |

## Key Observations

1. **YOLO11n vs YOLOv8n**: YOLO11n shows slightly better performance with the best mAP50-95 of 0.859
2. **Batch Size Impact**: Fixed batch size (128) generally performs well, auto batch size (-1) shows good results too
3. **Learning Rate**: Lower learning rate (0.005) with SGD optimizer shows competitive performance
4. **Training Duration**: YOLO11n models train faster than YOLOv8n models
5. **Class Performance**: All classes achieve high mAP50 (>0.92), with vespsp and vvel performing best

## Model Architecture Comparison

| Model | Parameters | GFLOPs | Model Size |
|-------|------------|--------|------------|
| YOLO11n | 2,582,932 | 6.3 | 5.5MB |
| YOLOv8n | 3,006,428 | 8.1 | 6.2-6.3MB |

## Recommendations

1. **Best Overall**: YOLO11n_05c with mAP50-95 of 0.859
2. **Best YOLOv8n**: YOLOv8n_05a with mAP50-95 of 0.856
3. **Fastest Training**: YOLO11n_05a (1.902h for 159 epochs)
4. **Most Efficient**: YOLO11n models (fewer parameters, faster inference) 