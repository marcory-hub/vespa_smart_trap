// ESP32-S3 to test gv2-uart firmware 
//
// Wiring (ESP32-S3):
// - Red LED: GPIO2
// - Yellow LED: GPIO3 (power-on self-test, 3 blinks)
// - Green LED: GPIO4
//
// UART (GV2 socket → ESP32-S3 Grove UART pins):
// - ESP32-S3 GPIO44 = Serial1 RX  (connect to GV2 TX)
// - ESP32-S3 GPIO43 = Serial1 TX  (connect to GV2 RX)
//
// Protocol (GV2 → ESP32-S3):
// - GV2 sends 1 byte repeatedly:
//   - 0x00: none
//   - 0x01: Vespa velutina present => GPIO2 on
//   - 0x02: other class present   => GPIO4 on

#include <Arduino.h>
#include <stdint.h>

static const int kRedLedGpio = 2;
static const int kYellowLedGpio = 3;
static const int kGreenLedGpio = 4;

static const int kUartRxGpio = 44;
static const int kUartTxGpio = 43;

// Must match the GV2 firmware UART baudrate
static const uint32_t kGv2UartBaud = 921600;

enum class DetectionState : uint8_t {
    kNone = 0,
    kVvel = 1,
    kOtherClass = 2,
};

static void set_all_leds_off() {
    digitalWrite(kRedLedGpio, LOW);
    digitalWrite(kYellowLedGpio, LOW);
    digitalWrite(kGreenLedGpio, LOW);
}

static void set_leds_for_state(DetectionState state) {
    const bool red_on = (state == DetectionState::kVvel);
    const bool green_on = (state == DetectionState::kOtherClass);

    digitalWrite(kRedLedGpio, red_on ? HIGH : LOW);
    digitalWrite(kGreenLedGpio, green_on ? HIGH : LOW);
}

static void power_on_self_test_yellow_led() {
    for (int i = 0; i < 3; ++i) {
        digitalWrite(kYellowLedGpio, HIGH);
        delay(500);
        digitalWrite(kYellowLedGpio, LOW);
        delay(500);
    }
}

static bool is_valid_state_byte(uint8_t value) {
    return value == static_cast<uint8_t>(DetectionState::kNone) ||
           value == static_cast<uint8_t>(DetectionState::kVvel) ||
           value == static_cast<uint8_t>(DetectionState::kOtherClass);
}

static const uint8_t kJpegMagic[4] = {'V', 'S', 'T', 'J'};
static const uint8_t kStateMagic[4] = {'V', 'S', 'T', 'S'};

static const uint32_t kNoUartBytesFailSafeMs = 1000;
static const uint32_t kStateFrameFailSafeMs = 1000;
// Not sure if we need a small delay to prevent flickering when signals are dropped for the step motors? If not, comment this out.
static const uint32_t kLedOffDelayMs = 100;

static bool read_u32_le_from_uart(uint32_t* out_value) {
    if (!out_value) return false;
    uint8_t b[4];
    for (int i = 0; i < 4; ++i) {
        const int v = Serial1.read();
        if (v < 0) return false;
        b[i] = static_cast<uint8_t>(v);
    }
    *out_value = (static_cast<uint32_t>(b[0])      ) |
                 (static_cast<uint32_t>(b[1]) <<  8) |
                 (static_cast<uint32_t>(b[2]) << 16) |
                 (static_cast<uint32_t>(b[3]) << 24);
    return true;
}

struct JpegRxState {
    uint8_t magic_window[4] = {0, 0, 0, 0};
    uint8_t magic_filled = 0;

    bool receiving_jpeg = false;
    uint32_t jpeg_remaining = 0;

    uint8_t frame_state = 0;
    uint8_t frame_class_idx = 0;
    uint8_t frame_conf_u8 = 0;
    uint32_t frame_len = 0;

    uint32_t image_counter = 0;
    uint32_t last_saved_ms = 0;

    // Preview (print first N JPEG payload bytes as hex)
    uint8_t preview_remaining = 0;
    bool preview_printed_prefix = false;
};

struct StateRxState {
    uint8_t magic_window[4] = {0, 0, 0, 0};
    uint8_t magic_filled = 0;
};

static void shift_magic_window(uint8_t* window, uint8_t* filled, uint8_t byte_value) {
    if (*filled < 4) {
        window[(*filled)++] = byte_value;
        return;
    }
    window[0] = window[1];
    window[1] = window[2];
    window[2] = window[3];
    window[3] = byte_value;
}

static bool magic_matches(const uint8_t* window, uint8_t filled, const uint8_t* magic) {
    if (filled < 4) return false;
    for (int i = 0; i < 4; ++i) {
        if (window[i] != magic[i]) return false;
    }
    return true;
}

