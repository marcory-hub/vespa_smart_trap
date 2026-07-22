
**One-line purpose:** restore factory settings of gv2
**Short summary:** himax or sensecraft restore
**Agent:** inactive

---


2025-07: Gekoppeld aan raspberry en ook daar vast gelopen, maar vervolgens bij aansluiten op de mac en SenseCraft site werd firmware opnieuw geïnstalleerd


cd # Update system
```
sudo apt update && sudo apt upgrade -y
```

# Install required packages
```
sudo apt install -y python3-pip git screen minicom
```

# Clone the repository
```
cd ~
git clone --recursive https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2.git
cd Seeed_Grove_Vision_AI_Module_V2
```

# Set up Python environment
```
python3 -m venv .venv

pip install -r xmodem/requirements.txt
```

# Download SenseCraft firmware
```
wget https://cdn.edgeimpulse.com/firmware/seeed-grove-vision-ai-module-v2.zip
unzip seeed-grove-vision-ai-module-v2.zip
```

# Check device connection
```
ls /dev/ttyUSB* /dev/ttyACM*
```

# Set permissions
```
sudo chmod 666 /dev/ttyACM0
```  
or whatever port shows up

# Flash firmware
```
python3 xmodem/xmodem_send.py \
  --port=/dev/ttyACM0 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=firmware.img
```

## nieuwe poging

# Install ARM toolchain
```
sudo apt install -y gcc-arm-none-eabi
```

# Install build essentials (make and other build tools)
```
sudo apt install -y build-essential
```

# build w yolo11n model
```
cd ~/Seeed_Grove_Vision_AI_Module_V2/EPII_CM55M_APP_S
gmake clean
gmake APP_TYPE=tflm_yolo11_od

cd ../we2_image_gen_local/
cp ../EPII_CM55M_APP_S/obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf input_case1_secboot/
```

# flash
```
python3 xmodem/xmodem_send.py \
  --port=/dev/ttyACM0 \
  --baudrate=921600 \
  --protocol=xmodem \
  --file=we2_image_gen_local/output_case1_sec_wlcsp/output.img
```

make image generator executable
# Check if the file exists with a different name
```
ls -l we2_local_image_gen*
```
# If it exists, make it executable
```
chmod +x we2_local_image_gen_linux_arm64
```

# First, make sure we're in the right directory
```
cd ~/Seeed_Grove_Vision_AI_Module_V2/we2_image_gen_local/
```

# Copy the ELF file to the input directory
```
cp ../EPII_CM55M_APP_S/obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf input_case1_secboot/
```

# Generate the image using the Linux version of the tool
```
./we2_local_image_gen project_case1_blp_wlcsp.json
```

# Check if the ELF file was created
```
ls -l EPII_CM55M_APP_S/obj_epii_evb_icv30_bdv10/gnu_epii_evb_WLCSP65/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf
```

# Check if the image was generated
```
ls -l we2_image_gen_local/output_case1_sec_wlcsp/output.img
```


# Check the secureboot tool contents
ls -l secureboot_tool/

# Check the key gen tool contents
ls -l key_gen_tool/

# Also, let's look at the project JSON file
cat project_case1_blp_wlcsp.json

# check of we alles hebben
ls -l common/bl/EPII_FW_BL_arm_epii_evb_xtal24rc96rc32k.bin
ls -l common/2ndbl/EPII_FW_2NDBL_arm_epii_evb.bin
ls -l common/sec_mem/sec_mem_layout_one_sonly_bin.json

# gererate img bin
# Make sure we're in the right directory
```
cd ~/Seeed_Grove_Vision_AI_Module_V2/we2_image_gen_local
```

# Try running the Linux binary
```
./we2_local_image_gen project_case1_blp_wlcsp.json
```

# Create a temporary directory for our work
```
mkdir -p temp_image
```

# Copy all required files to our temp directory
```
cp common/bl/EPII_FW_BL_arm_epii_evb_xtal24rc96rc32k.bin temp_image/bootloader.bin
cp common/2ndbl/EPII_FW_2NDBL_arm_epii_evb.bin temp_image/2ndbl.bin
cp common/sec_mem/sec_mem_layout_one_sonly_bin.json temp_image/memdesc.json
cp input_case1_secboot/EPII_CM55M_gnu_epii_evb_WLCSP65_s.elf temp_image/app.elf

cd temp_image
```

# Convert ELF to binary
./arm-none-eabi-objcopy -O binary app.elf app.bin

# Create the final image
dd if=/dev/zero of=output.img bs=1M count=16
dd if=bootloader.bin of=output.img bs=1 seek=$((0x34005000)) conv=notrunc
dd if=2ndbl.bin of=output.img bs=1 seek=$((0x3401f000)) conv=notrunc
dd if=app.bin of=output.img bs=1 seek=$((0x00000000)) conv=notrunc