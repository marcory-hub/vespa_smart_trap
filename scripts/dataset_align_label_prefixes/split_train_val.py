#!/usr/bin/env python3
"""
Split paired image + label files into train/ and val/ under images/ and labels/.

Only files directly in images/ and labels/ are considered (not already under
train/ or val/). Pairs share the same stem (e.g. foo.jpg and foo.txt).

Default split: 85% train, 15% val (rounded; for n>=2 at least one sample in val).
Shuffle is reproducible via --seed.

Dry-run by default; use --apply to move files. Use --copy to copy instead of move.
Back up the dataset before --apply.
"""

from __future__ import annotations

import argparse
import random
import shutil
import sys
from pathlib import Path

DEFAULT_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def _collect_pairs(
    images_dir: Path,
    labels_dir: Path,
    extensions: tuple[str, ...],
) -> tuple[list[tuple[str, Path, Path]], list[Path], list[Path]]:
    """
    Returns (pairs, orphan_images, orphan_labels).
    Each pair is (stem, image_path, label_path).
    """
    image_by_stem: dict[str, Path] = {}
    for path in sorted(images_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in extensions:
            continue
        stem = path.stem
        if stem in image_by_stem:
            raise ValueError(
                f"Duplicate image stem '{stem}': {image_by_stem[stem]} and {path}"
            )
        image_by_stem[stem] = path

    pairs: list[tuple[str, Path, Path]] = []
    orphan_images: list[Path] = []
    for stem, img_path in image_by_stem.items():
        label_path = labels_dir / f"{stem}.txt"
        if label_path.is_file():
            pairs.append((stem, img_path, label_path))
        else:
            orphan_images.append(img_path)

    label_paths = [
        p
        for p in labels_dir.iterdir()
        if p.is_file() and p.suffix.lower() == ".txt"
    ]
    paired_stems = {s for s, _i, _l in pairs}
    orphan_labels = [p for p in label_paths if p.stem not in paired_stems]

    return pairs, orphan_images, orphan_labels


def _split_sizes(n: int, train_ratio: float) -> tuple[int, int]:
    """Return (n_train, n_val) with n_train + n_val == n."""
    if n <= 0:
        return 0, 0
    if n == 1:
        return 1, 0
    n_train = int(round(n * train_ratio))
    n_train = min(max(1, n_train), n - 1)
    n_val = n - n_train
    return n_train, n_val


def _warn_nonempty_split_dirs(images_dir: Path, labels_dir: Path) -> list[str]:
    warnings: list[str] = []
    for sub in ("train", "val"):
        for base in (images_dir, labels_dir):
            d = base / sub
            if not d.is_dir():
                continue
            existing = [p for p in d.iterdir() if p.is_file()]
            if existing:
                warnings.append(
                    f"{d} already has {len(existing)} file(s); new files will be added."
                )
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split paired images/labels into train/ and val/ subfolders."
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        required=True,
        help="Folder containing images/ and labels/ (flat files in each).",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.85,
        help="Fraction of pairs for train (default: 0.85).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="RNG seed for shuffling pairs (default: 42).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Move or copy files (default is dry-run only).",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of moving them.",
    )
    parser.add_argument(
        "--ext",
        nargs="*",
        default=list(DEFAULT_IMAGE_EXTENSIONS),
        help=f"Image extensions to pair (default: {list(DEFAULT_IMAGE_EXTENSIONS)}).",
    )
    args = parser.parse_args()

    if not 0.0 < args.train_ratio < 1.0:
        print("ERROR: --train-ratio must be between 0 and 1.", file=sys.stderr)
        return 2

    extensions = tuple(e if e.startswith(".") else f".{e}" for e in args.ext)
    dataset_root = args.dataset_root.expanduser().resolve()
    images_dir = dataset_root / "images"
    labels_dir = dataset_root / "labels"

    if not images_dir.is_dir() or not labels_dir.is_dir():
        print(
            f"ERROR: need both {images_dir} and {labels_dir} as directories.",
            file=sys.stderr,
        )
        return 2

    try:
        pairs, orphan_images, orphan_labels = _collect_pairs(
            images_dir, labels_dir, extensions
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    n = len(pairs)
    n_train, n_val = _split_sizes(n, args.train_ratio)

    print(f"Dataset root: {dataset_root}")
    mode = "DRY-RUN"
    if args.apply:
        mode = "APPLY (copy)" if args.copy else "APPLY (move)"
    print(f"Mode: {mode}")
    print(f"Train ratio: {args.train_ratio}  seed: {args.seed}")
    print(f"Paired samples: {n}  ->  train: {n_train},  val: {n_val}")
    print()

    for w in _warn_nonempty_split_dirs(images_dir, labels_dir):
        print(f"Note: {w}")
    if orphan_images:
        print(f"Orphan images (no matching .txt in labels/): {len(orphan_images)}")
        for p in orphan_images[:20]:
            print(f"  {p.name}")
        if len(orphan_images) > 20:
            print(f"  ... and {len(orphan_images) - 20} more")
        print()
    if orphan_labels:
        print(f"Orphan labels (no matching image in images/): {len(orphan_labels)}")
        for p in orphan_labels[:20]:
            print(f"  {p.name}")
        if len(orphan_labels) > 20:
            print(f"  ... and {len(orphan_labels) - 20} more")
        print()

    if n == 0:
        print("No pairs to split.")
        return 0

    rng = random.Random(args.seed)
    stems_order = list(pairs)
    rng.shuffle(stems_order)

    train_pairs = stems_order[:n_train]
    val_pairs = stems_order[n_train:]

    def show_sample(name: str, plist: list[tuple[str, Path, Path]], limit: int = 8) -> None:
        print(f"{name} ({len(plist)} pairs), sample:")
        for stem, img, lab in plist[:limit]:
            print(f"  {img.name}  <->  {lab.name}")
        if len(plist) > limit:
            print(f"  ... ({len(plist) - limit} more)")
        print()

    show_sample("TRAIN", train_pairs)
    show_sample("VAL", val_pairs)

    if not args.apply:
        print("Re-run with --apply to create train/val folders and move or copy files.")
        return 0

    for sub in ("train", "val"):
        (images_dir / sub).mkdir(parents=True, exist_ok=True)
        (labels_dir / sub).mkdir(parents=True, exist_ok=True)

    transfer = shutil.copy2 if args.copy else shutil.move

    def do_batch(batch: list[tuple[str, Path, Path]], split: str) -> None:
        for _stem, img, lab in batch:
            transfer(img, images_dir / split / img.name)
            transfer(lab, labels_dir / split / lab.name)

    do_batch(train_pairs, "train")
    do_batch(val_pairs, "val")

    action = "Copied" if args.copy else "Moved"
    print(f"{action} {n_train} pair(s) to train/, {n_val} pair(s) to val/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
