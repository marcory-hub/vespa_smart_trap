
**One-line purpose:** camera menuconfig
**Short summary:** Camera-related menuconfig settings for ESP32-S3 camera integration on the LilyGO T-SIM7080G-S3 board. These settings apply to OV2640, OV7670, OV7675.
**Agent:** inactive

---


# Camera Menuconfig Settings - Complete Reference

## Overview

Camera-related menuconfig settings for ESP32-S3 camera integration on the LilyGO T-SIM7080G-S3 board. These settings apply to OV2640, OV7670, OV7675.

## ESP32-S3 Specific Context

### Hardware Platform

**Target Board**: LilyGO T-SIM7080G-S3
- **Microcontroller**: ESP32-S3-WROOM-1-N16R8
- **Flash**: 16 MB
- **PSRAM**: 8 MB Octal Mode @ 80 MHz
- **Camera Interface**: DVP (Digital Video Port) - 8-bit parallel interface

### ESP32-S3 Camera Driver Behavior

On ESP32-S3, the camera driver automatically uses the LCD_CAM peripheral for XCLK generation. This is different from ESP32 (original), which uses LEDC.

**Key Points**:
1. **XCLK Generation**: Driver handles LCD_CAM peripheral automatically
2. **Only Configure**: `xclk_freq_hz` and `pin_xclk` in code
3. **Do NOT Configure**: LEDC channel/timer (that's for ESP32 original only)
4. **Do NOT Manually Configure**: LCD_CAM registers (driver handles this)

**Important**: These menuconfig settings are specific to ESP32-S3. If you are using ESP32 (original), the camera driver uses LEDC for XCLK generation instead of LCD_CAM.

## Complete Settings Summary

For quick reference, here are all required settings in one block:

```
# Sensor Support
CONFIG_OV2640_SUPPORT=y
CONFIG_OV7670_SUPPORT=y
CONFIG_OV7675_SUPPORT=y
CONFIG_OV7725_SUPPORT=y

# I2C/SCCB Configuration
CONFIG_SCCB_HARDWARE_I2C_DRIVER_NEW=y
CONFIG_SCCB_HARDWARE_I2C_PORT1=y
CONFIG_SCCB_CLK_FREQ=100000

# DMA Configuration
CONFIG_CAMERA_DMA_BUFFER_SIZE_MAX=32768
CONFIG_CAMERA_PSRAM_DMA=y

# LCD_CAM Configuration
CONFIG_LCD_CAM_ISR_IRAM_SAFE=y

# Task Configuration
CONFIG_CAMERA_TASK_STACK_SIZE=4096
CONFIG_CAMERA_CORE0=y

# JPEG Mode
CONFIG_CAMERA_JPEG_MODE_FRAME_SIZE_AUTO=y

# Converter (disabled)
# CONFIG_CAMERA_CONVERTER_ENABLED is not set
```


## Accessing Camera Configuration

### Method 1: Using VS Code ESP-IDF Extension (Recommended)

Open Command Palette: `Cmd + Shift + P` (Mac) or `Ctrl + Shift + P` (Windows/Linux)


### Method 2: Using Terminal

```bash
idf.py menuconfig
```

Then navigate to: **Component config → Camera configuration**

## Required Menuconfig Settings

### Sensor Support

Enable the sensors you plan to use:

```
CONFIG_OV2640_SUPPORT=y
CONFIG_OV7670_SUPPORT=y
CONFIG_OV7675_SUPPORT=y
CONFIG_OV7725_SUPPORT=y
```

### I2C/SCCB Configuration

These settings are required for proper camera detection and communication.

```
CONFIG_SCCB_HARDWARE_I2C_DRIVER_NEW=y
CONFIG_SCCB_HARDWARE_I2C_PORT1=y
CONFIG_SCCB_CLK_FREQ=100000
```

**Explanation**:
- **SCCB Hardware I2C Driver**: Use the new driver (not legacy)
- **SCCB Hardware I2C Port**: Port 1 matches code configuration (GPIO01/GPIO02)
- **SCCB Clock Frequency**: 100 kHz is standard and reliable. Can try 400000 (400 kHz) if needed, but 100 kHz is more stable

### DMA Buffer Configuration

```
CONFIG_CAMERA_DMA_BUFFER_SIZE_MAX=32768
```

**Explanation**: 32 KB buffer size is sufficient for most frame sizes. Increase if you need larger buffers for high-resolution frames.

### PSRAM DMA Configuration

```
CONFIG_CAMERA_PSRAM_DMA=y
```

**Explanation**: Required when using `CAMERA_FB_IN_PSRAM` in code configuration. Enables DMA transfers to/from PSRAM for better performance.

### LCD_CAM ISR Configuration

```
CONFIG_LCD_CAM_ISR_IRAM_SAFE=y
```

This is an optimization that can improve performance and reduce timing issues related to flash cache misses. The default is disabled (`n`), and cameras can operate without this setting.

### Camera Task Configuration

```
CONFIG_CAMERA_TASK_STACK_SIZE=4096
CONFIG_CAMERA_CORE0=y
```

**Explanation**:
- **Task Stack Size**: Default 4096 bytes is usually sufficient. Increase to 8192 if you encounter stack overflow errors
- **Core Affinity**: Core 0 is the default and works well for most applications

### JPEG Mode Configuration

```
CONFIG_CAMERA_JPEG_MODE_FRAME_SIZE_AUTO=y
```

**Explanation**: Auto frame size for JPEG mode. Not relevant for RGB565 format, but keep as default.

### Other Settings

```
CONFIG_CAMERA_CONVERTER_ENABLED is not set
```

**Explanation**: Camera converter is disabled by default. Keep disabled unless you specifically need format conversion features.


## Verification

After configuring menuconfig, save and exit. The settings will be saved to `sdkconfig`.

To verify the settings were saved correctly, run:

```bash
grep "CONFIG_OV" sdkconfig
grep "CONFIG_SCCB" sdkconfig
grep "CONFIG_CAMERA" sdkconfig
```

Expected output should include:
- `CONFIG_OV2640_SUPPORT=y`
- `CONFIG_OV7670_SUPPORT=y` (if enabled)
- `CONFIG_OV7675_SUPPORT=y` (if enabled)
- `CONFIG_SCCB_HARDWARE_I2C_DRIVER_NEW=y`
- `CONFIG_SCCB_HARDWARE_I2C_PORT1=y`
- `CONFIG_SCCB_CLK_FREQ=100000`
- `CONFIG_CAMERA_PSRAM_DMA=y`
- `CONFIG_CAMERA_DMA_BUFFER_SIZE_MAX=32768`
- `CONFIG_LCD_CAM_ISR_IRAM_SAFE=y`

## Settings by Camera Type

### OV2640 (Primary Configuration)

Required settings:
- `CONFIG_OV2640_SUPPORT=y`
- `CONFIG_SCCB_HARDWARE_I2C_DRIVER_NEW=y`
- `CONFIG_SCCB_HARDWARE_I2C_PORT1=y`
- `CONFIG_SCCB_CLK_FREQ=100000`
- `CONFIG_CAMERA_PSRAM_DMA=y`
- `CONFIG_CAMERA_DMA_BUFFER_SIZE_MAX=32768`

Recommended settings:
- `CONFIG_LCD_CAM_ISR_IRAM_SAFE=y` (optional, improves performance)

### OV7675 (Working Configuration)

Required settings:
- `CONFIG_OV7675_SUPPORT=y`
- `CONFIG_SCCB_HARDWARE_I2C_DRIVER_NEW=y`
- `CONFIG_SCCB_HARDWARE_I2C_PORT1=y`
- `CONFIG_SCCB_CLK_FREQ=100000`
- `CONFIG_CAMERA_PSRAM_DMA=y` (if using PSRAM frame buffers)
- `CONFIG_CAMERA_DMA_BUFFER_SIZE_MAX=32768`

### OV7670 (Module-Specific Issues)

Required settings:
- `CONFIG_OV7670_SUPPORT=y`
- `CONFIG_SCCB_HARDWARE_I2C_DRIVER_NEW=y`
- `CONFIG_SCCB_HARDWARE_I2C_PORT1=y`
- `CONFIG_SCCB_CLK_FREQ=100000`

**Note**: Some OV7670 modules may have I2C communication issues. If detection fails, verify hardware connections first.
