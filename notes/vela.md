**One-line purpose:** background and compilation to vela
**Short summary:** colab notebook, vela summary
**SoT:** vela documentation links
**Agent:** vela information for installation
**Main index:** [[__vespa_smart_trap]]

---


**install vela compiler** 
```python
# Install the Arm Ethos-U Vela compiler
!pip3 install ethos-u-vela

# Download the specific Himax configuration for the Grove Vision AI V2
!wget https://raw.githubusercontent.com/HimaxWiseEyePlus/ML_FVP_EVALUATION/main/vela/himax_vela.ini
```

---

**online documentation**
[pypi ethos-u-vela 4.5.0](https://pypi.org/project/ethos-u-vela/)
[arm developer ethos-u vela compiler](https://developer.arm.com/documentation/109267/0102/Tool-support-for-the-Arm-Ethos-U-NPU/Ethos-U-Vela-compiler?lang=en)

---

**vela.tflite** is the optimized for Arm Ethos-U NPUs
(.tflite files run on CPU only)

**Ethos-U Vela** is a software tool developed by Arm that compiles a TFLM model into an optimized version that runs on an Ethos-U NPU.
- The Vela compiler performs various memory optimizations to reduce both permanent, (for example flash) and runtime (for example SRAM) memory requirements.
- The Vela compiler can report estimated performance
```
YOLO (PyTorch)
   ↓
INT8 TFLite (Ultralytics export)
   ↓
Vela compiler
   ↓
int8_vela.tflite (NPU optimized)
```
---

There is a known issue when using Ethos-U Vela with older versions of NumPy that uses different C APIs. 
```python
vela your_int8_model.tflite --config ethos-u55 --outdir ./grove_output
```

```python
vela your_int8_model.tflite --config ethos-u55 --outdir ./grove_output
```


---



