(() => {
  const IMAGE_SECONDS = 4;

  const overlayTitle = document.getElementById("overlayTitle");
  const overlaySubtitle = document.getElementById("overlaySubtitle");
  const overlayHint = document.getElementById("overlayHint");
  const overlay = document.getElementById("overlay");
  const contentGrid = document.getElementById("contentGrid");
  const imageEl = document.getElementById("image");
  const imageLabel = document.getElementById("imageLabel");
  const cameraImage = document.getElementById("cameraImage");
  const cameraInferenceLabel = document.getElementById("cameraInferenceLabel");
  const setupBanner = document.getElementById("setupBanner");
  const pausedBanner = document.getElementById("pausedBanner");
  const pageQuery = new URLSearchParams(window.location.search);

  function isTruthyParam(value) {
    if (typeof value !== "string") return false;
    return ["1", "true", "yes", "on"].includes(value.trim().toLowerCase());
  }

  const queryLockedBenchmark =
    isTruthyParam(pageQuery.get("locked")) || isTruthyParam(pageQuery.get("benchmark"));
  const DEFAULT_MANIFEST_SEED = "42";
  const querySeed = pageQuery.get("seed");
  const manifestSeed =
    typeof querySeed === "string" && /^-?\d+$/.test(querySeed.trim())
      ? querySeed.trim()
      : DEFAULT_MANIFEST_SEED;

  const IMAGE_WIDTH_MIN_CM = 4.0;
  const IMAGE_WIDTH_DEFAULT_CM = 8.0;
  const IMAGE_WIDTH_SETUP_CM = 30.0;

  function setHidden(el, hidden) {
    if (!el) return;
    el.classList.toggle("is-hidden", hidden);
  }

  function nowIso() {
    return new Date().toISOString();
  }

  async function fetchJson(path) {
    const res = await fetch(path, { cache: "no-store" });
    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      throw new Error(`Expected JSON from ${path}, got: ${text.slice(0, 200)}`);
    }
    if (!res.ok) {
      const msg = data && data.error ? data.error : `Request failed: ${res.status}`;
      const err = new Error(msg);
      err.data = data;
      throw err;
    }
    return data;
  }

  async function postJson(path, payload) {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`POST ${path} failed: ${res.status} ${text.slice(0, 200)}`);
    }
  }

  function logControlEvent(eventName) {
    if (!state.runStarted) return;
    postJson("/log/control", {
      event: eventName,
      at_iso: nowIso(),
    }).catch(() => {
      // Keep slideshow resilient even if control audit logging fails.
    });
  }

  function showError(title, details) {
    setHidden(imageEl, true);
    setHidden(imageLabel, true);
    setHidden(contentGrid, true);
    setHidden(pausedBanner, true);
    setHidden(overlay, false);
    setHidden(setupBanner, true);
    overlayTitle.textContent = title;
    overlaySubtitle.textContent = details || "";
    overlayHint.textContent = "";
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function normalizeImageWidthCm(rawValue) {
    const parsed = Number.parseFloat(rawValue);
    if (!Number.isFinite(parsed)) return IMAGE_WIDTH_DEFAULT_CM;
    return Math.max(IMAGE_WIDTH_MIN_CM, parsed);
  }

  function applyImageWidthCm(widthCm) {
    const normalized = normalizeImageWidthCm(widthCm);
    document.documentElement.style.setProperty("--image-width-cm", `${normalized.toFixed(1)}cm`);
  }

  function shortTokenFromFilename(filename) {
    if (typeof filename !== "string") return "";
    const stem = filename.replace(/\.[^.]+$/, "");
    const match = /^([a-zA-Z]{3})_([a-zA-Z]{3})/.exec(stem);
    if (!match) return stem;
    return `${match[1].toLowerCase()}_${match[2]}`;
  }

  const state = {
    manifest: null,
    currentIndex: -1,
    paused: false,
    runStarted: false,
    stopping: false,
    lockedBenchmark: queryLockedBenchmark,
    currentImageShortToken: "",
    latestInferenceLabel: "",
    autoSizeByLabels: true,
    inSetupPhase: false,
    setupConfirmed: false,
  };

  applyImageWidthCm(IMAGE_WIDTH_DEFAULT_CM);

  function updatePausedUi() {
    setHidden(pausedBanner, !state.paused);
  }

  function updateImageLabel() {
    const left = state.currentImageShortToken || "";
    imageLabel.textContent = left;
  }

  function updateCameraInferenceLabel() {
    cameraInferenceLabel.textContent = state.latestInferenceLabel || "waiting_for_gv2";
  }

  function confirmSetupIfActive(source) {
    if (!state.inSetupPhase || state.setupConfirmed) return false;
    state.setupConfirmed = true;
    logControlEvent(`setup_confirmed_${source}`);
    return true;
  }

  function formatInferenceLabel(payload) {
    if (!payload || typeof payload !== "object") return "";
    if (typeof payload.species !== "string" || !payload.species) return "";
    const confidence = Number.parseFloat(payload.confidence);
    if (!Number.isFinite(confidence)) return "";
    return `${payload.species}_${confidence.toFixed(2)}`;
  }

  async function pollLatestInferenceWhileRunning() {
    while (state.runStarted && !state.stopping) {
      try {
        const response = await fetchJson("/api/latest_inference");
        const latest = response ? response.latest_inference : null;
        state.latestInferenceLabel = formatInferenceLabel(latest);
        updateCameraInferenceLabel();
      } catch {
        // Ignore transient poll errors.
      }
      await sleep(200);
    }
  }

  function applyCameraFrame(payload) {
    if (!payload || typeof payload !== "object") return;
    const raw = payload.image_base64;
    if (typeof raw !== "string" || !raw) return;
    if (raw.startsWith("data:image/")) {
      cameraImage.src = raw;
      return;
    }
    cameraImage.src = `data:image/jpeg;base64,${raw}`;
  }

  async function pollLatestCameraFrameWhileRunning() {
    while (state.runStarted && !state.stopping) {
      try {
        const response = await fetchJson("/api/latest_camera_frame");
        applyCameraFrame(response ? response.latest_camera_frame : null);
      } catch {
        // Ignore transient poll errors.
      }
      await sleep(200);
    }
  }

  async function waitWhilePaused() {
    while (state.paused && !state.stopping) {
      await sleep(100);
    }
  }

  async function startRun() {
    state.stopping = false;

    overlayTitle.textContent = "Preparing…";
    overlaySubtitle.textContent = "";
    overlayHint.textContent = "";
    setHidden(overlay, true);
    setHidden(contentGrid, true);
    setHidden(setupBanner, true);
    setHidden(imageEl, false);
    setHidden(imageLabel, false);
    updatePausedUi();

    const startInfo = await fetchJson("/start");
    const manifestQuery = new URLSearchParams();
    manifestQuery.set("shuffle", "1");
    manifestQuery.set("seed", manifestSeed);
    const manifest = await fetchJson(`/manifest.json?${manifestQuery.toString()}`);

    state.manifest = manifest;
    state.currentIndex = -1;
    state.runStarted = true;
    state.lockedBenchmark = Boolean(startInfo.locked_benchmark) || queryLockedBenchmark;
    state.latestInferenceLabel = "";
    updateCameraInferenceLabel();
    state.autoSizeByLabels = true;
    pollLatestInferenceWhileRunning().catch(() => {
      // Ignore poll loop errors.
    });
    pollLatestCameraFrameWhileRunning().catch(() => {
      // Ignore poll loop errors.
    });
    if (!Array.isArray(state.manifest.items) || state.manifest.items.length === 0) {
      throw new Error("Manifest contains no images");
    }

    // Setup preview screen: example image left (max size), live camera right.
    state.currentIndex = 0;
    if (state.manifest.items.length > 0) {
      await showItem(state.manifest.items[0], false);
      applyImageWidthCm(IMAGE_WIDTH_SETUP_CM);
    }
    setHidden(contentGrid, false);
    setHidden(setupBanner, false);
    state.inSetupPhase = true;
    state.setupConfirmed = false;
    while (!state.setupConfirmed && !state.stopping) {
      setupBanner.textContent =
        "Setup: adjust camera distance so full example image is captured, then press Space/Enter or click to start.";
      await sleep(50);
    }
    state.inSetupPhase = false;
    if (state.stopping) return;

    setHidden(overlay, true);
    setHidden(setupBanner, true);
    setHidden(contentGrid, false);
    setHidden(imageEl, false);
    setHidden(imageLabel, false);
    state.currentIndex = -1;

    // Slideshow
    while (!state.stopping) {
      await showNextImage();
      const shownStart = Date.now();
      while (Date.now() - shownStart < IMAGE_SECONDS * 1000 && !state.stopping) {
        await waitWhilePaused();
        await sleep(25);
      }
    }
  }

  async function showNextImage() {
    if (!state.manifest || !Array.isArray(state.manifest.items)) {
      throw new Error("Manifest not loaded");
    }
    state.currentIndex += 1;
    if (state.currentIndex >= state.manifest.items.length) {
      state.currentIndex = 0;
    }
    const item = state.manifest.items[state.currentIndex];
    await showItem(item, true);
  }

  async function showItem(item, logShown) {
    const label = shortTokenFromFilename(item.filename);
    state.currentImageShortToken = label;
    const displayWidthCm = Number.parseFloat(item.display_width_cm);
    if (Number.isFinite(displayWidthCm)) {
      applyImageWidthCm(displayWidthCm);
    }

    updateImageLabel();
    imageEl.src = item.url;

    if (logShown) {
      await postJson("/log", {
        index: item.index,
        filename: item.filename,
        viewpoint: item.viewpoint,
        species: item.species,
        shown_at_iso: nowIso(),
      });
    }
  }

  function togglePause() {
    if (state.lockedBenchmark) {
      logControlEvent("blocked_pause_toggle");
      return;
    }
    logControlEvent(state.paused ? "resume" : "pause");
    state.paused = !state.paused;
    updatePausedUi();
  }

  function requestNext() {
    if (state.lockedBenchmark) {
      logControlEvent("blocked_manual_next");
      return;
    }
    logControlEvent("manual_next");
    // Next should work even while paused, so user can step through.
    showNextImage().catch((e) => showError("Error", String(e && e.message ? e.message : e)));
  }

  function restart() {
    if (state.lockedBenchmark) {
      logControlEvent("blocked_restart");
      return;
    }
    logControlEvent("restart");
    state.stopping = true;
    state.paused = false;
    updatePausedUi();
    // Allow the loop to unwind, then start again.
    setTimeout(() => startRun().catch((e) => showError("Error", String(e && e.message ? e.message : e))), 50);
  }

  document.addEventListener("keydown", (ev) => {
    if (ev.code === "Space") {
      ev.preventDefault();
      if (confirmSetupIfActive("space")) {
        return;
      }
      togglePause();
      return;
    }
    if (ev.code === "Enter" || ev.code === "NumpadEnter") {
      if (confirmSetupIfActive("enter")) {
        ev.preventDefault();
      }
      return;
    }
    if (ev.code === "ArrowRight") {
      ev.preventDefault();
      requestNext();
      return;
    }
    if (ev.key === "r" || ev.key === "R") {
      ev.preventDefault();
      restart();
      return;
    }
  });

  setupBanner.addEventListener("pointerdown", () => {
    confirmSetupIfActive("setup_banner_click");
  });
  contentGrid.addEventListener("pointerdown", () => {
    confirmSetupIfActive("content_click");
  });

  startRun().catch((e) => {
    const msg = e && e.message ? e.message : String(e);
    let details = "";
    if (e && e.data && e.data.bad_files) {
      details = JSON.stringify(e.data, null, 2);
    }
    showError(msg, details);
  });
})();
