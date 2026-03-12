
**One-line purpose:** build firmware
**Short summary:** commands to build the firmware
**Agent:** for user to copy and paste to terminal
**Main Index:** [[_himax sdk]]
[[himax build firmware first install]]

---

### Build firmware
```sh
cd EPII_CM55M_APP_S
make clean
make
cd ../we2_image_gen_local/
cp ../EPII_CM55M_APP_S/obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf input_case1_secboot/
./we2_local_image_gen_macOS_arm64 project_case1_blp_wlcsp.json
cd ..
```
- Build: `EPII_CM55M_APP_S` → `make clean` then `make`.
- Copy ELF into `we2_image_gen_local/input_case1_secboot/`.
- Run `we2_local_image_gen_macOS_arm64 project_case1_blp_wlcsp.json` in `we2_image_gen_local`.
- Flash from `we2_image_gen_local/output_case1_sec_wlcsp/output.img`.
- And go back to main folder to flash the firmware

---
