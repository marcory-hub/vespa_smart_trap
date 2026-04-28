// ESP32-S3 receiver for GV2 UART output
//
// Hardware setup:
// - GV2 is powered via USB-C.
// - ESP32-S3 USB is used only for Serial Monitor / JPEG capture verification.
// - UART via GV2 socket -> ESP32-S3 pins:
//   - ESP32-S3 GPIO44 = Serial1 RX  (connect to GV2 TX)
//   - ESP32-S3 GPIO43 = Serial1 TX  (connect to GV2 RX)
//
// Protocol (GV2 -> ESP32-S3):
// - State frame: 'V''S''T''S' + state(1)
// - JPEG frame:  'V''S''T''J' + state(1) + class_idx(1)+ conf(1) + len_u32_le(4) + jpeg_payload(len)
//
// USB output (ESP32-S3 -> host):
// - Prints: recv #<n> len=<bytes> state=<...> class=<...> conf_u8=<...> conf=<...>\n
// - Immediately followed by raw JPEG bytes (exactly len bytes), so scripts/capture_gv2_uart_jpeg.py can save it.

#include <Arduino.h>
#include <stdint.h>

static const int kUartRxGpio = 44;
static const int kUartTxGpio = 43;

static const uint32_t kGv2UartBaud = 921600;
static const uint32_t kUsbSerialBaud = 921600;

static const uint8_t kJpegMagic[4] = {'V', 'S', 'T', 'J'};
static const uint8_t kStateMagic[4] = {'V', 'S', 'T', 'S'};

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
    uint32_t last_forwarded_ms = 0;

    bool forward_jpeg_usb = false;
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

    // Rate limit forwarding to keep host capture manageable and match the existing behavior.
    const uint32_t now = millis();
    if (now - s->last_forwarded_ms < 500) {
        s->receiving_jpeg = true;
        s->jpeg_remaining = s->frame_len;
        s->forward_jpeg_usb = false;
        Serial.print("[jpeg] drop len=");
        Serial.print(s->frame_len);
        Serial.print(" class=");
        Serial.print(s->frame_class_idx);
        Serial.print(" conf_u8=");
        Serial.println(s->frame_conf_u8);
        return;
    }

    s->last_forwarded_ms = now;
    s->image_counter++;

    Serial.print("recv #");
    Serial.print(s->image_counter);
    Serial.print(" len=");
    Serial.print(s->frame_len);
    Serial.print(" state=");
    Serial.print(s->frame_state);
    Serial.print(" class=");
    Serial.print(s->frame_class_idx);
    Serial.print(" conf=");
    Serial.println(static_cast<float>(s->frame_conf_u8) / 255.0f, 3);

    s->receiving_jpeg = true;
    s->jpeg_remaining = s->frame_len;
    s->forward_jpeg_usb = true;
}

static void consume_uart(JpegRxState* jpeg_rx, StateRxState* state_rx) {
    if (!jpeg_rx || !state_rx) return;

    while (Serial1.available() > 0) {
        if (jpeg_rx->receiving_jpeg) {
            static uint8_t buf[256];
            const int avail_i = Serial1.available();
            if (avail_i <= 0) break;

            uint32_t to_read = static_cast<uint32_t>(avail_i);
            if (to_read > jpeg_rx->jpeg_remaining) to_read = jpeg_rx->jpeg_remaining;
            if (to_read > sizeof(buf)) to_read = sizeof(buf);

            const size_t n = Serial1.readBytes(buf, static_cast<size_t>(to_read));
            if (n == 0) break;

            if (jpeg_rx->forward_jpeg_usb) {
                Serial.write(buf, n);
            }

            jpeg_rx->jpeg_remaining -= static_cast<uint32_t>(n);
            if (jpeg_rx->jpeg_remaining == 0) {
                jpeg_rx->receiving_jpeg = false;
            }
            continue;
        }

        const int b = Serial1.read();
        if (b < 0) break;
        const uint8_t value = static_cast<uint8_t>(b);

        // 1) Framed state messages: 'V''S''T''S' + state(1)
        shift_magic_window(state_rx->magic_window, &state_rx->magic_filled, value);
        if (magic_matches(state_rx->magic_window, state_rx->magic_filled, kStateMagic)) {
            if (Serial1.available() >= 1) {
                // State byte is informational only for this receiver (printed by GV2 in JPEG header anyway).
                (void)Serial1.read();
            }
        }

        // 2) Scan for JPEG magic
        shift_magic_window(jpeg_rx, value);
        if (!magic_window_matches(*jpeg_rx)) continue;

        // Read header: state, class_idx, conf, len_u32_le
        if (Serial1.available() < 1 + 1 + 1 + 4) {
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

        on_jpeg_frame_start(jpeg_rx);
    }
}

void setup() {
    Serial.begin(kUsbSerialBaud);
    delay(200);
    Serial.println();
    Serial.println("[init] GV2 UART receiver starting...");

    Serial1.begin(kGv2UartBaud, SERIAL_8N1, kUartRxGpio, kUartTxGpio);
    Serial.print("[init] Serial1 RX=GPIO");
    Serial.print(kUartRxGpio);
    Serial.print(" TX=GPIO");
    Serial.print(kUartTxGpio);
    Serial.print(" baud=");
    Serial.println(kGv2UartBaud);
}

void loop() {
    static JpegRxState jpeg_rx;
    static StateRxState state_rx;
    consume_uart(&jpeg_rx, &state_rx);
}

