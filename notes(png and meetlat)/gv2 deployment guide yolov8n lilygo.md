
**One-line purpose:** gv2 yolov8n deployment guide
**Short summary:** 
**Agent:** inactive, testing swift-yolo has priority because of ease of use

---


# Grove Vision AI V2 Deployment Guide for YOLOv8n INT8 TFLite

## Current Status Assessment

### **What Works**
- Hardware: LilyGO-T-SIM7080G ESP32S3 + Grove Vision AI V2
- Model: YOLOv8n INT8 TFLite (192x192)
- Dataset: 4 classes (amel, vcra, vespsp, vvel) - 10,558 train + 3,152 val images
- I2C Communication: GPIO 2 (SDA), GPIO 1 (SCL)

### **Current Limitations**
1. **SenseCraft AI Platform**: Only interface for model upload
2. **Custom Model Support**: Not yet available for user-uploaded models
3. **Swift-YOLO Only**: Only Swift-YOLO models currently supported

## Deployment Options

### Option 1: SSCMA Library Approach (Test First)

#### Hardware Setup
```
LilyGO-T-SIM7080G    Grove Vision AI V2
┌─────────────────┐   ┌─────────────────┐
│ GPIO 2 (SDA) ───┼───┤ SDA            │
│ GPIO 1 (SCL) ───┼───┤ SCL            │
│ 3.3V ───────────┼───┤ VCC            │
│ GND ────────────┼───┤ GND            │
└─────────────────┘   └─────────────────┘
```

#### Software Requirements
1. **Arduino IDE** with ESP32 board support
2. **SSCMA Library** (install via Library Manager)
3. **YOLOv8n INT8 TFLite model** (192x192)

#### Arduino Sketch
```cpp
#include <Wire.h>
#include <SSCMA.h>
#include <SPIFFS.h>

SSCMA sscma;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("YOLOv8n deployment on ESP32S3 + Grove Vision AI V2");
  
  // Initialize SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS initialization failed");
    while (1);
  }
  
  // Initialize I2C for LilyGO-T-SIM7080G
  Wire.begin(2, 1);  // SDA=GPIO2, SCL=GPIO1
  Serial.println("I2C initialized: SDA=GPIO2, SCL=GPIO1");
  
  // Initialize Grove Vision AI V2
  if (!sscma.begin(&Wire, SSCMA_I2C_ADDRESS, 2, 400000)) {
    Serial.println("Grove Vision AI V2 initialization failed");
    Serial.println("Check I2C connections and power supply");
    while (1);
  }
  
  Serial.println("Grove Vision AI V2 initialized successfully");
  
  // Load model (may fail due to format limitations)
  if (sscma.loadModel("/yolov8n.tflite") != 0) {
    Serial.println("Model loading failed - format may not be supported");
    Serial.println("Current limitation: Only Swift-YOLO models supported");
    while (1);
  }
  
  Serial.println("YOLOv8n model loaded successfully");
}

void loop() {
  int result = sscma.invoke(1, true, true);
  
  if (result == 0) {
    sscma_result_t *results = sscma.getResults();
    
    if (results->num > 0) {
      Serial.printf("Detected %d objects:\n", results->num);
      
      for (int i = 0; i < results->num; i++) {
        Serial.printf("Detection %d: Class %d, Confidence %.2f\n",
          i, results->objects[i].target, results->objects[i].confidence);
      }
    }
  }
  
  delay(1000);
}
```

### Option 2: Swift-YOLO Retraining (Backup Plan)

#### Why Swift-YOLO?
- Currently supported by Grove Vision AI V2
- Based on YOLOv5 (good for small objects)
- 192x192 input size supported

#### Training Process
```python
# Convert dataset to Swift-YOLO format
# Use SenseCraft AI platform for training
# Export as Swift-YOLO model
```

### Option 3: Alternative Hardware (Fallback)

#### ESP32S3 + Camera Module
- **ESP32S3 DevKit** + **OV2640/OV5640 camera**
- Direct TFLite deployment support
- More flexible model formats

