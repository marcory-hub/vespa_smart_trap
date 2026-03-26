## Image slider web (seeded)

### What it does
- Serves a local webpage that:
  - shows a 20 second black calibration screen with text + a 10 cm bar
  - then shows all `data/test/images/*.jpg` images for 2 seconds each
  - uses a deterministic shuffled order (seed 42)
  - overlays `#index filename`
  - logs each shown image to a CSV file

### Run
From the repo root:

```bash
python3 "scripts/image_slider_web/server.py" 8000
```

Then open `http://127.0.0.1:8000/` in your browser.

### Controls
- **Space**: pause / resume
- **Right Arrow**: next image
- **R**: restart from the intro screen

### Outputs
- Logs are written to `scripts/image_slider_web/outputs/<yyyy-mm-dd_HHMMSS>/run_log.csv`.

# Image slider (local web)

Tiny local server + minimal webpage scaffold.

## Run

From repo root:

```bash
python3 scripts/image_slider_web/server.py --port 8008
```

Then open `http://127.0.0.1:8008/`.

## What it serves

- `GET /` -> `scripts/image_slider_web/static/index.html`
- `GET /api/manifest` -> deterministic shuffled list from `data/test/images`
- `GET /images/<filename>` -> raw image bytes

