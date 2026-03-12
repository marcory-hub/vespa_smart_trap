import os
import shutil
from pathlib import Path


IMAGE_DIR = Path("/Users/md/Developer/vespa_smart_trap/test/images")
TOP_DOWN_DIR = IMAGE_DIR / "top_down"
SIDE_DIR = IMAGE_DIR / "side"
OTHER_DIR = IMAGE_DIR / "other"

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def iter_images():
    for entry in sorted(IMAGE_DIR.iterdir()):
        if entry.is_dir():
            continue
        if entry.suffix.lower() not in VALID_EXTENSIONS:
            continue
        if entry.parent in (TOP_DOWN_DIR, SIDE_DIR, OTHER_DIR):
            continue
        yield entry


def choose_target():
    while True:
        choice = input("[t]op-down, [s]ide, [o]ther, [q]uit? ").strip().lower()
        if choice in {"t", "s", "o", "q"}:
            return choice


def main():
    TOP_DOWN_DIR.mkdir(exist_ok=True)
    SIDE_DIR.mkdir(exist_ok=True)
    OTHER_DIR.mkdir(exist_ok=True)

    images = list(iter_images())
    print(f"Found {len(images)} images to classify.")

    for index, image_path in enumerate(images, start=1):
        print(f"\n[{index}/{len(images)}] {image_path.name}")
        os.system(f'open "{image_path}"')

        choice = choose_target()
        if choice == "q":
            print("Stopping early by user request.")
            break

        if choice == "t":
            target_dir = TOP_DOWN_DIR
        elif choice == "s":
            target_dir = SIDE_DIR
        else:
            target_dir = OTHER_DIR

        destination = target_dir / image_path.name
        print(f"Moving -> {destination}")
        shutil.move(str(image_path), str(destination))

    print("Done.")


if __name__ == "__main__":
    main()

