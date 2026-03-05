**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---


# GV2 web flasher: what you need (from Seeed_Grove_Vision_AI_Module_V2)

**One-line purpose:** Checklist and protocol so others can flash GV2 from a browser (no Python/CLI).

**Source:** What you used to flash yesterday: [Seeed_Grove_Vision_AI_Module_V2](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2) (local: `himax/Seeed_Grove_Vision_AI_Module_V2`).

---

## 1. Artifacts to host (for “flash from internet site”)

| Asset | Description | Max size |
|-------|-------------|----------|
| **Firmware image** | `we2_image_gen_local/output_case1_sec_wlcsp/output.img` | 1 MB |
| **Model (optional)** | `yolo11n_*_vela.tflite` (int8 Vela, for YOLO11 OD) | &lt; 2.4 MB |

- Build once per app type (e.g. `APP_TYPE = tflm_yolo11_od`). One `output.img` can be reused for all models of that app.
- Per model: one `.tflite` URL. Flash address for YOLO11 OD: **0xB7B000**, offset **0x00000**.

---

## 2. Serial settings (browser = Web Serial API)

| Parameter | Value |
|-----------|--------|
| Baud rate | **921600** |
| Data | 8 bit |
| Parity | None |
| Stop | 1 bit |
| Flow control | None |

---

## 3. Protocol (exact sequence the site must implement)

User: connect GV2 via USB → open site → select model → “Connect device” (Web Serial) → **press RESET on GV2** (optionally hold any key except Enter before reset).

1. **Wait for bootloader prompt**  
   Device sends a line containing:  
   `Send data using the xmodem protocol from your terminal`

2. **Send** `1\r`  
   (enter Xmodem receive mode)

3. **Xmodem send** `output.img`  
   - Protocol: **Xmodem** (128-byte packets, CRC-16).  
   - After send, device asks: `Do you want to end file transmission and reboot system? (y)`

4. **If flashing a model:**  
   - Send `n\r` (do not reboot yet).  
   - **Send 1 × Xmodem block (128 bytes) = preamble:**  
     - Bytes 0–1: `0xC0, 0x5A`  
     - Bytes 2–5: `model_position` 32-bit little-endian (e.g. **0xB7B000** → `00 B0 B7 00`)  
     - Bytes 6–9: `model_offset` 32-bit little-endian (e.g. **0x00000** → `00 00 00 00`)  
     - Bytes 10–11: `0x5A, 0xC0`  
     - Bytes 12–127: `0xFF`  
   - Device again asks reboot? → send `n\r`.  
   - **Xmodem send** the `.tflite` file.  
   - Device asks reboot? → send `y\r` to reboot.

5. **If firmware only (no model):**  
   On first reboot prompt send `y\r`.

---

## 4. Xmodem parameters (sensible defaults)

- Packet size: **128 bytes** (standard Xmodem, not Xmodem-1K).  
- Timeouts/retries: e.g. maxTimeouts 30, maxErrors 50, crcAttempts 10 (as in SenseCraft logs).  
- All communication: binary over the same serial port (no separate channel).

---

## 5. What the website must do (no backend for flashing)

- **Frontend only:** Web Serial (Chrome/Edge) + Xmodem implemented in JavaScript.  
- **Backend (optional):** Serve SPA + `output.img` + `.tflite` files (or URLs) + a `models.json` listing (name, description, `firmwareUrl`, `modelUrl`, `flashAddress`, `flashOffset`).  
- **User flow:** Select model → Connect → Reset GV2 → site runs the sequence above.

---

## 6. One-shot reference: firmware + one model (YOLO11 OD)

- **Firmware:** `output.img` (from `we2_image_gen_local` with `tflm_yolo11_od`).  
- **Model:** one `*_vela.tflite`, address **0xB7B000**, offset **0x00000**.  
- **Order:** image → reboot prompt `n` → preamble (128 B) → reboot prompt `n` → `.tflite` → reboot prompt `y`.

---

## 7. Links

- Repo: [HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2)  
- Flash by Python: README sections “Flash Image Update at Linux/Windows Environment by python code”.  
- Preamble logic: `xmodem/xmodem_send.py` (header at line 203).  
- App type for YOLO11: `tflm_yolo11_od`; model address in `EPII_CM55M_APP_S/app/scenario_app/tflm_yolo11_od/common_config.h` (use **0xB7B000** for single-model flash).
