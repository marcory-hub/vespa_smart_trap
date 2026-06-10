# RESOURCES.md format

Curated trusted sources. Draw lesson facts from here and cited links, not parametric guesses.

## Structure

```md
# {Topic} Resources

## Knowledge

- [GV2 flashing — repo README](../../README.md)
  Operator steps for xmodem flash. Use for: flash workflow teaching.
- [Seeed Colab notebooks](https://github.com/marcory-hub/Seeed_Grove_Vision_AI_Module_V2)
  Train/quant SoT. Use for: Colab cell walkthroughs after `@sync-colab-notebooks`.

## Wisdom (Communities)

- [Forum or community name](https://example.com)
  When to use: real-world troubleshooting, not primary SoT.

## Gaps

- {Area mission needs but no trusted resource yet}
```

## Rules

- **High-trust only.** Primary sources, vendor docs, peer-reviewed work, moderated communities.
- **Annotate every entry.** One line: what it covers, when to reach for it.
- **Knowledge / Wisdom** groups mirror teach philosophy.
- **`## Gaps`** when mission needs coverage you lack.
- **Prune** wrong or shallow entries.
- **Record opt-out** if user declines communities.

For this repo: prefer `notes/`, `README.md`, `colab-notebooks/` after sync over generic web summaries.
