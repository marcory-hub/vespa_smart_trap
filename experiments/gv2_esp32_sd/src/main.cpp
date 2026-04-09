// GV2 SD capture control firmware for ESP32-S3
// Uses Seeed_Arduino_SSCMA to talk to Grove Vision AI V2 over UART.

// Set to 1 to run UART test only: listen on Grove UART (Serial1) and echo to USB.
// Use serial monitor at 115200; type AT+ID? and press Enter to ping GV2.
#define UART_TEST_MODE 1

#include <Arduino.h>
#include <stdint.h>

#if !UART_TEST_MODE
// External library from Seeed (Seeed_Arduino_SSCMA).
#include <Seeed_Arduino_SSCMA.h>

#ifdef ESP32
// XIAO ESP32S3: Grove UART is on Serial1 (D6=TX=GPIO43, D7=RX=GPIO44).
#define atSerial Serial1
#else
#define atSerial Serial1
#endif

SSCMA AI;
#endif

#if !UART_TEST_MODE
// --- Configuration constants ---

// Classes of interest.
static const int kMinClassId = 0;
static const int kMaxClassId = 3;

// Timing rules (milliseconds).
static const uint32_t kNoDetectionResetMs = 5000;   // 5 seconds of no detection resets state.
static const uint32_t kMinSaveIntervalMs  = 15000;  // 15 seconds between images for the same object.

// Image count rule.
static const uint8_t kMaxImagesPerObject = 3;

// Overlap rule (simple IoU threshold).
static const float kIouThreshold = 0.3f;

// --- Data structures ---

struct Box {
    float x;
    float y;
    float w;
    float h;
};

struct TrackedObject {
    bool active;
    int class_id;
    Box box;
    uint32_t last_seen_ms;
    uint32_t last_saved_ms;
    uint8_t saved_count;
};

// We keep a small fixed set of tracked objects per class.
static const size_t kMaxTrackedPerClass = 4;

struct ClassTracker {
    TrackedObject objects[kMaxTrackedPerClass];
};

ClassTracker trackers[kMaxClassId + 1];

// Time of last valid detection for any of the tracked classes.
uint32_t g_last_any_detection_ms = 0;

// --- Utility functions ---

static float compute_iou(const Box &a, const Box &b) {
    const float ax1 = a.x;
    const float ay1 = a.y;
    const float ax2 = a.x + a.w;
    const float ay2 = a.y + a.h;

    const float bx1 = b.x;
    const float by1 = b.y;
    const float bx2 = b.x + b.w;
    const float by2 = b.y + b.h;

    const float inter_x1 = (ax1 > bx1) ? ax1 : bx1;
    const float inter_y1 = (ay1 > by1) ? ay1 : by1;
    const float inter_x2 = (ax2 < bx2) ? ax2 : bx2;
    const float inter_y2 = (ay2 < by2) ? ay2 : by2;

    const float inter_w = inter_x2 - inter_x1;
    const float inter_h = inter_y2 - inter_y1;

    if (inter_w <= 0.0f || inter_h <= 0.0f) {
        return 0.0f;
    }

    const float inter_area = inter_w * inter_h;
    const float area_a = a.w * a.h;
    const float area_b = b.w * b.h;
    const float union_area = area_a + area_b - inter_area;
    if (union_area <= 0.0f) {
        return 0.0f;
    }
    return inter_area / union_area;
}

static bool class_in_range(int class_id) {
    return class_id >= kMinClassId && class_id <= kMaxClassId;
}

