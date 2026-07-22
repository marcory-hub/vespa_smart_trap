
- UART0 is on PB0/PB1:
    
    - `PB0 / RX0`
    - `PB1 / TX0`
- UART1 is on PB6/PB7:
    
    - `PB6 / UART1_RX`
    - `PB7 / UART1_TX`

Source: the Grove Vision AI V2 circuit diagram PDF linked from the wiki’s Resources section ([“Circuit Diagram”](https://files.seeedstudio.com/wiki/grove-vision-ai-v2/Grove_Vision_AI_Module_V2_Circuit_Diagram.pdf)) and the wiki page itself ([Grove Vision AI V2 wiki](https://wiki.seeedstudio.com/grove_vision_ai_v2/)).

wiring
- GV2 TX (UART1_TX / PB7) → ESP32 RX (GPIO44)
- GV2 RX (UART1_RX / PB6) → ESP32 TX (GPIO43)
- GND ↔ GND

