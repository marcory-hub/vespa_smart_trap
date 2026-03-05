
**One-line purpose:** build firmware
**Short summary:** 
**Agent:** inactive

---


```sh
cd /Users/md/Developer/vespCVacc/Himax/
source .venv/bin/activate
```
### Himax github project clonen
dit bevat enkele voorbeelden
```sh
git clone --recursive https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2.git
cd Seeed_Grove_Vision_AI_Module_V2
```
### PATH
```sh
export PATH="/Applications/ArmGNUToolchain/14.3.rel1/arm-none-eabi/bin:$PATH" 
hash -r
```
### Firmware compilen
```sh
cd EPII_CM55M_APP_S
make clean
make
```
obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf
(bij error terug naar laatste stap van het maken van environment)
### Maak firmware image
```sh
cd ../we2_image_gen_local/
cp ../EPII_CM55M_APP_S/obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf input_case1_secboot/
```

run script om output.img te maken
```sh
./we2_local_image_gen_macOS_arm64 project_case1_blp_wlcsp.json
```
Output image: output_case1_sec_wlcsp/output.img
Output image: output_case1_sec_wlcsp/output.img

IMAGE GEN DONE

verder met [[himax flash firmware]]