#### Hardware Setup
```
ESP32S3 DevKit + Camera Module
┌─────────────────┐
│ ESP32S3 DevKit  │
│ + Camera Module │
└─────────────────┘
```

## Immediate Action Plan

### Step 1: Test Current Setup (Today)
1. **Hardware Assembly**
   - Connect LilyGO-T-SIM7080G to Grove Vision AI V2
   - Verify I2C communication
   - Test power supply

2. **Software Test**
   - Upload basic SSCMA test sketch
   - Check Serial Monitor output
   - Verify Grove Vision AI V2 initialization

### Step 2: Model Format Test (Tomorrow)
1. **Export YOLOv8n to INT8 TFLite**
   ```python
   from ultralytics import YOLO
   model = YOLO('best.pt')
   model.export(format='tflite', int8=True, imgsz=192)
   ```

2. **Test Model Loading**
   - Upload model to SPIFFS
   - Try SSCMA library loading
   - Document any error messages

### Step 3: Alternative Preparation (This Week)
1. **Swift-YOLO Training**
   - Prepare dataset in Swift-YOLO format
   - Train on SenseCraft AI platform
   - Test Swift-YOLO deployment

2. **Alternative Hardware Research**
   - Research ESP32S3 + camera alternatives
   - Compare performance and cost
   - Prepare fallback implementation

## Troubleshooting Guide

### I2C Communication Issues
```cpp
// Test I2C scanner
#include <Wire.h>

void setup() {
  Serial.begin(115200);
  Wire.begin(2, 1);  // SDA=GPIO2, SCL=GPIO1
}

void loop() {
  Serial.println("I2C Scanner");
  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    byte error = Wire.endTransmission();
    if (error == 0) {
      Serial.printf("I2C device found at address 0x%02X\n", address);
    }
  }
  delay(5000);
}
```

### Expected I2C Addresses
- **Grove Vision AI V2**: 0x12 (default)
- **Other devices**: Check documentation

### Power Supply Issues
- **Voltage**: Ensure 3.3V supply
- **Current**: Grove Vision AI V2 needs ~200mA
- **Stability**: Use stable power supply

## Performance Expectations

### Grove Vision AI V2 (Current Setup)
- **Inference Time**: ~100-200ms per frame
- **Model Size**: <2MB for optimal performance
- **Input Resolution**: 192x192 (optimal)
- **Accuracy**: >90% (field conditions)

### Alternative Hardware (ESP32S3 + Camera)
- **Inference Time**: ~200-500ms per frame
- **Model Size**: <4MB
- **Input Resolution**: 320x320 (possible)
- **Accuracy**: >85% (field conditions)

## Next Steps Priority

1. **Immediate (Today)**: Test hardware connections and basic communication
2. **Short-term (This Week)**: Test YOLOv8n model loading, prepare Swift-YOLO backup
3. **Medium-term (Next Week)**: Evaluate alternative hardware if needed
4. **Long-term (Next Month)**: Optimize for production deployment

## Contact Information

### Seeed Studio Support
- **Forum**: https://forum.seeedstudio.com/
- **Documentation**: https://wiki.seeedstudio.com/
- **Custom Model Support**: Monitor for updates

### Community Resources
- **ESP32 Community**: https://esp32.com/
- **Arduino Forum**: https://forum.arduino.cc/
- **GitHub Issues**: Check SSCMA repository for updates

## Success Metrics

### Technical Metrics
- **Detection Accuracy**: >90% for vvel class
- **False Positive Rate**: <5% for non-target insects
- **Inference Speed**: <200ms per frame
- **Power Consumption**: <500mA total

### Operational Metrics
- **Field Reliability**: >95% uptime
- **Maintenance**: <1 hour per month
- **Cost**: <€200 per unit (production)

## Notes
- Current Grove Vision AI V2 limitations are temporary
- Swift-YOLO provides good fallback option
- Alternative hardware offers more flexibility
- Focus on vvel detection accuracy as primary goal 