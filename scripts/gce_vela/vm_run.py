#!/usr/bin/env python3
"""GCE VELA pipeline steps for vst-vela-01 (terminal runner; mirrors GCE notebook)."""

from __future__ import annotations

import argparse
import os
import random
import shutil
import subprocess
import sys
import urllib.request
import zipfile

WORKDIR = os.path.expanduser("~/vst")
VENV_PYTHON = os.path.join(WORKDIR, ".venv", "bin", "python")
LOG_PATH = os.path.join(WORKDIR, "logs", "agent_run.log")


def log(message: str) -> None:
    line = f"[vm_run] {message}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(line + "\n")


def require_venv() -> None:
    if VENV_PYTHON not in sys.executable:
        raise RuntimeError(
            f"Wrong Python: {sys.executable}. Activate ~/vst/.venv first."
        )


def run_pip(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pip", *args],
        check=check,
        text=True,
    )


def step_preflight() -> None:
    require_venv()
    os.chdir(WORKDIR)
    log(f"python: {sys.executable}")
    for name in ("best.pt", "dataset.zip"):
        if not os.path.isfile(name):
            raise FileNotFoundError(f"Missing {name} in {WORKDIR}")
    log(f"inputs OK: {sorted(os.listdir(WORKDIR))}")


def step_extract() -> None:
    step_preflight()
    dest_dir = "dataset"
    if os.path.isdir(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)
    log("Extracting dataset.zip...")
    with zipfile.ZipFile("dataset.zip", "r") as archive:
        archive.extractall(dest_dir)
    roboflow_train = os.path.join(dest_dir, "images", "train")
    yolo_train = os.path.join(dest_dir, "train", "images")
    if os.path.isdir(roboflow_train) and not os.path.isdir(yolo_train):
        log("Reshaping Roboflow layout -> YOLO layout")
        for split in ("train", "val"):
            os.makedirs(os.path.join(dest_dir, split), exist_ok=True)
            for kind in ("images", "labels"):
                src = os.path.join(dest_dir, kind, split)
                dst = os.path.join(dest_dir, split, kind)
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.move(src, dst)
    n_train = len(os.listdir(os.path.join(dest_dir, "train", "images")))
    n_val = len(os.listdir(os.path.join(dest_dir, "val", "images")))
    log(f"dataset ready: train={n_train} val={n_val}")


def step_pins() -> None:
    step_preflight()
    run_pip("uninstall", "-y", "opencv-python", "opencv-contrib-python", check=False)
    export_pins = [
        "tensorflow==2.18.0",
        "tensorboard==2.18.0",
        "protobuf==5.29.6",
        "ml-dtypes==0.5.1",
        "numpy>=1.26.0,<2.1.0",
        "onnx==1.17.0",
        "onnx-ir==0.2.1",
        "onnxruntime==1.26.0",
        "onnxscript==0.2.7",
        "tf-keras==2.18.0",
        "onnx2tf==1.22.3",
        "onnxslim==0.1.94",
        "sng4onnx>=1.0.1",
        "onnx-graphsurgeon>=0.3.26",
    ]
    run_pip("install", "-q", *export_pins)
    run_pip(
        "install",
        "--force-reinstall",
        "--no-cache-dir",
        "numpy>=1.26.0,<2.1.0",
        "opencv-python-headless==4.10.0.84",
    )
    import cv2
    import onnx
    import tensorflow as tf

    log(f"opencv {cv2.__version__}")
    log(f"tensorflow {tf.__version__} onnx {onnx.__version__}")
    if not tf.__version__.startswith("2.18"):
        raise RuntimeError("tensorflow must be 2.18.x after pins step")


def step_calibrate() -> None:
    step_preflight()
    num_images = 500
    original_train_dir = "dataset/train"
    original_valid_dir = "dataset/val"
    temp_dir = os.path.join(WORKDIR, "temp_subset")
    random.seed(42)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    def copy_random_subset(src_dir: str, dst_dir: str, sample_count: int) -> int:
        img_path = f"{src_dir}/images"
        if not os.path.exists(img_path):
            log(f"Warning: {img_path} not found")
            return 0
        all_images = [
            name
            for name in os.listdir(img_path)
            if name.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        selected = random.sample(all_images, min(sample_count, len(all_images)))
        os.makedirs(f"{dst_dir}/images", exist_ok=True)
        os.makedirs(f"{dst_dir}/labels", exist_ok=True)
        count = 0
        for image_name in selected:
            label_name = image_name.rsplit(".", 1)[0] + ".txt"
            shutil.copy(f"{src_dir}/images/{image_name}", f"{dst_dir}/images/{image_name}")
            src_label_path = f"{src_dir}/labels/{label_name}"
            if os.path.exists(src_label_path):
                shutil.copy(src_label_path, f"{dst_dir}/labels/{label_name}")
            count += 1
        return count

    train_count = copy_random_subset(original_train_dir, f"{temp_dir}/train", num_images)
    valid_count = copy_random_subset(original_valid_dir, f"{temp_dir}/valid", num_images)
    names_list = ["amel", "vcra", "vespsp", "vvel"]
    yaml_text = f"""
train: {temp_dir}/train/images
val: {temp_dir}/valid/images
nc: 4
names: {names_list}
""".strip()
    with open("dataset/data.yaml", "w", encoding="utf-8") as yaml_file:
        yaml_file.write(yaml_text)
    log(f"Train images sampled: {train_count}")
    log(f"Valid images sampled: {valid_count}")


def step_ultralytics() -> None:
    step_preflight()
    if not os.path.isdir("ultralytics"):
        subprocess.run(
            ["git", "clone", "https://github.com/kris-himax/ultralytics"],
            cwd=WORKDIR,
            check=True,
        )
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "./ultralytics"],
        cwd=WORKDIR,
        check=True,
    )
    run_pip("uninstall", "-y", "opencv-python", "opencv-contrib-python", check=False)
    run_pip(
        "install",
        "--force-reinstall",
        "--no-cache-dir",
        "numpy>=1.26.0,<2.1.0",
        "opencv-python-headless==4.10.0.84",
    )
    import cv2
    import ultralytics

    ultralytics.checks()
    log(f"opencv {cv2.__version__}")
    log("ultralytics OK")


