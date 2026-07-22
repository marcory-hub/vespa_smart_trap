**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---

# 1. Transfere images, labels and yaml to google drive



- YOLO11s model imgsz 224


1. Make sure it has this folder structure with these exact names:

```
data
  train
    images
    labels
   valid
    images
    labels
```

2. Zip the data folder to a file names `dataset.zip` On mac use `zip -r dataset.zip . -x "*.DS_Store" "__MACOSX/*" ".Trashes/*" ".Spotlight-V100/*" ".TemporaryItems/*"` to exclude hidden files, such as finderfiles, from the zipped file.

3. Make in google drive the folder `vespCV`.

4. Copy the dataset.zip file to the folder vespCV.

5. Add `data.yaml` to folder vespCV.

# Mount Google Drive
```
from google.colab import drive

drive.mount('/content/drive', force_remount=True)
# check GPU
gpu_info = !nvidia-smi
gpu_info = '\n'.join(gpu_info)
if gpu_info.find('failed') >= 0:
  print('Not connected to a GPU')
else:
  print(gpu_info)
```
# Adjust the zipped file name
# Copy zipped dataset to colab and unzip the dataset

!scp '/content/drive/MyDrive/vespCV/dataset.zip' '/content/dataset.zip'
!unzip '/content/dataset.zip' -d '/content/'
# Install the required packages for Ultralytics YOLO 8.3.166 and Weights & Biases
!pip install -U ultralytics wandb

# Enable W&B logging for Ultralytics
!yolo settings wandb=True
# check if ultralytics version is 8.3.166
import ultralytics
print(ultralytics.__version__)
import wandb
from google.colab import userdata

# Retrieve the WandB API key from Colab's user secrets
api_key = userdata.get('wandb-key')

# Log in to WandB
wandb.login(key=api_key)
from ultralytics import YOLO

# Initialize YOLO
yolo = YOLO()

# Enable W&B logging for Ultralytics
yolo.settings = {"wandb": True}

# Train YOLO11n model
## and zip and download the model
Common batch sizes that work well with GPU architectures are powers of two, such as 16, 32, 64, 128, ... 512. -1 for autobatch.

from ultralytics import YOLO
from google.colab import files

name = "yolo11n_25-09-01-224_e300" #@param {type:"string"}
project = "vespCV_acc" #@param {type:"string"}
epochs = 300 #@param {type:"integer"}
batch_size = -1 #@param {type:"integer"}
dataset_path = "/content/dataset/data.yaml" #@param {type:"string"}

# Get pre-trained model
model = YOLO("yolo11n.pt")

# Train/fine-tune model
model.train(data=dataset_path,
            epochs=epochs,
            patience=30,
            imgsz=224,
            batch=batch_size,
            optimizer="SGD",
            project=project,
            name=name)

# zip and download
!zip -r /content/{name}.zip /content/{project}
files.download(f'/content/{name}.zip')

---
