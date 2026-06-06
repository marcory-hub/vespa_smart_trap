#!/usr/bin/env python3
"""
Archive reviewed images into images_reviewed/ using all review logs.

Sources merged:
  - .review_folder_placement.json  -> reviewed[] and moves[]
  - review_moves.log               -> every folder correction (T/O)
  - archive_reviewed.log           -> prior archive runs (if any)

With --use-sequence (default): also archive every image from the start of the
sorted queue through the furthest queue index seen in any key above. That
covers images marked correct (N/Space) with no line in review_moves.log, as
long as you reviewed in order.

Example:
  source .venv/bin/activate
  python scripts/dataset_top_select/archive_reviewed_from_state.py \\
    --dataset-root data/dataset_top --dry-run
  python scripts/dataset_top_select/archive_reviewed_from_state.py \\
    --dataset-root data/dataset_top
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from review_folder_placement import (  # noqa: E402
    ARCHIVE_LOG_NAME,
    DEFAULT_MOVES_LOG_NAME,
    DEFAULT_STATE_NAME,
    SOURCE_SPLITS,
    QueueItem,
    archive_item_to_reviewed,
    build_queue,
    locate_active_item,
    locate_reviewed_item,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Archive reviewed images using state + move logs + queue sequence.",
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path("data/dataset_top"),
        help="Dataset root (default: data/dataset_top).",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=None,
        help=f"State JSON (default: <dataset-root>/{DEFAULT_STATE_NAME}).",
    )
    parser.add_argument(
        "--moves-log",
        type=Path,
        default=None,
        help=f"Move log (default: <dataset-root>/{DEFAULT_MOVES_LOG_NAME}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without moving files.",
    )
    parser.add_argument(
        "--no-sequence",
        action="store_true",
        help="Only archive explicit log keys, not queue positions 0..max before them.",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        choices=list(SOURCE_SPLITS),
        default=list(SOURCE_SPLITS),
        help="Splits included in queue order (default: train val test).",
    )
    return parser.parse_args()


def parse_log_line(line: str) -> tuple[str, str] | None:
    if "split=" not in line or "stem=" not in line:
        return None
    split = stem = None
    for token in line.split():
        if token.startswith("split="):
            split = token.split("=", 1)[1]
        elif token.startswith("stem="):
            stem = token.split("=", 1)[1]
    if split and stem:
        return (split, stem)
    return None


def keys_from_text_log(log_path: Path) -> set[tuple[str, str]]:
    if not log_path.is_file():
        return set()
    keys: set[tuple[str, str]] = set()
    for line in log_path.read_text(encoding="utf-8").splitlines():
        parsed = parse_log_line(line.strip())
        if parsed is not None:
            keys.add(parsed)
    return keys


def collect_explicit_keys(
    state_path: Path,
    moves_log: Path,
    archive_log: Path,
) -> tuple[set[tuple[str, str]], dict[str, int]]:
    counts: dict[str, int] = {}
    keys: set[tuple[str, str]] = set()

    if state_path.is_file():
        data = json.loads(state_path.read_text(encoding="utf-8"))
        from_state = {tuple(pair) for pair in data.get("reviewed", [])}
        keys |= from_state
        counts["state_reviewed"] = len(from_state)
        from_json_moves = {
            (m["split"], m["stem"]) for m in data.get("moves", []) if "split" in m and "stem" in m
        }
        keys |= from_json_moves
        counts["state_moves_json"] = len(from_json_moves)
    else:
        counts["state_reviewed"] = 0
        counts["state_moves_json"] =  0

    from_moves_log = keys_from_text_log(moves_log)
    keys |= from_moves_log
    counts["review_moves_log"] = len(from_moves_log)

    from_archive_log = keys_from_text_log(archive_log)
    keys |= from_archive_log
    counts["archive_reviewed_log"] = len(from_archive_log)

    counts["explicit_union"] = len(keys)
    return keys, counts


def expand_sequence_keys(
    explicit: set[tuple[str, str]],
    dataset_root: Path,
    splits: list[str],
) -> tuple[set[tuple[str, str]], int]:
    full_queue = build_queue(dataset_root, splits, set())
    if not full_queue:
        return set(), -1

    index_by_key = {item.reviewed_key: index for index, item in enumerate(full_queue)}
    indices = [index_by_key[key] for key in explicit if key in index_by_key]
    if not indices:
        return set(), -1

    max_index = max(indices)
    sequence_keys = {full_queue[index].reviewed_key for index in range(max_index + 1)}
    return sequence_keys, max_index + 1


def archive_keys(
    keys: set[tuple[str, str]],
    dataset_root: Path,
    archive_log: Path,
    dry_run: bool,
) -> dict[str, int]:
    stats = {"archived": 0, "already": 0, "missing": 0, "failed": 0}

    for split, stem in sorted(keys):
        active = locate_active_item(dataset_root, split, stem)
        if active is None:
            if locate_reviewed_item(dataset_root, split, stem) is not None:
                stats["already"] += 1
            else:
                stats["missing"] += 1
                print(f"Missing: {split} {stem}", file=sys.stderr)
            continue

        ok, message = archive_item_to_reviewed(
            active, dataset_root, archive_log, dry_run=dry_run
        )
        if ok:
            stats["archived"] += 1
        else:
            stats["failed"] += 1
            print(f"Failed {split}/{stem}: {message}", file=sys.stderr)

    return stats


def main() -> int:
    args = parse_args()
    dataset_root = args.dataset_root.expanduser().resolve()
    state_path = (
        args.state_file.expanduser().resolve()
        if args.state_file
        else dataset_root / DEFAULT_STATE_NAME
    )
    moves_log = (
        args.moves_log.expanduser().resolve()
        if args.moves_log
        else dataset_root / DEFAULT_MOVES_LOG_NAME
    )
    archive_log = dataset_root / ARCHIVE_LOG_NAME

    explicit, source_counts = collect_explicit_keys(state_path, moves_log, archive_log)
    print("Explicit keys by source:")
    for name, count in source_counts.items():
        print(f"  {name}: {count}")

    keys_to_archive = set(explicit)
    max_position = -1
    if not args.no_sequence:
        sequence_keys, max_position = expand_sequence_keys(
            explicit, dataset_root, args.splits
        )
        added = len(sequence_keys - explicit)
        keys_to_archive |= sequence_keys
        print(f"Sequence expansion (sorted queue): through position {max_position}")
        print(f"  added {added} keys (marked correct / not in move log)")

    print(f"Total keys to archive: {len(keys_to_archive)}")

    stats = archive_keys(keys_to_archive, dataset_root, archive_log, args.dry_run)

    print("Summary:")
    for name, value in stats.items():
        print(f"  {name}: {value}")
    if args.dry_run:
        print("Dry run: no files were moved.")
    else:
        print(f"  log: {archive_log}")
    return 1 if stats["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
