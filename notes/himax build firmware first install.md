
**One-line purpose:** how to generate a new firmware image with new custom model
**Short summary:** compile firmware image, copy and compile elf file, generate image firmware file
**Agent:** after adjusting the [[himax makefile]] user should generate new firmware image
**Index:** [[himax from pt to flash]]

---
previous
1. [[himax installation on MacOS environment]]
2. [[himax makefile]] adjusted to yolov8od or yolo11od

---

Github [Himax examples for Seeed Grove Vision AI Module V2](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2) teaches you how to build your own examples and run on Seeed Grove Vision AI Module V2

---

# Build firmware

On mac
- cd to `himax` folder
- activate .venv

cd to EPII_CM55M_APP_S
```sh
cd /Users/md/Developer/vespa_smart_trap/himax/Seeed_Grove_Vision_AI_Module_V2/EPII_CM55M_APP_S
```

compile the firmware
```sh
make clean
make
```

output elf file (executable and linkable format)

generate the firmware image (different command on MacOS)
```sh
cd ../we2_image_gen_local/
```

```sh
cp ../EPII_CM55M_APP_S/obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf input_case1_secboot/
./we2_local_image_gen_macOS_arm64 project_case1_blp_wlcsp.json
```

en cd terug naar Seeed folder
```sh
cd ..
```

next
- [[himax install xmodem]] (only for first install)
-  [[himax flash command firmware]] to flash new model 
- [[himax ai web toolkit installation]]



