**One-line purpose:** information about dataset_vespa_2026-02
**Short summary:** information about structure, preprocessing and augmentation to the dataset_vespa_2026-02
**Agent:** specifications of dataset_vespa_2026-02 versions
**Main Index:** [[_000]]

---


2026-03-01:
- NULL images were added to the datasetsv1
- backup naar SSDs

2026-03-01: 
- added train-valid dataset for quantization
- backup naar SSDs

2026-02:
## v1: no preprocessing, no augmentation
dataset: 
subsets:
allpx: 38847 pairs -> train=33020 valid=5439 test=388
30px: annotations smallere than 30px when scaled to 192px are removed (estimated size of a bee) [[dataset pixelsize raspberry cam 1.3 at 10 cm]]
40px: annotations smallere than 40px when scaled to 192px are removed 
60px: annotations smallere than 60px when scaled to 192px are removed (estimated size of a hornet)

## v2: 192, no augmentation
## v3: no preprocessing, augmentation
- Augmentation is done by swift and yolo ultralytics, no additional value. Increases dataset size 3x.
## v4: 192 and augmentation