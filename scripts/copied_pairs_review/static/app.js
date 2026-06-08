const splitFilter = document.getElementById("splitFilter");
const classFilter = document.getElementById("classFilter");
const showFilter = document.getElementById("showFilter");
const counter = document.getElementById("counter");
const imageWrap = document.querySelector(".image-wrap");
const image = document.getElementById("image");
const overlay = document.getElementById("overlay");
const meta = document.getElementById("meta");
const status = document.getElementById("status");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const keepBtn = document.getElementById("keepBtn");
const removeBtn = document.getElementById("removeBtn");
const applyBtn = document.getElementById("applyBtn");

let items = [];
let keptStems = new Set();
let currentIndex = 0;
let removeCount = 0;
let keptCount = 0;
let totalCount = 0;
const boxCache = new Map();
const preload = new Image();
const CLASS_NAMES = ["vcra", "vvel"];
const CLASS_COLORS = ["#4ade80", "#60a5fa"];

function isKept(stem) {
  return keptStems.has(stem);
}

function syncCounts(payload) {
  keptCount = payload.kept_count ?? keptStems.size;
  removeCount = payload.remove_count ?? totalCount - keptCount;
  totalCount = payload.total ?? totalCount;
  if (payload.kept_stems) {
    keptStems = new Set(payload.kept_stems);
  }
}

function updateHeader() {
  const item = items[currentIndex];
  const keptHere = item ? isKept(item.stem) : false;
  const filterNote = showFilter.value ? ` (${showFilter.options[showFilter.selectedIndex].text})` : "";
  counter.textContent = items.length
    ? `${currentIndex + 1} / ${items.length}${filterNote} · kept ${keptCount} · remove ${removeCount} · total ${totalCount}`
    : "No items";
  applyBtn.textContent = `Delete all except kept (${keptCount} kept, ${removeCount} remove)`;
  imageWrap.classList.toggle("is-keep", keptHere);
  imageWrap.classList.toggle("is-remove", item && !keptHere);
  keepBtn.textContent = keptHere ? "Keep (K) ✓" : "Keep (K)";
}

async function loadSession() {
  const params = new URLSearchParams();
  if (splitFilter.value) params.set("split", splitFilter.value);
  if (classFilter.value) params.set("class", classFilter.value);
  if (showFilter.value) params.set("show", showFilter.value);
  const response = await fetch(`/api/session?${params.toString()}`);
  const payload = await response.json();
  items = payload.items || [];
  keptStems = new Set(payload.kept_stems || []);
  syncCounts(payload);
  currentIndex = Math.min(currentIndex, Math.max(0, items.length - 1));
  if (items.length > 0) showCurrent();
  else {
    image.removeAttribute("src");
    meta.textContent = "No items for this filter.";
    clearOverlay();
    updateHeader();
  }
}

function preloadAdjacent() {
  if (!items.length) return;
  const next = items[(currentIndex + 1) % items.length];
  if (next) preload.src = next.image_url;
}

function showCurrent() {
  const item = items[currentIndex];
  if (!item) return;
  image.src = item.image_url;
  meta.textContent = `${item.split} / ${item.class} — ${isKept(item.stem) ? "KEEP" : "REMOVE (default)"}`;
  updateHeader();
  preloadAdjacent();
  image.onload = () => drawBoxes(item);
}

function clearOverlay() {
  overlay.getContext("2d").clearRect(0, 0, overlay.width, overlay.height);
}

async function drawBoxes(item) {
  clearOverlay();
  let boxes = boxCache.get(item.label_url);
  if (!boxes) {
    const labelPath = item.label_url.replace(/^\/media\//, "media/");
    const response = await fetch(`/api/labels?path=${encodeURIComponent(labelPath)}`);
    const payload = await response.json();
    boxes = payload.boxes || [];
    boxCache.set(item.label_url, boxes);
  }
  overlay.width = image.clientWidth;
  overlay.height = image.clientHeight;
  const ctx = overlay.getContext("2d");
  ctx.lineWidth = 2;
  ctx.font = "14px system-ui";
  boxes.forEach((box) => {
    const w = box.width * overlay.width;
    const h = box.height * overlay.height;
    const x = box.x_center * overlay.width - w / 2;
    const y = box.y_center * overlay.height - h / 2;
    const color = CLASS_COLORS[box.class_id] || "#fbbf24";
    ctx.strokeStyle = color;
    ctx.strokeRect(x, y, w, h);
    ctx.fillStyle = color;
    ctx.fillText(CLASS_NAMES[box.class_id] || String(box.class_id), x + 4, y + 16);
  });
}

function dropCurrentFromView() {
  items.splice(currentIndex, 1);
  if (currentIndex >= items.length) {
    currentIndex = Math.max(0, items.length - 1);
  }
}

async function setKeep(keep) {
  const item = items[currentIndex];
  if (!item) return;

  if (keep === isKept(item.stem)) {
    step(1);
    return;
  }

  const response = await fetch("/api/keep/set", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ stem: item.stem, keep }),
  });
  if (!response.ok) {
    status.textContent = "Save failed — check server.";
    return;
  }
  const payload = await response.json();
  syncCounts(payload);
  status.textContent = keep ? `Kept (${keptCount} total)` : `Remove (${removeCount} total)`;

  if ((showFilter.value === "remove" && keep) || (showFilter.value === "keep" && !keep)) {
    dropCurrentFromView();
    if (items.length > 0) showCurrent();
    else {
      image.removeAttribute("src");
      meta.textContent = "No items left in this filter.";
      clearOverlay();
      updateHeader();
    }
    return;
  }
  step(1);
}

function step(delta) {
  if (!items.length) return;
  currentIndex = (currentIndex + delta + items.length) % items.length;
  showCurrent();
}

async function applyRemovals() {
  if (removeCount === 0) {
    status.textContent = "Nothing to remove — all items are marked keep.";
    return;
  }
  const ok = window.confirm(
    `WARNING: Irreversible.\nDelete ${removeCount} pair(s) from BOTH dataset folders?\nKeep ${keptCount} top-down pair(s).`
  );
  if (!ok) return;
  const response = await fetch("/api/apply-removals", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dry_run: false }),
  });
  const payload = await response.json();
  status.textContent =
    `Deleted ${payload.stems} pair(s) (${payload.files_removed} files). ` +
    `Kept ${payload.kept}. Missing on disk: ${payload.files_missing}.`;
  if (!payload.errors?.length) await loadSession();
}

splitFilter.addEventListener("change", () => {
  currentIndex = 0;
  loadSession();
});
classFilter.addEventListener("change", () => {
  currentIndex = 0;
  loadSession();
});
showFilter.addEventListener("change", () => {
  currentIndex = 0;
  loadSession();
});
prevBtn.addEventListener("click", () => step(-1));
nextBtn.addEventListener("click", () => step(1));
keepBtn.addEventListener("click", () => setKeep(true));
removeBtn.addEventListener("click", () => step(1));
applyBtn.addEventListener("click", applyRemovals);

window.addEventListener("keydown", (event) => {
  if (event.target.matches("input, textarea, select")) return;
  if (event.key === "ArrowLeft") step(-1);
  if (event.key === "ArrowRight" || event.key === " ") {
    event.preventDefault();
    step(1);
  }
  if (event.key === "k" || event.key === "K") setKeep(true);
  if (event.key === "r" || event.key === "R") step(1);
});

window.addEventListener("resize", () => {
  if (items[currentIndex]) drawBoxes(items[currentIndex]);
});

loadSession();
