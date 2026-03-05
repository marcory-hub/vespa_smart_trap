**One-line purpose:** index quick test audio ML, archived, index [[z audio detectie]]
**Short summary:** audio datasets insufficient for ML
**Agent:** archived

---
https://wiki.seeedstudio.com/grove_vision_ai_v2_himax_sdk/

# Flashen
rebuild firmware
```sh
cd /Users/md/Developer/cv_vespcv_acc/gv2-sdk/Seeed_Grove_Vision_AI_V2_SD-Mic/EPII_CM55M_APP_S && make clean && make
```
maak image
```sh
cd /Users/md/Developer/cv_vespcv_acc/gv2-sdk/Seeed_Grove_Vision_AI_V2_SD-Mic/EPII_CM55M_APP_S && ./output.sh
```
flash meet flasher.py
```sh
cd /Users/md/Developer/cv_vespcv_acc/gv2-sdk/Seeed_Grove_Vision_AI_V2_SD-Mic
python3 flasher.py output.img /dev/tty.usbmodem58FA1047631
```
(als serial port niet klopt dan checken met `ls -la /dev/tty.usbmodem*)

---
# Installatie compilatie omgeving
Tutorial: Himax SDK for the Grove Vision AI platform
- utilize microSD card --> mogelijk handig voor opslaan foto's?
- PDM microphones --> geluids model tzt verberen?

Inhoud
1. [Install Ubuntu 22.04 on Windows Subsystem for Linux (WSL)](https://wiki.seeedstudio.com/grove_vision_ai_v2_himax_sdk/#install-ubuntu-2204-on-windows-subsystem-for-linux-wsl)
2. [Preparation of the compilation environment](https://wiki.seeedstudio.com/grove_vision_ai_v2_himax_sdk/#preparation-of-the-compilation-environment)
3. [Run the recording example using the Himax SDK](https://wiki.seeedstudio.com/grove_vision_ai_v2_himax_sdk/#run-the-recording-example-using-the-himax-sdk)
4. [Himax SDK Code Analysis](https://wiki.seeedstudio.com/grove_vision_ai_v2_himax_sdk/#himax-sdk-code-analysis)

in gv2-sdk folder
```sh
cd /Users/md/Developer/cv_vespcv_acc/gv2-sdk
```

clone repo
```sh
git clone https://github.com/limengdu/Seeed_Grove_Vision_AI_V2_SD-Mic.git
```

Project openen `Seeed_Grove_Vision_AI_V2_SD-Mic` in Cursor/VScode


**Install Prerequisites**
check of GNU make geinstalleerd is
``` sh
make --version
```
anders installeren
```sh
brew install make
```

Installeer Arm GNU Toolchain (in bovenliggende folder)
```sh
wget https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-darwin-arm64-arm-none-eabi.tar.xz
```
uitpakken
```sh
tar -xvf arm-gnu-toolchain-13.2.rel1-darwin-arm64-arm-none-eabi.tar.xz
```
toevoegen aan .zshrc
```sh
   nano ~/.zshrc
```
add
```sh
export PATH="/Users/md/Developer/cv_vespcv_acc/gv2-sdk/arm-gnu-toolchain-13.2.rel1-darwin-arm64-arm-none-eabi.tar.xz/bin:$PATH"
```
reload
```sh
source ~/.zshrc
```
check
```sh
echo $PATH | tr ':' '\n' | grep gnu
arm-none-eabi-gcc --version
```
![[acc gv2 SDK.png]]
zou 13.2 moeten zijn, nu 13.3 (zeker niet installeren via apt install, die is te oud)

Environment is klaar
Project compilen en uploaden
project folder **EPII_CM55M_APP_S**
open makefile in folder **EPII_CM55M_APP_S**
```sh
nano makefile
```
pas GNU_TOOLPATH regel 47 aan
absolute path naar bin folder
```sh
/Users/md/Developer/cv_vespcv_acc/gv2-sdk/arm-gnu-toolchain-13.2.Rel1-x86_64-arm-none-eabi/bin
```

```sh
#GNU_TOOLPATH ?= /Users/md/Developer/cv_vespcv_acc/gv2-sdk/arm-gnu-toolchain-13.2.Rel1-x86_64-arm-none-eabi/bin
GNU_TOOLPATH ?= $(shell which arm-none-eabi-gcc | sed 's|/arm-none-eabi-gcc||')
```
---

**## Fixes for Mac Silicon (Apple Silicon M1/M2)**
### 1 Added macOS/Darwin detection in scripts.mk (so the Makefile recognizes macOS)
1. Update OS detection (around line 34) to handle macOS using uname -s.
2. Add a Darwin/macOS section (after line 126) with the same Unix-like settings as GNU/Linux.
In /Users/md/Developer/cv_vespcv_acc/gv2-sdk/Seeed_Grove_Vision_AI_V2_SD-Mic/EPII_CM55M_APP_S/options/scripts.mk 
regel 33-35
```
else ## Linux Environment ##
	HOST_OS:=$(shell uname -o)
endif
```
vervangen door
```
else ## Linux/Unix Environment ##
	# On macOS, uname -o doesn't exist, so use uname -s instead
	UNAME_S:=$(shell uname -s)
	ifeq "$(UNAME_S)" "Darwin"
		HOST_OS:=Darwin
	else
		HOST_OS:=$(shell uname -o)
	endif
endif
```
voor MAKEFILE COMPILE MESSAGE CONTROL toevoegen
```
## Check OS == Darwin (macOS) ##
ifeq "$(HOST_OS)" "Darwin"
	PS=/$(nullstring)
	NULL=/dev/null
	OPNPRN=\(
	CLSPRN=\)

	RM=rm -rf
	RMD=rm -rf
	ECHO=echo
	CP=cp
	MKD = mkdir -p

	IFEXISTDIR=[ ! -d$(space)
	ENDIFEXISTDIR=$(space)] ||

	IFNOTEXISTDIR=[ -d$(space)
	ENDIFEXISTDIR=$(space)] ||

	IFEXISTFILE=[ ! -f$(space)
	ENDIFEXISTFILE=$(space)] ||

	IFNOTEXISTFILE=[ -f$(space)
	ENDIFNOTEXISTFILE=$(space)] ||
endif
```

Find lines 298-301:
rules.mkLines 298-301
```
%/.mkdir_done:    $(TRACE_CREATE_DIR)    $(TRY_MK_OBJDIR)    @$(ECHO) $(@D) > $@
```
Replace with:
```
%/.mkdir_done:    $(TRACE_CREATE_DIR)    $(TRY_MK_OBJDIR)    @$(MKD) $(@D) 2> $(NULL) || true    @$(ECHO) $(@D) > $@
```

checks
```
which arm-none-eabi-gcc
```
check architecture ARM64
```sh
file /Applications/ArmGNUToolchain/14.3.rel1/arm-none-eabi/bin/arm-none-eabi-gcc
```
check
```sh
arm-none-eabi-gcc --version
```
bevestig dat het werkt met 
```
make
```

expecte output
```
Memory region         Used Size  Region Size  %age Used
 CM55M_S_APP_ROM:       77476 B       256 KB     29.55%
CM55M_S_APP_DATA:       30736 B       256 KB     11.72%
    CM55M_S_SRAM:      160000 B      1924 KB      8.12%
/Applications/ArmGNUToolchain/14.3.rel1/arm-none-eabi/bin/arm-none-eabi-size obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf
   text	   data	    bss	    dec	    hex	filename
  82792	    652	 184592	 268036	  41704	obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf
  ```

cd to Seeed_Grove_Vision_AI_V2_SD-Mic/EPII_CM55M_APP_S
```sh
make clean
make
```
.elf converteren naar .img
```sh
./output.sh
```


```sh
cp /Users/md/Developer/cv_vespcv_acc/Himax/Seeed_Grove_Vision_AI_Module_V2/we2_image_gen_local/we2_local_image_gen_macOS_arm64 \
   /Users/md/Developer/cv_vespcv_acc/gv2-sdk/Seeed_Grove_Vision_AI_V2_SD-Mic/we2_image_gen_local/
```
update output.sh regel 6
```nano
./we2_local_image_gen_macOS_arm64 ./project_case1_blp_wlcsp.json
```
missing macOS secure boot tool
```sh
cp -r /Users/md/Developer/cv_vespcv_acc/Himax/Seeed_Grove_Vision_AI_Module_V2/we2_image_gen_local/secureboot_tool/mac \
      /Users/md/Developer/cv_vespcv_acc/gv2-sdk/Seeed_Grove_Vision_AI_V2_SD-Mic/we2_image_gen_local/secureboot_tool/
```

```sh
chmod +x /Users/md/Developer/cv_vespcv_acc/gv2-sdk/Seeed_Grove_Vision_AI_V2_SD-Mic/we2_image_gen_local/secureboot_tool/mac/generate_secureboot_certificates
```

```sh
cp -r /Users/md/Developer/cv_vespcv_acc/Himax/Seeed_Grove_Vision_AI_Module_V2/we2_image_gen_local/arm_none_eabi/mac \
      /Users/md/Developer/cv_vespcv_acc/gv2-sdk/Seeed_Grove_Vision_AI_V2_SD-Mic/we2_image_gen_local/arm_none_eabi/
```

```sh
chmod +x /Users/md/Developer/cv_vespcv_acc/gv2-sdk/Seeed_Grove_Vision_AI_V2_SD-Mic/we2_image_gen_local/arm_none_eabi/mac/arm-none-eabi-objcopy
chmod +x /Users/md/Developer/cv_vespcv_acc/gv2-sdk/Seeed_Grove_Vision_AI_V2_SD-Mic/we2_image_gen_local/arm_none_eabi/mac/arm-none-eabi-objdump
```

```sh
pip install pyserial xmodem tqdm
```

```sh
pip install pyserial
```

vind port
```sh
ls /dev/tty.usb* /dev/cu.usb* 2>/dev/null
```
/dev/tty.usbmodem58FA1047631

run script
```sh
cd /Users/md/Developer/cv_vespcv_acc/gv2-sdk/Seeed_Grove_Vision_AI_V2_SD-Mic
python flasher.py we2_image_gen_local/output_case1_sec_wlcsp/output.img /dev/tty.usbmodem58FA1047631
```

expected output
```
(.venv) md@m2 Seeed_Grove_Vision_AI_V2_SD-Mic % cd /Users/md/Developer/cv_vespcv_acc/gv2-sdk/Seeed_Grove_Vision_AI_V2_SD-Mic

python flasher.py we2_image_gen_local/output_case1_sec_wlcsp/output.img /dev/tty.usbmodem58FA1047631

Waiting for burn mode

#

Start transfer

100%|████████████████████████████████████████| 252k/252k [00:07<00:00, 34.9kB/s]

Waiting for completion

#

Flash completed
```

in getdata.py
playsound  niet compatible met python3.14
```
# from playsound import playsound  # Not needed - playback is commented out
```
en
serial port ipv COM27 gebruiken (regel 23)
```
ser = serial.Serial("/dev/tty.usbmodem58FA1047631", 921600, timeout=5)
```
record and save 4 sec audio (let op typo op de site niet getdate maar getdata)

```
python getdata.py
```

