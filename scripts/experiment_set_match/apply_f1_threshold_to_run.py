#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


SCORING_CLASSES = ["amel", "vcra", "vespsp", "vvel"]


def parse_json_list(raw: str) -> set[str]:
    if not raw:
        return set()
    parsed = json.loads(raw)
    if not isinstance(parsed, list):
        return set()
    return {str(item) for item in parsed}


def parse_json_dict(raw: str) -> dict[str, Any]:
    if not raw:
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        return {}
    return parsed


def compute_match_type(pred_set: set[str], gt_set: set[str]) -> str:
    if pred_set == gt_set:
        return "complete"
    if pred_set.intersection(gt_set):
        return "partial"
    return "no_match"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create threshold-specific CSVs from an existing run folder.")
    parser.add_argument("--run-dir", required=True, help="Run folder containing per_image_results.csv")
    parser.add_argument("--threshold", type=float, required=True, help="F1 threshold to apply on sample_avg_conf_by_class")
    parser.add_argument("--suffix", default="f1_threshold", help="Suffix for generated CSV filenames")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    per_image_in = run_dir / "per_image_results.csv"
    if not per_image_in.exists():
        raise FileNotFoundError(f"Missing input CSV: {per_image_in}")

    per_image_out = run_dir / f"per_image_results_{args.suffix}.csv"
    per_class_out = run_dir / f"per_class_metrics_{args.suffix}.csv"

    with per_image_in.open("r", newline="", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        rows = list(reader)

    if not rows:
        raise RuntimeError("Input per_image_results.csv has no rows.")

    transformed_rows: list[dict[str, Any]] = []
    per_class_tp = {class_name: 0 for class_name in SCORING_CLASSES}
    per_class_fp = {class_name: 0 for class_name in SCORING_CLASSES}
    per_class_fn = {class_name: 0 for class_name in SCORING_CLASSES}

    for row in rows:
        gt_set = parse_json_list(row.get("gt_set", ""))
        sample_avg_conf = parse_json_dict(row.get("sample_avg_conf_by_class", ""))

        pred_set_threshold: set[str] = set()
        for class_name in SCORING_CLASSES:
            raw_value = sample_avg_conf.get(class_name)
            if raw_value is None:
                continue
            try:
                avg_conf = float(raw_value)
            except (TypeError, ValueError):
                continue
            if avg_conf >= args.threshold:
                pred_set_threshold.add(class_name)

        exact_match_threshold = int(pred_set_threshold == gt_set)
        match_type_threshold = compute_match_type(pred_set_threshold, gt_set)
        multi_species_threshold = int(len(gt_set) > 1 or len(pred_set_threshold) > 1)

        for class_name in SCORING_CLASSES:
            gt_has = class_name in gt_set
            pred_has = class_name in pred_set_threshold
            if gt_has and pred_has:
                per_class_tp[class_name] += 1
            elif pred_has and not gt_has:
                per_class_fp[class_name] += 1
            elif gt_has and not pred_has:
                per_class_fn[class_name] += 1

        next_row = dict(row)
        next_row["threshold_f1"] = f"{args.threshold:.6f}"
        next_row["pred_set_f1_threshold"] = json.dumps(sorted(pred_set_threshold))
        next_row["exact_match_f1_threshold"] = str(exact_match_threshold)
        next_row["match_type_f1_threshold"] = match_type_threshold
        next_row["multi_species_flag_f1_threshold"] = str(multi_species_threshold)
        transformed_rows.append(next_row)

    per_image_fieldnames = list(transformed_rows[0].keys())
    with per_image_out.open("w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=per_image_fieldnames)
        writer.writeheader()
        for row in transformed_rows:
            writer.writerow(row)

    with per_class_out.open("w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=[
                "class_name",
                "threshold_f1",
                "TP",
                "FP",
                "FN",
                "support_gt_images",
                "precision",
                "recall",
            ],
        )
        writer.writeheader()
        for class_name in SCORING_CLASSES:
            tp = per_class_tp[class_name]
            fp = per_class_fp[class_name]
            fn = per_class_fn[class_name]
            support = tp + fn
            precision = "NA" if (tp + fp) == 0 else f"{tp / (tp + fp):.6f}"
            recall = "NA" if (tp + fn) == 0 else f"{tp / (tp + fn):.6f}"
            writer.writerow(
                {
                    "class_name": class_name,
                    "threshold_f1": f"{args.threshold:.6f}",
                    "TP": tp,
                    "FP": fp,
                    "FN": fn,
                    "support_gt_images": support,
                    "precision": precision,
                    "recall": recall,
                }
            )

    print(f"Wrote: {per_image_out}")
    print(f"Wrote: {per_class_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

