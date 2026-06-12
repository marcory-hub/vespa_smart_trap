# Learning record format

Teaching equivalent of ADRs: steers zone of proximal development.

## Template

```md
# {Short title}

{1-3 sentences: what was learned or established, and why it matters for future sessions.}
```

## Optional (only when useful)

- **Status** frontmatter: `active | superseded by LR-NNNN`
- **Evidence**: question answered, exercise done, prior experience cited
- **Implications**: what this unlocks or rules out next

## Numbering

Scan `teaching/learning-records/` for highest `NNNN`; increment.

## When to write

1. User **demonstrates** non-trivial understanding (can use concept correctly).
2. User discloses **prior knowledge** ("I already know X") with depth claimed.
3. **Misconception corrected** (high value for related topics).
4. **Mission shifted**; cross-link `MISSION.md` and update it.

## Does not qualify

- Material only covered, not demonstrated
- Term already in `GLOSSARY.md` (do not duplicate)
- Session activity logs

## Supersession

Mark old record `Status: superseded by LR-NNNN`; do not delete history.