// Find or create a tracked object for this detection.
static TrackedObject *match_or_create_object(int class_id, const Box &box, uint32_t now_ms) {
    if (!class_in_range(class_id)) {
        return nullptr;
    }
    ClassTracker &ct = trackers[class_id];

    // Try to match an existing active object.
    float best_iou = 0.0f;
    TrackedObject *best_obj = nullptr;
    for (size_t i = 0; i < kMaxTrackedPerClass; ++i) {
        TrackedObject &obj = ct.objects[i];
        if (!obj.active) {
            continue;
        }
        float iou = compute_iou(obj.box, box);
        if (iou > best_iou) {
            best_iou = iou;
            best_obj = &obj;
        }
    }

    if (best_obj != nullptr && best_iou >= kIouThreshold) {
        best_obj->box = box;
        best_obj->last_seen_ms = now_ms;
        return best_obj;
    }

    // No suitable match; create a new object in the first free slot.
    for (size_t i = 0; i < kMaxTrackedPerClass; ++i) {
        TrackedObject &obj = ct.objects[i];
        if (!obj.active) {
            obj.active = true;
            obj.class_id = class_id;
            obj.box = box;
            obj.last_seen_ms = now_ms;
            obj.last_saved_ms = 0;
            obj.saved_count = 0;
            return &obj;
        }
    }

    // No free slot available.
    Serial.println("[track] No free slot for new object");
    return nullptr;
}

static void reset_all_trackers() {
    for (int class_id = kMinClassId; class_id <= kMaxClassId; ++class_id) {
        ClassTracker &ct = trackers[class_id];
        for (size_t i = 0; i < kMaxTrackedPerClass; ++i) {
            ct.objects[i].active = false;
            ct.objects[i].saved_count = 0;
            ct.objects[i].last_seen_ms = 0;
            ct.objects[i].last_saved_ms = 0;
        }
    }
}

// Build a human-readable filename for logging; GV2 naming is controlled by its firmware.
static String build_intended_filename(const TrackedObject &obj, uint32_t now_ms) {
    // Simple placeholder using millis instead of real date-time.
    // [to be verified] Map millis to real RTC time if available.
    char buffer[64];
    // Use milliseconds as a stand-in timestamp.
    snprintf(buffer, sizeof(buffer),
             "class%d_%010lu_%u.jpg",
             obj.class_id,
             static_cast<unsigned long>(now_ms),
             static_cast<unsigned>(obj.saved_count + 1));
    return String(buffer);
}

// Trigger GV2 to save a JPEG to its SD card.
// [to be verified] Exact sequence of save_jpeg / clean_actions calls for one-shot saves.
static bool trigger_jpeg_save(const TrackedObject &obj, uint32_t now_ms) {
    const String intended_name = build_intended_filename(obj, now_ms);
    Serial.print("[save] Requesting snapshot for class ");
    Serial.print(obj.class_id);
    Serial.print(" (intended name: ");
    Serial.print(intended_name);
    Serial.println(")");

    // Clear any previous actions, then set save_jpeg.
    AI.clean_actions();
    AI.save_jpeg();

    // Invoke once; according to Seeed docs this will save a JPEG to SD.
    int err = AI.invoke(1, false, true);
    if (err != CMD_OK) {
        Serial.print("[save] ERROR: invoke failed, code=");
        Serial.println(err);
        // Clear actions on failure too.
        AI.clean_actions();
        return false;
    }

    Serial.println("[save] Snapshot saved to GV2 SD (see default export folder).");

    // Clear action sets so future invokes do not keep saving images.
    AI.clean_actions();
    return true;
}

// --- Setup and main loop ---

void setup() {
    Serial.begin(115200);
    while (!Serial) {
        // Wait for USB serial on some boards.
        delay(10);
    }
    Serial.println();
    Serial.println("[init] GV2 SD capture control starting...");

    // Initialize trackers.
    reset_all_trackers();
    g_last_any_detection_ms = 0;

    // Initialize GV2 communication (Serial1 = Grove D6/D7 on XIAO ESP32S3, 921600 baud).
    AI.begin(&atSerial);

    Serial.println("[init] SSCMA AI interface initialized (Serial1 = Grove UART).");
}

