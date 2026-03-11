**One-line purpose:** install himax repo and requirements on MacOS
**Short summary:** make, arm gnu toolchain, clone repo
**Agent:** SoT: [Build the firmware at MacOS environment](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2?tab=readme-ov-file#build-the-firmware-at-macos-environment)
**Index:** [[_himax sdk]]

---

cd make a `himax` folder and activate .venv
```
source .venv/bin/activate
```

install make with brew install make
```sh
brew install make
```
make sure `make --version` is GNU (not BSD)

create alias to prevent conflicts with default make 
```sh
alias make='gmake'
```

Download Arm GNU Toolchain 
```sh
cd ~
wget https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-x86_64-arm-none-eabi.tar.xz
```
extract
```sh
tar -xvf arm-gnu-toolchain-13.2.rel1-x86_64-arm-none-eabi.tar.xz
```
Add arm-gnu-toolchain-13.2.Rel1-x86_64-arm-none-eabi/bin/: to PATH
`#this is just the example, you can not just copy and paste !! export PATH="$HOME/arm-gnu-toolchain-13.2.Rel1-x86_64-arm-none-eabi/bin/:$PATH"`

clone the seeed gv2 repo to the folder
```sh
git clone --recursive https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2.git
cd Seeed_Grove_Vision_AI_Module_V2
```

---

next 
1. [[himax makefile]] change APP_TYPE=tflm_yolo11_od
2. [[himax install xmodem]] (only for first install)
3. [[himax build firmware first install]]
4. [[himax flash command firmware]]
5. [[himax ai web toolkit installation]]
