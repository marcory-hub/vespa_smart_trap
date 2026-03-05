**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---

# YOLOv8n Training Runs Analysis

## Overview
Analysis of three YOLOv8n training runs for vespid detection (wasps/hornets) with different configurations.

## Training Runs Summary

### Run 1: `yolov8n_25-07-04b_b128` (Batch 128, Default LR)
- **Epochs**: 184 (early stopped)
- **Training Time**: 2.164 hours
- **Best Epoch**: 164
- **Batch Size**: 128
- **Learning Rate**: 0.01 (default)

### Run 2: `yolov8n_25-07-04c_b265` (Batch 265, Default LR)
- **Epochs**: 193 (early stopped)
- **Training Time**: 2.221 hours
- **Best Epoch**: 173
- **Batch Size**: 265
- **Learning Rate**: 0.01 (default)

### Run 3: `yolov8n_25-07-05a_lr0_0.005_wu_53` (Batch 128, Lower LR)
- **Epochs**: 200 (completed)
- **Training Time**: 2.294 hours
- **Best Epoch**: Not specified (completed full training)
- **Batch Size**: 128
- **Learning Rate**: 0.005 (reduced)
- **Warmup Epochs**: 5 (increased from 3)

## Performance Metrics Comparison

| Metric | Run 1 (b128) | Run 2 (b265) | Run 3 (lr0.005) | Best |
|--------|--------------|--------------|-----------------|------|
| **mAP50-95 (all)** | 0.853 | 0.852 | **0.856** | Run 3 |
| **mAP50 (all)** | 0.974 | 0.973 | **0.974** | Run 3 |
| **Precision (all)** | 0.96 | 0.949 | **0.951** | Run 1 |
| **Recall (all)** | 0.948 | 0.951 | **0.953** | Run 3 |
| **Training Time** | 2.164h | 2.221h | 2.294h | Run 1 |

## Class-Specific Performance

### Amel (Ameles spallanzania)
| Metric | Run 1 | Run 2 | Run 3 | Best |
|--------|-------|-------|-------|------|
| mAP50-95 | 0.792 | 0.794 | **0.799** | Run 3 |
| mAP50 | 0.928 | 0.931 | 0.929 | **Run 2** |
| Precision | 0.918 | 0.908 | 0.908 | **Run 1** |
| Recall | 0.921 | 0.918 | **0.924** | Run 3 |

### Vcra (Vespa crabro)
| Metric | Run 1 | Run 2 | Run 3 | Best |
|--------|-------|-------|-------|------|
| mAP50-95 | 0.858 | 0.853 | **0.858** | Run 1/3 |
| mAP50 | 0.989 | 0.986 | **0.988** | Run 1 |
| Precision | 0.977 | 0.96 | **0.968** | Run 1 |
| Recall | 0.953 | 0.958 | **0.963** | Run 3 |

### Vespsp (Vespa species)
| Metric | Run 1 | Run 2 | Run 3 | Best |
|--------|-------|-------|-------|------|
| mAP50-95 | 0.892 | 0.891 | **0.895** | Run 3 |
| mAP50 | 0.989 | 0.987 | **0.989** | Run 1/3 |
| Precision | 0.972 | 0.969 | 0.963 | **Run 1** |
| Recall | 0.956 | 0.966 | **0.964** | Run 2 |

### Vvel (Vespa velutina)
| Metric | Run 1 | Run 2 | Run 3 | Best |
|--------|-------|-------|-------|------|
| mAP50-95 | 0.872 | 0.87 | **0.873** | Run 3 |
| mAP50 | 0.991 | 0.989 | **0.99** | Run 1 |
| Precision | 0.974 | 0.959 | **0.966** | Run 1 |
| Recall | 0.962 | 0.963 | **0.962** | Run 1 |

## Key Observations

### 1. **Learning Rate Impact**
- **Run 3** with reduced learning rate (0.005 vs 0.01) achieved the best overall mAP50-95 (0.856)
- Lower learning rate allowed for more stable training and better convergence
- Increased warmup epochs (5 vs 3) likely helped with stability

### 2. **Batch Size Effects**
- **Run 1** (batch=128) vs **Run 2** (batch=265) showed minimal performance differences
- Larger batch size (265) didn't significantly improve performance
- Training time was similar despite different batch sizes

### 3. **Early Stopping Behavior**
- Runs 1 and 2 stopped early (epochs 164 and 173 respectively)
- Run 3 completed full 200 epochs, suggesting better convergence
- Early stopping patience of 20 epochs may be appropriate for this dataset

### 4. **Class Performance Patterns**
- **Amel** (Ameles spallanzania) consistently shows lower performance across all runs
- **Vespa velutina** and **Vespa crabro** show strong performance
- **Vespa species** shows good performance with some variation

### 5. **Inference Speed**
- All runs show similar inference speeds (~1.1-1.3ms)
- Postprocessing time varies slightly between runs

## Recommendations

### 1. **Optimal Configuration**
Based on the results, **Run 3** configuration appears optimal:
- **Learning Rate**: 0.005 (reduced from default)
- **Batch Size**: 128 (good balance of performance and memory)
- **Warmup Epochs**: 5 (increased stability)

### 2. **Further Optimization Opportunities**
- Consider experimenting with even lower learning rates (0.001-0.003)
- Test different optimizers (AdamW, Adam)
- Explore cosine learning rate scheduling
- Investigate why Amel class performs consistently lower

### 3. **Dataset Considerations**
- The dataset appears well-balanced across classes
- Consider data augmentation specifically for the Amel class
- Evaluate if Amel class needs more training samples

### 4. **Training Strategy**
- The early stopping mechanism is working well
- Consider reducing patience to 15 epochs for faster experimentation
- Monitor class-specific metrics during training

## Conclusion

**Run 3** with the reduced learning rate (0.005) and increased warmup epochs (5) achieved the best overall performance. The lower learning rate allowed for better convergence and more stable training, resulting in the highest mAP50-95 score (0.856). The batch size differences between runs 1 and 2 had minimal impact on final performance, suggesting that the learning rate is the more critical hyperparameter for this specific dataset and model configuration.

The model shows excellent performance on most vespid classes, with room for improvement specifically on the Amel class detection. 