// Process one round of detections and apply tracking logic.
static void process_detections(uint32_t now_ms) {
    // Invoke once, no filter, result only (no image data).
    int err = AI.invoke(1, false, false);
    if (err != CMD_OK) {
        Serial.print("[invoke] ERROR: code=");
        Serial.print(err);
        if (err == CMD_ETIMEDOUT) {
            Serial.print(" (timeout: no reply from GV2; check Grove UART cable and power)");
        }
        Serial.println();
        return;
    }

    auto &boxes = AI.boxes();
    if (boxes.size() == 0) {
        return;
    }

    bool any_tracked_class_seen = false;

    for (size_t i = 0; i < boxes.size(); ++i) {
        const auto &b = boxes[i];
        int class_id = b.target;
        float score = b.score;
        // Basic log for raw detection.
        Serial.print("[det] class=");
        Serial.print(class_id);
        Serial.print(" score=");
        Serial.print(score, 3);
        Serial.print(" x=");
        Serial.print(b.x);
        Serial.print(" y=");
        Serial.print(b.y);
        Serial.print(" w=");
        Serial.print(b.w);
        Serial.print(" h=");
        Serial.println(b.h);

        if (!class_in_range(class_id)) {
            continue;
        }
        any_tracked_class_seen = true;

        Box box{b.x, b.y, b.w, b.h};
        TrackedObject *obj = match_or_create_object(class_id, box, now_ms);
        if (obj == nullptr) {
            continue;
        }

        // Decide whether to save an image for this object.
        if (obj->saved_count >= kMaxImagesPerObject) {
            Serial.print("[logic] class ");
            Serial.print(class_id);
            Serial.println(" already reached max images for this object.");
            continue;
        }

        if (obj->last_saved_ms != 0) {
            const uint32_t since_last_save = now_ms - obj->last_saved_ms;
            if (since_last_save < kMinSaveIntervalMs) {
                Serial.print("[logic] cooldown active for class ");
                Serial.print(class_id);
                Serial.print(" (");
                Serial.print(since_last_save);
                Serial.println("ms since last save).");
                continue;
            }
        }

        // At this point we can request a JPEG save.
        if (trigger_jpeg_save(*obj, now_ms)) {
            obj->saved_count += 1;
            obj->last_saved_ms = now_ms;
        }
    }

    if (any_tracked_class_seen) {
        g_last_any_detection_ms = now_ms;
    }
}

void loop() {
    const uint32_t now_ms = millis();

    // Reset state if we have gone too long without any detections.
    if (g_last_any_detection_ms != 0) {
        const uint32_t since_last_detection = now_ms - g_last_any_detection_ms;
        if (since_last_detection >= kNoDetectionResetMs) {
            Serial.println("[logic] No detections for 5s, resetting all trackers.");
            reset_all_trackers();
            g_last_any_detection_ms = 0;
        }
    }

    // Process one detection cycle.
    process_detections(now_ms);

    // Small delay to avoid flooding the UART and to give time for inference.
    delay(100);
}

#else
// --- UART test mode: echo Serial1 (Grove) <-> Serial (USB) to verify GV2 link ---
// Try 921600 first (GV2 default); if no reply, change to 9600 and reflash.
static const uint32_t kTestBaud = 921600;

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) { delay(10); }
    Serial.println();
    Serial.println("[UART test] GV2 link check on Serial1 (Grove UART port).");
    Serial.println("[UART test] Baud: " + String(kTestBaud) + ". If no reply, set kTestBaud=9600 and reflash.");
    Serial.println("[UART test] Type AT+ID? and Enter to ping GV2. Any reply will appear below.");
    Serial.println();

    // RX=44 (D7), TX=43 (D6) on XIAO ESP32S3. If still no reply, try swapped: begin(..., 43, 44).
    Serial1.begin(kTestBaud, SERIAL_8N1, 44, 43);
}

void loop() {
    // GV2 -> USB: print whatever arrives on the Grove UART.
    while (Serial1.available()) {
        int c = Serial1.read();
        if (c >= 32 && c <= 126) {
            Serial.write((char)c);
        } else {
            Serial.print("\\x");
            if (c < 16) Serial.print('0');
            Serial.print(c, HEX);
        }
    }
    // USB -> GV2: forward typed lines to GV2 (add CR so GV2 gets full command).
    while (Serial.available()) {
        String line = Serial.readStringUntil('\n');
        if (line.length() > 0) {
            Serial1.print(line);
            Serial1.print("\r\n");
            Serial.print("[sent] ");
            Serial.println(line);
        }
    }
    delay(1);
}
#endif