def step_export() -> None:
    step_preflight()
    os.environ["YOLO_AUTOINSTALL"] = "0"
    os.chdir(WORKDIR)
    run_pip(
        "install",
        "-q",
        "numpy>=1.26.0,<2.1.0",
        "opencv-python-headless==4.10.0.84",
    )
    import cv2
    import torch.onnx

    original_export = torch.onnx.export

    def legacy_export(*args, **kwargs):
        kwargs["dynamo"] = False
        return original_export(*args, **kwargs)

    torch.onnx.export = legacy_export

    from ultralytics import YOLO

    log(f"export python: {sys.executable}")
    log(f"opencv {cv2.__version__}")
    log("Starting YOLO export (10-20 min CPU, legacy ONNX)...")
    model = YOLO(os.path.join(WORKDIR, "best.pt"))
    model.export(
        format="tflite",
        int8=True,
        no_post=True,
        imgsz=224,
        data=os.path.join(WORKDIR, "dataset/data.yaml"),
    )
    log("export success")


def step_vela_install() -> None:
    step_preflight()
    run_pip("install", "-q", "ethos-u-vela")
    ini_url = (
        "https://raw.githubusercontent.com/HimaxWiseEyePlus/"
        "ML_FVP_EVALUATION/main/vela/himax_vela.ini"
    )
    ini_path = os.path.join(WORKDIR, "himax_vela.ini")
    if not os.path.isfile(ini_path):
        urllib.request.urlretrieve(ini_url, ini_path)
        log("Downloaded himax_vela.ini")
    else:
        log("himax_vela.ini already present")


def step_vela() -> None:
    step_preflight()
    vela_bin = os.path.join(os.path.dirname(sys.executable), "vela")
    subprocess.run(
        [
            vela_bin,
            "--accelerator-config",
            "ethos-u55-64",
            "--config",
            "himax_vela.ini",
            "--system-config",
            "My_Sys_Cfg",
            "--memory-mode",
            "My_Mem_Mode_Parent",
            "--output-dir",
            "./best_saved_model",
            "./best_saved_model/best_full_integer_quant.tflite",
        ],
        cwd=WORKDIR,
        check=True,
    )
    log("vela compile done")


def step_size() -> None:
    step_preflight()
    output_model = os.path.join(WORKDIR, "best_saved_model/best_full_integer_quant_vela.tflite")
    if not os.path.exists(output_model):
        raise FileNotFoundError(f"Missing {output_model}")
    size_mb = os.path.getsize(output_model) / (1024 * 1024)
    log(f"Vela model: {output_model}")
    log(f"Size: {size_mb:.2f} MB")
    limit_mb = 2.4
    if size_mb <= limit_mb:
        log(f"SUCCESS: Model is within the {limit_mb}MB limit.")
    else:
        raise RuntimeError(f"Model ({size_mb:.2f}MB) exceeds {limit_mb}MB limit")


def step_upload() -> None:
    step_preflight()
    dest_folder = os.path.join(WORKDIR, "best_saved_model")
    source_onnx = os.path.join(WORKDIR, "best.onnx")
    if os.path.exists(source_onnx):
        shutil.move(source_onnx, os.path.join(dest_folder, "best.onnx"))
    artifact = os.path.join(dest_folder, "best_full_integer_quant_vela.tflite")
    if not os.path.isfile(artifact):
        raise FileNotFoundError(artifact)
    subprocess.run(
        [
            "gsutil",
            "cp",
            artifact,
            "gs://pt-vela-gce/output/best_full_integer_quant_vela.tflite",
        ],
        check=True,
    )
    zip_name = "full_integer_quant_vela_imgz224.tflite"
    shutil.make_archive(zip_name, "zip", dest_folder)
    subprocess.run(
        ["gsutil", "cp", f"{zip_name}.zip", "gs://pt-vela-gce/output/"],
        cwd=WORKDIR,
        check=True,
    )
    log("Uploaded to gs://pt-vela-gce/output/")


STEPS = {
    "preflight": step_preflight,
    "extract": step_extract,
    "pins": step_pins,
    "calibrate": step_calibrate,
    "ultralytics": step_ultralytics,
    "export": step_export,
    "vela-install": step_vela_install,
    "vela": step_vela,
    "size": step_size,
    "upload": step_upload,
}

FULL_ORDER = [
    "preflight",
    "extract",
    "pins",
    "calibrate",
    "ultralytics",
    "export",
    "vela-install",
    "vela",
    "size",
    "upload",
]

RESUME_ORDER = [
    "preflight",
    "calibrate",
    "pins",
    "ultralytics",
    "export",
    "vela-install",
    "vela",
    "size",
    "upload",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="GCE VELA pipeline steps")
    parser.add_argument(
        "step",
        choices=[*STEPS.keys(), "all", "resume"],
        help="Pipeline step or full run",
    )
    args = parser.parse_args()
    os.makedirs(os.path.join(WORKDIR, "logs"), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(f"\n--- run step={args.step} ---\n")

    if args.step == "all":
        for name in FULL_ORDER:
            log(f"=== {name} ===")
            STEPS[name]()
        return
    if args.step == "resume":
        for name in RESUME_ORDER:
            log(f"=== {name} ===")
            STEPS[name]()
        return
    STEPS[args.step]()


if __name__ == "__main__":
    main()
