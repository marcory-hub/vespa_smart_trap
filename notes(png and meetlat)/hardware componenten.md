
**One-line purpose:** index list of hardware components november 2025
**Short summary:** gv2, lilygo, custom pcb
**Agent:** needs update

---


2025-11-14

## Hardware Componenten
### Current phase
1. **Grove Vision AI V2** - AI inferentie
2. **I2C Hub** - Centrale I2C bus
3. **Relay Module** - Actuator controle

### Later in the project
1. **LILYGO T-SIM7080-S3** - Communicatie en controle
2. **Solar Charger** - Power management
3. **18650 Battery** - Portable power

### Connections

- **I2C Bus**: LILYGO ↔ I2C Hub ↔ Grove Vision AI V2 + Relay (trap mechanism)
- **Power**: Solar/USB → Charger → Battery → LILYGO


### 1. LILYGO T-SIM7080-S3 + I2C Hub

![[acc Vespa Smart Trap 2.png]]

**Componenten:**
- LILYGO T-SIM7080-S3 development board
- I2C Hub (breadboard) voor centrale bus
- Grove Vision AI V2 (via I2C)
- Relay module (via I2C)

**Functie:**
- Communicatie (GPS, LTE-M, WiFi)
- AI detectie verwerking
- Actuator controle (relay)

### 2. Solar Charger

![[acc Vespa Smart Trap-1.png]]

**Componenten:**
- Solar panel met USB output
- Battery charger module
- 18650 batterij

**Functie:**
- Power management
- Battery charging
- Portable operation

### 3. Relay Module

![[acc Vespa Smart Trap-2.png]]

**Componenten:**
- Relay module (5V, optocoupler isolated)
- I2C interface

**Functie:**
- Trap mechanisme controle
- Alarm systeem
- Actuator switching
