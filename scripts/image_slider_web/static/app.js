(() => {
  const INTRO_SECONDS = 20;
  const IMAGE_SECONDS = 2;

  const overlayTitle = document.getElementById("overlayTitle");
  const overlaySubtitle = document.getElementById("overlaySubtitle");
  const overlayHint = document.getElementById("overlayHint");
  const overlay = document.getElementById("overlay");
  const calibration = document.getElementById("calibration");
  const imageEl = document.getElementById("image");
  const imageLabel = document.getElementById("imageLabel");
  const pausedBanner = document.getElementById("pausedBanner");

  function setHidden(el, hidden) {
    if (!el) return;
    el.classList.toggle("is-hidden", hidden);
    if (el === calibration) {
      el.setAttribute("aria-hidden", hidden ? "true" : "false");
    }
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

  function showError(title, details) {
    setHidden(imageEl, true);
    setHidden(imageLabel, true);
    setHidden(pausedBanner, true);
    setHidden(overlay, false);
    setHidden(calibration, true);
    overlayTitle.textContent = title;
    overlaySubtitle.textContent = details || "";
    overlayHint.textContent = "";
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  const state = {
    manifest: null,
    currentIndex: -1,
    paused: false,
    runStarted: false,
    stopping: false,
  };

  function updatePausedUi() {
    setHidden(pausedBanner, !state.paused);
  }

  async function waitWhilePaused() {
    while (state.paused && !state.stopping) {
      await sleep(100);
    }
  }

  async function startRun() {
    state.stopping = false;

    overlayTitle.textContent = "Starting…";
    overlaySubtitle.textContent = "";
    overlayHint.textContent = "Controls: Space pause/resume • Right Arrow next • R restart";
    setHidden(overlay, false);
    setHidden(calibration, true);
    setHidden(imageEl, true);
    setHidden(imageLabel, true);
    updatePausedUi();

    const startInfo = await fetchJson("/start");
    const manifest = await fetchJson("/manifest.json");

    state.manifest = manifest;
    state.currentIndex = -1;
    state.runStarted = true;

    // Intro screen
    overlayTitle.textContent = startInfo.intro_text || "Calibration";
    overlaySubtitle.textContent =
      "Resize the browser image so the bar below measures exactly 10 cm (use a ruler). " +
      "Then place the camera 10 cm from the screen.";
    setHidden(calibration, false);
    const introStart = Date.now();
    while (Date.now() - introStart < INTRO_SECONDS * 1000 && !state.stopping) {
      await waitWhilePaused();
      const elapsedSeconds = Math.floor((Date.now() - introStart) / 1000);
      const remainingSeconds = Math.max(0, INTRO_SECONDS - elapsedSeconds);
      overlayHint.textContent =
        `Calibration starts in ${remainingSeconds}s. ` +
        "Controls: Space pause/resume • Right Arrow next • R restart";
      await sleep(50);
    }
    if (state.stopping) return;

    setHidden(overlay, true);
    setHidden(calibration, true);
    setHidden(imageEl, false);
    setHidden(imageLabel, false);

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
    const label = `#${String(item.index).padStart(4, "0")} ${item.filename}`;

    imageLabel.textContent = label;
    imageEl.src = item.url;

    await postJson("/log", {
      index: item.index,
      filename: item.filename,
      viewpoint: item.viewpoint,
      species: item.species,
      shown_at_iso: nowIso(),
    });
  }

  function togglePause() {
    state.paused = !state.paused;
    updatePausedUi();
  }

  function requestNext() {
    // Next should work even while paused, so user can step through.
    showNextImage().catch((e) => showError("Error", String(e && e.message ? e.message : e)));
  }

  function restart() {
    state.stopping = true;
    state.paused = false;
    updatePausedUi();
    // Allow the loop to unwind, then start again.
    setTimeout(() => startRun().catch((e) => showError("Error", String(e && e.message ? e.message : e))), 50);
  }

  document.addEventListener("keydown", (ev) => {
    if (ev.code === "Space") {
      ev.preventDefault();
      togglePause();
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

  startRun().catch((e) => {
    const msg = e && e.message ? e.message : String(e);
    let details = "";
    if (e && e.data && e.data.bad_files) {
      details = JSON.stringify(e.data, null, 2);
    }
    showError(msg, details);
  });
})();