static void shift_magic_window(JpegRxState* s, uint8_t byte_value) {
    shift_magic_window(s->magic_window, &s->magic_filled, byte_value);
}

static bool magic_window_matches(const JpegRxState& s) {
    return magic_matches(s.magic_window, s.magic_filled, kJpegMagic);
}

static void on_jpeg_frame_start(JpegRxState* s) {
    if (!s) return;
    const uint32_t now = millis();
    // Limit to max 2 images per second.
    if (now - s->last_saved_ms < 500) {
        s->receiving_jpeg = true;
        s->jpeg_remaining = s->frame_len;
        s->preview_remaining = 0;
        s->preview_printed_prefix = false;
        Serial.print("[jpeg] drop len=");
        Serial.print(s->frame_len);
        Serial.print(" class=");
        Serial.print(s->frame_class_idx);
        Serial.print(" conf_u8=");
        Serial.println(s->frame_conf_u8);
        return;
    }

    s->last_saved_ms = now;
    s->image_counter++;

    // NOTE: On XIAO ESP32-S3 we usually don't have SD. For now we just consume bytes.
    // When you move to LilyGO T-SIM7080G-S3, this is where you open an SD file and stream-write.
    Serial.print("[jpeg] recv #");
    Serial.print(s->image_counter);
    Serial.print(" len=");
    Serial.print(s->frame_len);
    Serial.print(" state=");
    Serial.print(s->frame_state);
    Serial.print(" class=");
    Serial.print(s->frame_class_idx);
    Serial.print(" conf_u8=");
    Serial.print(s->frame_conf_u8);
    Serial.print(" conf=");
    Serial.println(static_cast<float>(s->frame_conf_u8) / 255.0f, 3);

    s->receiving_jpeg = true;
    s->jpeg_remaining = s->frame_len;

    s->preview_remaining = 16;
    s->preview_printed_prefix = false;
}

static void consume_uart(JpegRxState* jpeg_rx,
                         StateRxState* state_rx,
                         DetectionState* out_state,
                         bool* out_saw_any_byte,
                         bool* out_saw_valid_state) {
    if (!jpeg_rx || !state_rx || !out_state) return;
    if (out_saw_any_byte) *out_saw_any_byte = false;
    if (out_saw_valid_state) *out_saw_valid_state = false;

    while (Serial1.available() > 0) {
        const int b = Serial1.read();
        if (b < 0) break;
        if (out_saw_any_byte) *out_saw_any_byte = true;

        const uint8_t value = static_cast<uint8_t>(b);

        if (jpeg_rx->receiving_jpeg) {
            if (jpeg_rx->preview_remaining > 0) {
                if (!jpeg_rx->preview_printed_prefix) {
                    jpeg_rx->preview_printed_prefix = true;
                    Serial.print("[jpeg] head:");
                }
                Serial.print(" 0x");
                if (value < 16) Serial.print("0");
                Serial.print(value, HEX);
                jpeg_rx->preview_remaining--;
                if (jpeg_rx->preview_remaining == 0) {
                    Serial.println();
                }
            }
            if (jpeg_rx->jpeg_remaining > 0) {
                jpeg_rx->jpeg_remaining--;
            }
            if (jpeg_rx->jpeg_remaining == 0) {
                jpeg_rx->receiving_jpeg = false;
                if (jpeg_rx->preview_printed_prefix && jpeg_rx->preview_remaining > 0) {
                    Serial.println();
                }
                Serial.println("[jpeg] done");
            }
            continue;
        }

        // 1) Framed state messages: 'V''S''T''S' + state(1)
        shift_magic_window(state_rx->magic_window, &state_rx->magic_filled, value);
        if (magic_matches(state_rx->magic_window, state_rx->magic_filled, kStateMagic)) {
            if (Serial1.available() >= 1) {
                const int st = Serial1.read();
                if (st >= 0 && is_valid_state_byte(static_cast<uint8_t>(st))) {
                    *out_state = static_cast<DetectionState>(static_cast<uint8_t>(st));
                    if (out_saw_valid_state) *out_saw_valid_state = true;
                }
            }
        }

        // 2) Scan for JPEG magic (needed to detect if a jpg is coming and not some noise)
        shift_magic_window(jpeg_rx, value);
        if (!magic_window_matches(*jpeg_rx)) continue;

        // Try to read the rest of the header (state, class_idx, conf_u8, len_u32_le).
        if (Serial1.available() < 1 + 1 + 1 + 4) {
            // Not enough bytes yet; wait for next loop iteration.
            continue;
        }

        const int st = Serial1.read();
        const int cls = Serial1.read();
        const int conf = Serial1.read();
        uint32_t len = 0;
        if (st < 0 || cls < 0 || conf < 0 || !read_u32_le_from_uart(&len)) {
            continue;
        }

        jpeg_rx->frame_state = static_cast<uint8_t>(st);
        jpeg_rx->frame_class_idx = static_cast<uint8_t>(cls);
        jpeg_rx->frame_conf_u8 = static_cast<uint8_t>(conf);
        jpeg_rx->frame_len = len;

        // The JPEG header carries a framed state too; treat it as authoritative.
        // This prevents outputs "sticking" when state frames are delayed by JPEG payload.
        if (is_valid_state_byte(jpeg_rx->frame_state)) {
            *out_state = static_cast<DetectionState>(jpeg_rx->frame_state);
            if (out_saw_valid_state) *out_saw_valid_state = true;
        }

        on_jpeg_frame_start(jpeg_rx);
    }
}

