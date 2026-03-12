**One-line purpose:** Index for vespa smart trap project with subindexes and quick access
**Short summary:** all subindexes and quick access links.
**Agent:** index for user
**Main Index:** [[_000]]

---

[[_timeline]] to do's and done

[[_meetings]], notes, online platforms, funding, mails, media

[[_datasets]], current dataset_vesp_2026-02 and earlier subsets

[[_model]], yolo8s, yolo11n, swift-yolo models (training config, results)

[[_hardware]], current stack gv2, lilygo-tsim7080-4g, and other tested hardware

[[_himax sdk]], Himax SDK for the Grove Vision AI platform. Inactive because flashing grove vision ai v2 is not as easy as flashing swift-yolo model from sensecraft.ai

[[_github]]
# Quick Access
- [[sharepoint]] - [sharepoint](https://imkersleiden.sharepoint.com/Gedeelde%20documenten/Forms/AllItems.aspx?id=%2FGedeelde%20documenten%2FHornet%20Trap%2FOntwerp%2FDraft%20system&p=true&ct=1750781064250&or=Teams%2DHL&ga=1&LOF=1) design, funding, rza login
- [[_cli_commands]] and  [[github cli commands]]

[[mails]] - ai authors, wallabiek, artez
[[example]]  -  trap designs, 3D printable examples

[[z_archive]]  -  Archive and deprecated notes 
![[vespCV.png]]

## Vespa Smart Trap: An AI-Powered Detection System for Asian Hornet Management

**Asian hornets are one of the greatest threats facing honeybee colonies today.**

To combat this, we’ve developed an autonomous AI detection system. Our technology provides:

- **Real-time Alerts:** Giving beekeepers the window they need to take immediate action.
    
- **Actionable Data:** Providing scientists with critical insights into the spread of this invasive species.



Vespa Smart Trap is an automated, edge-based computer vision system designed to detect and monitor _Vespa velutina_ (Asian yellow-legged hornet) infestations in real time. By combining custom-trained YOLO11 neural networks deployed on ultra-low-power Grove Vision AI V2 hardware (Himax WiseEye2), the system captures images, performs on-device inference, and transmits detection alerts via LTE connectivity (LilyGO T-SIM7080G-S3).

This allows beekeepers, conservation volunteers, and environmental authorities to:

- Detect invasive hornets at scale with mAP50 accuracy >0.97
- Minimize false positives through multi-species classification (Vespa velutina, Vespula sp., native wasps, NULL/background images)
- Deploy across geographies using modular hardware stacks (ONE / BASE / PRO configurations)
- Capture actionable intelligence for predation assessment and biocontrol interventions

### Why It Matters

_Vespa velutina_ is a highly invasive predator of honeybees, causing significant colony mortality and ecological disruption across Europe, Asia, and North America. Early detection and rapid response are critical for containment. Traditional trapping methods are labor-intensive, non-selective, and lack real-time visibility. Vespa Smart Trap automates monitoring.

### The Technical Stack

Edge Inference:

- **Grove Vision AI V2** (Himax A1, <2.4MB SRAM) running quantized YOLO11n (imgsz224, int8 + Vela hardware acceleration)
- Achieved Performance: mAP50 = 0.9779, mAP50-95 = 0.8064; per-species recall: Vespa velutina 0.7862, Vespula sp. 0.8345
- Inference: <500ms per frame at 1MP resolution

Cloud Connectivity & Logic:

- LilyGO T-SIM7080G-S3 (**ESP32-S3** with integrated LTE modem)
- UART-based packetization for bidirectional detection streaming and configuration

Training Pipeline:

- Colab-based Swift-YOLO for easy flashing from sensecraft.ai
- Dataset: 116,540+ annotated images across 4 classes; preprocessing via Roboflow with augmentation
- Versioning: 4 dataset iterations (v1–v4) tested; YOLOv11n, YOLOv26n benchmarked

Model Deployment:

- SenseCraft AI for simplified on-device flashing
- Himax SDK fork for low-level optimization and debugging
- Validated architecture: Multi-output models prioritized (2/3 compatibility); oversized single-output models eliminated via systematic validation framework (6 test scripts)

---

### Why This Matters for Stakeholders

- Beekeepers: Real-time alerts to defend hives during peak predation season
- Environmental agencies: Scalable, evidence-based monitoring for invasive species management
- Researchers: Reproducible, structured data for published analysis of invasive predator dynamics
- Conservation teams: Cost-effective early detection supporting rapid biocontrol interventions



#AIforGood #EdgeAI #Beekeeping #AsianHornet #InvasiveSpecies #Beelife #TechForGood #NatureTech