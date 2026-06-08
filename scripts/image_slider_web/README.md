## Image slider web

### What it does
- Serves a local webpage that:
  - shows a 20 second calibration screen with a 10 cm reference bar
  - then shows `data/test/images/*.jpg` for 4 seconds each
- Default image order is deterministic (sorted filenames).
- Browser now requests shuffled order by default for testing (`seed=42` unless overridden).
- Optional deterministic shuffle control is available via URL query (`?shuffle=1&seed=42`).
- Overlays `#index filename` and logs shown images into a per-run CSV.

### Run
From the repo root:

```bash
python3 scripts/image_slider_web/server.py --port 8000
```

Then open `http://127.0.0.1:8000/`.

For strict benchmark runs (manual controls disabled):

```bash
python3 scripts/image_slider_web/server.py --port 8000 --locked-benchmark
```

### Controls
- Default mode:
  - **Space**: pause / resume
  - **Right Arrow**: next image
  - **R**: restart from intro
- Locked benchmark mode:
  - manual controls are blocked and logged to `control_events.jsonl`
- Label overlay shows `vvv_sss | sss_confidence` when live inference updates are received.
- Display size is auto-scaled per image from label-derived bbox statistics and species average body lengths.
- UI uses a side-by-side layout: slideshow (left) and latest GV2 camera frame (right).
- Inference text (`sss_confidence`) is shown on top of the camera pane.
- Before scoring starts, a 20s setup preview shows one max-size example image (left) with live camera (right) so camera distance can be adjusted.

### Outputs
- Per run: `scripts/image_slider_web/outputs/<yyyy-mm-dd_HHMMSS>/`
  - `run_log.csv`: image shown events
  - `run_meta.json`: run metadata (including lock mode)
  - `control_events.jsonl`: control-event audit trail
  - `inference_events.jsonl`: live inference updates (`species`, `confidence`, `at_iso`)
- Cross-run linkage ledger: `scripts/image_slider_web/runs_ledger.jsonl`
  - one JSON line per run with `run_id` and repo-relative paths to run artifacts

### API
- `GET /` -> `scripts/image_slider_web/static/index.html`
- `GET /api/manifest` or `GET /manifest.json` -> image manifest
- Manifest items include `display_width_cm` for per-image autoscaling.
- `GET /start` -> initializes a run folder and returns run metadata
- `POST /log` -> appends shown-image rows to `run_log.csv`
- `POST /log/control` -> appends control events to `control_events.jsonl`
- `POST /log/inference` -> appends inference updates to `inference_events.jsonl`
- `GET /api/latest_inference` -> returns latest inference payload for UI label feedback
- `POST /log/camera_frame` -> updates latest GV2 camera frame for UI preview
- `GET /api/latest_camera_frame` -> returns latest camera frame payload
- `GET /images/<filename>` -> raw image bytes

