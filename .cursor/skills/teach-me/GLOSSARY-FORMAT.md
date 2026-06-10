# GLOSSARY.md format

Canonical language for this teaching workspace. Lessons and learning records use these terms.

## Structure

```md
# {Topic} Glossary

{One or two sentences: what domain this glossary covers.}

## Terms

**int8_vela.tflite**:
Full-integer quantized TFLite after Arm VELA compile for Himax GV2 SRAM.
_Avoid_: int8.tflite, plain tflite

**INVOKE**:
WE2 JSON serial message name carrying one inference result from GV2 firmware.
_Avoid_: detection packet, inference blob
```

## Rules

- **Add a term only when the user understands it.** Record compressed knowledge, not a dictionary to learn from cold.
- **Be opinionated.** Pick one term; list loose synonyms under `_Avoid_`.
- **Definitions tight.** One or two sentences; what it IS, not full procedure.
- **Use glossary terms inside other definitions** once promoted.
- **Subheadings** when clusters emerge (e.g. `## Hardware`, `## Training`).
- **Flag ambiguities.** "In this workspace, UART means GV2 USB debug serial unless noted as T-SIM link."
- **Revise in place** when understanding deepens.

Do not duplicate `notes/` SoT tables; glossary is teaching vocabulary, not project pinouts.
