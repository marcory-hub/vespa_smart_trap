**One-line purpose:** install himax repo and requirements on MacOS
**Short summary:** make, arm gnu toolchain, clone repo
**Agent:** SoT: [Build the firmware at MacOS environment](https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2?tab=readme-ov-file#build-the-firmware-at-macos-environment)
**Index:** [[_himax sdk]]

---
make .venv if it does not excist
```sh
python3 -m venv .venv
```
cd make a `himax` folder and activate .venv
```
source .venv/bin/activate
```
check python, pip and git
```sh
python3 --version
```

```sh
pip3 --version
```

```sh
git --version
```
install make with brew install make
```sh
brew install make
make --version
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
Path toevoegen in makefile
open makefile met nano
voeg deze toe
```nano
GNU_TOOLPATH ?= /Applications/ArmGNUToolchain/14.3.rel1/arm-none-eabi/bin
```
of
```sh
echo 'export PATH="/Applications/ArmGNUToolchain/14.3.rel1/arm-none-eabi/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```
controleren welke gcc wordt gebruikt
```sh
which arm-none-eabi-gcc
```
Moet opleveren:
`/Applications/ArmGNUToolchain/14.3.rel1/arm-none-eabi/bin/arm-none-eabi-gcc`
test de compiler met nano.specs
```sh
echo "int main() { return 0; }" | arm-none-eabi-gcc --specs=nano.specs -x c -c -o /dev/null -
```
geen output of foutmelding als alles goed is

clone the seeed gv2 repo to the folder
```sh
git clone --recursive https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2.git
cd Seeed_Grove_Vision_AI_Module_V2
```
path
```sh
export PATH="/Applications/ArmGNUToolchain/14.3.rel1/arm-none-eabi/bin:$PATH" 
hash -r
```

---

next 
1. [[himax makefile]] change APP_TYPE=tflm_yolo11_od
2. [[himax install xmodem]] (only for first install)
3. [[himax build firmware first install]]
4. [[himax flash command firmware]]
5. [[himax ai web toolkit installation]]
