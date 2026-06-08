# Presentations

Reveal.js decks for talks and show-and-tell sessions. One subfolder per deck.

## Decks

| Deck | Path | Public URL |
| :--- | :--- | :--- |
| Cursor Show & Tell (2026-06) | [`edge-ai-cursor-2026-06/`](edge-ai-cursor-2026-06/) | https://marcory-hub.github.io/vespa_smart_trap/edge-ai-cursor-2026-06/ |

## Local preview

Reveal loads `slides.md` over HTTP; open a local server from the deck folder:

```bash
cd presentations/edge-ai-cursor-2026-06
python3 -m http.server 8000
```

Open http://localhost:8000

Press `F` for fullscreen, arrow keys to advance.

## GitHub Pages (one-time setup)

1. Repo **Settings → Pages → Build and deployment**
2. Set **Source** to **GitHub Actions** (not "Deploy from a branch")
3. Push to `main`; workflow [`.github/workflows/deploy-presentations.yml`](../.github/workflows/deploy-presentations.yml) publishes the `presentations/` tree

Workflow runs when `presentations/**` or the workflow file changes.

## Add a new deck

1. Create `presentations/<deck-slug>/` with `index.html`, `slides.md`, and `assets/` as needed
2. Copy structure from `edge-ai-cursor-2026-06/index.html`
3. Separate slides with `---` in `slides.md`
4. Add a row to the table above

Naming: kebab-case slug, optional date prefix (e.g. `edge-ai-cursor-2026-06`).
