**One-line purpose:** index quick test audio ML, archived
**Short summary:** audio datasets insufficient for ML
**Agent:** archived

---
[[z audio database geluid]]
[[z audio gv2 SDK PDM]]

---

**Development**
**arduino**
**.venv**

brew update
brew outdated
brew upgrade
brew cleanup
cd Developer/arduino
source .venv/bin/activate

nodig
python3
node.js v16.x of hoger

mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.zprofile

npm install -g edge-impulse-cli

controleren met
edge-impulse-cli --version
npm --version

https://docs.arduino.cc/hardware/nano-33-ble-sense/
Use the built-in omnidirectional digital microphone (MP34DT05) to capture and analyze sound in real time to create a voice interface for your project. Use the PDM library to implement its functionalities in your projects.

brew install arduino-cli
arduino-cli version

download [firmware](https://cdn.edgeimpulse.com/firmware/arduino-nano-33-ble-sense.zip)
unzip
./flash_mac.command
[[z audio database geluid]]
# omzetten naar waf
```sh
ffmpeg -i vvel004.mp4 vvel004.wav
```

Create Impulse
MFCC
Autotune parameters
![[ad_index audio detectie-5.png]]

![[ad_index audio detectie-6.png]]

retrain model

live classification

Model testing
![[ad_index audio detectie-7.png]]
Perform calibration
Deployment
![[ad_index audio detectie-9.png]]
![[ad_index audio detectie-10.png]]
in sharepoint gezet
[acc-ethos-u55-64-v10.zip](https://imkersleiden.sharepoint.com/:u:/g/EZsyQbJ9HAhMr2c66ZwcGSwB-3piHJERxwRdyozEW9XkGg?e=kwUlKH)

evt verder met https://docs.edgeimpulse.com/tutorials/end-to-end/sound-recognition

betere dataset maken indien we het toe gaan passen


