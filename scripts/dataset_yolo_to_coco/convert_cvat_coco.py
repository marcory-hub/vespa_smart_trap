#!/usr/bin/env python3
"""Strip attributes from CVAT COCO export; optionally output 0-3 class variant.
Reads instances_train.json, writes _annotations.coco.json and _annotations.coco_class0-3.json.
"""
import json
import sys

ROOT = __file__.rsplit("/", 1)[0] if "/" in __file__ else "."
IN_PATH = f"{ROOT}/instances_train.json"
OUT_PATH = f"{ROOT}/_annotations.coco.json"
OUT_0_3_PATH = f"{ROOT}/_annotations.coco_class0-3.json"

def main():
    with open(IN_PATH) as f:
        data = json.load(f)

    # Strip attributes from all annotations
    for ann in data["annotations"]:
        ann.pop("attributes", None)

    # Save minimal (no pretty-print)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, separators=(",", ":"))

    # Build 0-3 variant: amel=0, vcra=1, vespsp=2, vvel=3
    # Current: 1=amel, 2=vcra, 3=vespsp, 4=vvel
    id_old_to_new = {1: 0, 2: 1, 3: 2, 4: 3}
    data_03 = {
        "licenses": data["licenses"],
        "info": data["info"],
        "categories": [
            {"id": 0, "name": "amel", "supercategory": ""},
            {"id": 1, "name": "vcra", "supercategory": ""},
            {"id": 2, "name": "vespsp", "supercategory": ""},
            {"id": 3, "name": "vvel", "supercategory": ""},
        ],
        "images": data["images"],
        "annotations": [],
    }
    for ann in data["annotations"]:
        cid = ann["category_id"]
        if cid not in id_old_to_new:
            continue
        a = {k: v for k, v in ann.items()}
        a["category_id"] = id_old_to_new[cid]
        data_03["annotations"].append(a)

    with open(OUT_0_3_PATH, "w") as f:
        json.dump(data_03, f, separators=(",", ":"))

    print(f"Wrote {OUT_PATH} (attributes stripped)")
    print(f"Wrote {OUT_0_3_PATH} (classes 0-3, amel=0)")

if __name__ == "__main__":
    main()
    sys.exit(0)
