
**One-line purpose:** yolo config.yaml format
**Short summary:** 
**Agent:** documentation

---


Make a config.yaml
```
path: /content/data # absolute path to images and annotation (relative path can give issues)
train: images/train # train images (relative to 'path')
val: images/val # val images (relative to 'path')

# Classes (adjust names to the class names if needed)
names:
  0: Vespa_velutina
  1: Vespa_crabro
  2: Vespula_vulgaris
```

Copy the config.yaml and the data.zip to google drive in folder vespCV


