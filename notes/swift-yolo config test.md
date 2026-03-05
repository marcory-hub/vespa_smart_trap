**One-line purpose:** 2026-02-15 test to test influence of batch, workers and GPU in colab
**Short summary:** 
A100: high ram, batch=2048, workers=12, lr=0.02
T4: high ram, batch=512 (try 768), workers=8, lr=0.02 (0.01 for fine-tuning)
**Agent:** test training runs of 5 epoch (to save compute) in colab with T4 and A100 to train a swift yolo model



---

T4 no high ram
Batch=64
Workers=8

Systeem-RAM: 8.3 / 12.7 GB
bij epoch 5: 9.9 / 12.7 GB
bij epoch 6: 10
GPU RAM: 1.0 / 15.0 GB
result na epoch 5
```
 Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = 0.092
 Average Precision  (AP) @[ IoU=0.50      | area=   all | maxDets=100 ] = 0.210
 Average Precision  (AP) @[ IoU=0.75      | area=   all | maxDets=100 ] = 0.063
 Average Precision  (AP) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = 0.002
 Average Precision  (AP) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = 0.048
 Average Precision  (AP) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = 0.115
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=  1 ] = 0.331
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets= 10 ] = 0.441
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = 0.493
 Average Recall     (AR) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = 0.035
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = 0.397
 Average Recall     (AR) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = 0.553
```

doel meer GPU gebruik en ram verlagen
T4 no high ram
workers=2
batch=512
Systeem-RAM: 7.7 / 12.7 GB
GPU RAM: 6.6 / 15.0 GB
bij epoch 5
```
 Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = 0.013
 Average Precision  (AP) @[ IoU=0.50      | area=   all | maxDets=100 ] = 0.048
 Average Precision  (AP) @[ IoU=0.75      | area=   all | maxDets=100 ] = 0.002
 Average Precision  (AP) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = 0.000
 Average Precision  (AP) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = 0.004
 Average Precision  (AP) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = 0.018
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=  1 ] = 0.133
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets= 10 ] = 0.201
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = 0.280
 Average Recall     (AR) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = 0.000
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = 0.091
 Average Recall     (AR) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = 0.365
```

hoog ram
T4
batch=1028
workers=4
Systeem-RAM: 9.5 / 51.0 GB
GPU RAM: 12.6 / 15.0 GB
bij epoch 2 gestopt om systeem ram beter te gebruiken door verhogen van aantal workers

---

hoog ram
T4
batch=1028
workers=32
loopt vast

---

hoog ram
T4
batch=512
workers=32
loopt vast
Systeem-RAM: 23.0 / 51.0 GB
GPU RAM: 7 / 15.0 GB
1:22 per epoch
```
Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = 0.021
 Average Precision  (AP) @[ IoU=0.50      | area=   all | maxDets=100 ] = 0.068
 Average Precision  (AP) @[ IoU=0.75      | area=   all | maxDets=100 ] = 0.005
 Average Precision  (AP) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = 0.000
 Average Precision  (AP) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = 0.008
 Average Precision  (AP) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = 0.028
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=  1 ] = 0.144
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets= 10 ] = 0.268
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = 0.351
 Average Recall     (AR) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = 0.000
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = 0.130
 Average Recall     (AR) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = 0.453

```

---

A100
high ram
batch=1024
workers=32
Systeem-RAM: 23.0 / 167.1 GB
GPU RAM: 13.4 / 80.0 GB
crashed, mogelijk teveel CPU. ruis door 32 workers?

---

A100
high ram
batch=4096
workers=16
crashed

---


A100
high ram
batch=1024
workers=8
Systeem-RAM: 12.8 / 167.1 GB
GPU RAM: 13.3 / 80.0 GB
1:17-1:04 per epoch
```

```
---

A100
high ram
batch=2048
workers=12
lr=0.04
Systeem-RAM: 19.5 / 167.1 GB
GPU RAM: 26.4 / 80.0 GB
0:32 per epoch

---
A100
high ram
batch=2048
workers=12
lr=0.02 (omdat er geen warm-up is)
Systeem-RAM: 19.5 / 167.1 GB
GPU RAM: 26.4 / 80.0 GB
0:32 per epoch