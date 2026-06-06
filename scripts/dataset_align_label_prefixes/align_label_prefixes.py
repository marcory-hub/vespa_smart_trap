#!/usr/bin/env python3
"""
Align label .txt filenames with image stems when images use top_/oth_ prefixes.

For each label stem L, looks for exactly one image among:
  images/top_L.<ext>, images/oth_L.<ext>
If the label stem already matches an image stem (labels/<S>.txt and images/<S>.*), no change.

Dry-run by default; use --apply to rename. Back up labels/ before --apply.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_PREFIXES = ("top_", "oth_")
DEFAULT_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


@dataclass(frozen=True)
class PlannedRename:
    source: Path
    target: Path
    image_match: Path


def _collect_image_stems(images_dir: Path, extensions: tuple[str, ...]) -> dict[str, Path]:
    """Map image stem -> path (duplicate stems with different ext are an error)."""
    stems: dict[str, Path] = {}
    for path in sorted(images_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in extensions:
            continue
        stem = path.stem
        if stem in stems:
            raise ValueError(
                f"Duplicate image stem '{stem}': {stems[stem]} and {path}. "
                "Resolve manually before running this tool."
            )
        stems[stem] = path
    return stems


def _find_prefix_matches(
    label_stem: str,
    images_dir: Path,
    prefixes: tuple[str, ...],
    extensions: tuple[str, ...],
) -> list[tuple[str, str, Path]]:
    """Return list of (prefix, ext, image_path) for each matching image file."""
    matches: list[tuple[str, str, Path]] = []
    for prefix in prefixes:
        for ext in extensions:
            candidate = images_dir / f"{prefix}{label_stem}{ext}"
            if candidate.is_file():
                matches.append((prefix, ext, candidate))
    return matches


def plan_renames(
    labels_dir: Path,
    images_dir: Path,
    prefixes: tuple[str, ...],
    extensions: tuple[str, ...],
) -> tuple[
    list[PlannedRename],
    list[Path],
    list[Path],
    list[tuple[Path, list[tuple[str, str, Path]]]],
    list[tuple[Path, Path]],
]:
    """
    Returns:
      planned: renames to perform (source != target)
      skipped_aligned: label files already matching an image stem
      orphans: no image for stem and no unique prefixed candidate
      ambiguous: (label_path, matches) when more than one image matches
      collisions: (source, target) when target exists and is not source
    """
    image_stems = _collect_image_stems(images_dir, extensions)
    planned: list[PlannedRename] = []
    skipped_aligned: list[Path] = []
    orphans: list[Path] = []
    ambiguous: list[tuple[Path, list[tuple[str, str, Path]]]] = []
    collisions: list[tuple[Path, Path]] = []

    label_paths = sorted(
        p for p in labels_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"
    )

    for label_path in label_paths:
        stem = label_path.stem
        if stem in image_stems:
            skipped_aligned.append(label_path)
            continue

        matches = _find_prefix_matches(stem, images_dir, prefixes, extensions)
        if len(matches) == 0:
            orphans.append(label_path)
            continue
        if len(matches) > 1:
            ambiguous.append((label_path, matches))
            continue

        prefix, _ext, image_path = matches[0]
        target = labels_dir / f"{prefix}{stem}.txt"
        if label_path == target:
            skipped_aligned.append(label_path)
            continue
        if target.exists() and target.resolve() != label_path.resolve():
            collisions.append((label_path, target))
            continue
        planned.append(
            PlannedRename(source=label_path, target=target, image_match=image_path)
        )

    return planned, skipped_aligned, orphans, ambiguous, collisions


def _missing_labels_for_images(
    image_stems: dict[str, Path],
    planned: list[PlannedRename],
    all_label_paths: list[Path],
) -> list[str]:
    """Image stems with no corresponding .txt after planned renames."""
    source_paths = {item.source for item in planned}
    final_label_stems: set[str] = set()
    for label_path in all_label_paths:
        if label_path in source_paths:
            continue
        final_label_stems.add(label_path.stem)
    for item in planned:
        final_label_stems.add(item.target.stem)

    missing: list[str] = []
    for stem in sorted(image_stems):
        if stem not in final_label_stems:
            missing.append(stem)
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rename label .txt files to match top_/oth_ image prefixes."
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        required=True,
        help="Folder containing images/ and labels/ subdirectories.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform renames (default is dry-run only).",
    )
    parser.add_argument(
        "--ext",
        nargs="*",
        default=list(DEFAULT_IMAGE_EXTENSIONS),
        help=f"Image extensions to consider (default: {list(DEFAULT_IMAGE_EXTENSIONS)}).",
    )
    args = parser.parse_args()
    extensions = tuple(e if e.startswith(".") else f".{e}" for e in args.ext)

    dataset_root: Path = args.dataset_root.expanduser().resolve()
    images_dir = dataset_root / "images"
    labels_dir = dataset_root / "labels"

    if not images_dir.is_dir():
        print(f"ERROR: images directory not found: {images_dir}", file=sys.stderr)
        return 2
    if not labels_dir.is_dir():
        print(f"ERROR: labels directory not found: {labels_dir}", file=sys.stderr)
        return 2

    prefixes = DEFAULT_PREFIXES
    try:
        planned, skipped_aligned, orphans, ambiguous, collisions = plan_renames(
            labels_dir, images_dir, prefixes, extensions
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    image_stems = _collect_image_stems(images_dir, extensions)
    all_labels = sorted(
        p for p in labels_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"
    )
    missing = _missing_labels_for_images(image_stems, planned, all_labels)

    print(f"Dataset root: {dataset_root}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    print()

    if planned:
        print("Planned renames:")
        for item in planned:
            print(
                f"  {item.source.name} -> {item.target.name}  "
                f"(image: {item.image_match.name})"
            )
        print()
    else:
        print("No renames planned (already aligned or nothing to fix).")
        print()

    if skipped_aligned:
        print(
            f"Already aligned (label stem matches an image): "
            f"{len(skipped_aligned)} file(s)."
        )
        print()

    if ambiguous:
        print(
            "AMBIGUOUS (no rename; multiple images match the same label stem):"
        )
        for label_path, matches in ambiguous:
            print(f"  {label_path.name}:")
            for _prefix, _ext, img in matches:
                print(f"    - {img.name}")
        print()

    if collisions:
        print("COLLISION (target label exists; no rename):")
        for source, target in collisions:
            print(f"  {source.name} -> {target.name} (exists)")
        print()

    if orphans:
        print("ORPHAN labels (no matching image with top_/oth_ prefix):")
        for path in orphans:
            print(f"  {path.name}")
        print()

    if missing:
        print("MISSING labels (image has no corresponding .txt):")
        for stem in missing:
            print(f"  {stem}.txt (image: {image_stems[stem].name})")
        print()

    if args.apply:
        if ambiguous or collisions:
            print(
                "ERROR: --apply aborted due to ambiguous or collision issues. "
                "Fix the dataset and retry.",
                file=sys.stderr,
            )
            return 1
        for item in planned:
            item.source.rename(item.target)
        print(f"Applied {len(planned)} rename(s).")
    else:
        if planned and not (ambiguous or collisions):
            print("Re-run with --apply to perform these renames.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
