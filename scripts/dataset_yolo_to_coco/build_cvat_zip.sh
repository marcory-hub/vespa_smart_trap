#!/usr/bin/env bash
# Builds CVAT YOLO import structure from images/train + labels/train.
# Run from dataset_vespa_2026-02_cvat_merged_yolo. Creates obj_train_data and train.txt.

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
IMG_DIR="$ROOT/images/train"
LBL_DIR="$ROOT/labels/train"
OUT_DIR="$ROOT/obj_train_data"
TRAIN_TXT="$ROOT/train.txt"

if [[ ! -d "$IMG_DIR" ]] || [[ ! -d "$LBL_DIR" ]]; then
  echo "Missing images/train or labels/train"
  exit 1
fi

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

echo "Linking images and labels into obj_train_data..."
for img in "$IMG_DIR"/*.jpg; do
  [[ -f "$img" ]] || continue
  base=$(basename "$img" .jpg)
  cp "$img" "$OUT_DIR/$base.jpg"
  lbl="$LBL_DIR/$base.txt"
  if [[ -f "$lbl" ]]; then
    cp "$lbl" "$OUT_DIR/$base.txt"
  fi
done

echo "Writing train.txt..."
find obj_train_data -maxdepth 1 -name '*.jpg' -print | sort > "$TRAIN_TXT"
echo "Done. obj_train_data and train.txt ready. Zip from this directory with:"
echo "  zip -r ../dataset_cvat_yolo.zip obj.data obj.names obj_train_data train.txt -x '*.DS_Store'"
