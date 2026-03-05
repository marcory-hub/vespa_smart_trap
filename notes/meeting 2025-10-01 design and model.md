**One-line purpose:** meeting
**Short summary:** start design traject voor val, verbeteren detectie
**Agent:** archived

---

Conclusie voor overleg 2025-10-01

- YOLO11n 224x224 model voor object detection op de grove vision A1 V2
	- Training in colab, staat in github
	- Idem voor conversie van pt naar onnx naar tflite (in venv vw module imp die vanaf python 3.13 niet meer aanwezig is)
	- Vooral het verminderen van trainen op 640x640 naar 224x224 geeft performance drop
	- De webtool heeft in de code de classes van coco, dus die moeten handmatig worden aangepast
	- Er is detectie van de AH
	- Beperkingen
		- Confidence tussen .3 en .8 (ter vergelijking op rpi4 is dit tussen de .9 en 1)
		- Opnames niet geschikt voor verdere training —> kijken of het mogelijk om images in betere resolutie op te slaan?
		- Grotere images werken niet, bij 256x256
		- `Failed to resize buffer. Requested: 573696, available 443064, missing: 130632`
	- Vragen:
		- Zijn er nog opties om de detectie te verbeteren (eigenlijk zitten alle demo modellen op deze confidence range)
		- Verbeteren van detectie door opstelling van de camera en licht (nu camera binnen die van de zijkant/schuin boven op de bait kijkt) —> camera van boven is optimaler (zie opstelling in de pet-fles)
		- Verbeteren door toevoegen van geluid (is er verschil tussen geluid van de Vespa Crabro en Vespa velutina)
		- Is grove vision PDM (pulse dense modulation) voldoende om dit op te pikken

esp hoger resolutie

foto's van opstelling

artikel doorsturen


max opstelling waar hardware detector in kan
arjan esp
arjen programmeren? max check dit

design traject voor de val in workshop setup