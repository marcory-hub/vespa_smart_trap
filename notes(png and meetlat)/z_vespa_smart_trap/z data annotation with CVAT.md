# Annotate data
Go to https://www.cvat.ai
Click `Try for free` and sign-up and login
Make a new project
Add labels, choose color and click `continue`
- Vespa_velutina
- Vespa_crabro
- Vespula_velutina

Click on `+` to create new task
Click or drag files to this area
Click `submit & open`

Click on `Job #number` to open task

Label
Click on rectangle (taskbar on the left) to Draw new rectangle
Select the class name
Click `shape`

f: forward
n: new shape
ctrl + s: save
backup task and project

# Export annotation data

Go to tasks
Under Actions (bottom left) select Export task dataset
Export format: choose YOLO 1.1
Enter a 'Custom name.zip'
(add images is not possible with a free tier)
Click `here`
Download the zip file

# Format data
Open the downloaded zipfile
Open the folder obj_train_data
Copy the txt files to the file with the images and sort on name

Copy the text files to the folder with the images (total 3148 6296) 
Check if every images has a txt with the same name
Make three folders: train, val and test
Verdeel as follow:
- 80% in folder names train (2518)
- 10% in folder named val (315)
- 10% in folder named test (315)

Make 2 folders
- images
- labels
Put images in images and txt in labels
zip the data in data.zip


[bron](https://www.youtube.com/watch?v=PfQwNe0P-G4&list=WL&index=5)

www.cvat.ai

try for free
login
Project
Name: hornet
Labels:
- VespaCrabro
- VespaVelutina
- VespulaVulgaris
submit & open
`+` create a new task
task-0001
click or drag files
click submit & open to upload
click job nr
click in linker sidebar de rechthoek
kies juiste soort
click shape
volgende selecties met f (nieuw plaatje) en n (nieuwe shapef)
d vorige plaatje

save

tasks
open
export annotations
yolo 1.1
download 

maak mappenstructuur
vespCV
	data
		images
			train
			val
		labels
			train
			val
	
80% in train (330)
10% in val (12 per class) (51)
10% in test (12 per class) (51)

om de 11 1 naar test en 1 naar val

zipfile van data folder maken
deze zip in google drive zetten

https://github.com/computervisioneng/train-yolov10-custom-data-full-guide

https://github.com/computervisioneng/train-yolov10-custom-data-full-guide/blob/main/Yolov10ObjectDetectionCustomTraining.ipynb

open colab
selecteer een T4

1: mount google drive
2: pas path naam aan en pak zip uit
3: install packages
4: pas config aan
	config.yaml
	classes aanpassen naar\

5: download
als er een error optreed dan restart session
model staat in runs/detect/train
comprimeren van runs folder
downloaden van runs
zet folder runs in je folder vespCV

in vsocde
python3 -m venv venv
source venv/bin/activate

pip install torch torchvision torchaudio
pip install opencv-python
pip install ultralytics

https://wiki.seeedstudio.com/tutorial_of_ai_kit_with_raspberrypi5_about_yolov8n_object_detection/

in vscode naar de folder met de weights
convert .pt naar .onnx
```sh
yolo export model=./best.pt imgsz=640 format=onnx opset=11 
```