void setup() {
    pinMode(kRedLedGpio, OUTPUT);
    pinMode(kYellowLedGpio, OUTPUT);
    pinMode(kGreenLedGpio, OUTPUT);
    set_all_leds_off();
    power_on_self_test_yellow_led();

    Serial.begin(115200);
    delay(200);
    // Do not wait for Serial connection: this firmware should behave the same
    // whether powered from USB or from the final power setup.
    Serial.println();
    Serial.println("[init] GV2 UART LED controller starting...");

    Serial1.begin(kGv2UartBaud, SERIAL_8N1, kUartRxGpio, kUartTxGpio);
    Serial.print("[init] Serial1 RX=GPIO");
    Serial.print(kUartRxGpio);
    Serial.print(" TX=GPIO");
    Serial.print(kUartTxGpio);
    Serial.print(" baud=");
    Serial.println(kGv2UartBaud);
}

void loop() {
    static DetectionState current_state = DetectionState::kNone;
    static uint32_t last_rx_ms = 0;
    static uint32_t last_heartbeat_ms = 0;
    static JpegRxState jpeg_rx;
    static StateRxState state_rx;
    static uint32_t last_state_ms = 0;
    static uint32_t last_non_none_state_ms = 0;

    bool saw_any_byte = false;
    bool saw_valid_state = false;
    DetectionState new_state = current_state;
    consume_uart(&jpeg_rx, &state_rx, &new_state, &saw_any_byte, &saw_valid_state);
    if (saw_any_byte) {
        last_rx_ms = millis();
    }

    if (saw_valid_state) {
        last_state_ms = millis();
        if (new_state != DetectionState::kNone) {
            last_non_none_state_ms = last_state_ms;
        }
    }

    // Heartbeat (disabled): keep code for future bring-up.
    // Visible heartbeat for bring-up: blink yellow briefly every 2 seconds.
    // This makes "firmware is running" obvious even without Serial attached.
    //
    // if (millis() - last_heartbeat_ms >= 2000) {
    //     last_heartbeat_ms = millis();
    //     digitalWrite(kYellowLedGpio, HIGH);
    //     delay(50);
    //     digitalWrite(kYellowLedGpio, LOW);
    //
    //     Serial.print("[hb] state=");
    //     Serial.print(static_cast<uint8_t>(current_state));
    //     Serial.print(" rx_age_ms=");
    //     Serial.println(static_cast<unsigned long>(millis() - last_rx_ms));
    // }

    // If we stop receiving UART bytes entirely, fail-safe to off.
    bool force_state_update = false;
    if (millis() - last_rx_ms > kNoUartBytesFailSafeMs) {
        new_state = DetectionState::kNone;
        force_state_update = true;
    }

    // If we keep receiving bytes (e.g. JPEG payload), but stop receiving framed state,
    // also fail-safe to off. This prevents "stuck ON" when GV2 stops sending state.
    if (millis() - last_state_ms > kStateFrameFailSafeMs) {
        new_state = DetectionState::kNone;
        force_state_update = true;
    }

    // Debounce/hold: don't turn outputs off immediately on brief "none" gaps.
    // Use last NON-NONE timestamp so "none" frames don't extend the hold window.
    if (new_state == DetectionState::kNone && (millis() - last_non_none_state_ms) < kLedOffDelayMs) {
        new_state = current_state;
        force_state_update = false;
        saw_valid_state = false;
    }

    if ((saw_valid_state || force_state_update) && new_state != current_state) {
        current_state = new_state;
        set_leds_for_state(current_state);
        Serial.print("[uart] state=");
        Serial.println(static_cast<uint8_t>(current_state));
    }
}

