**One-line purpose:** google cloudplatform access
**Short summary:** GCP login to train swift-yolo
**Agent:** 

---


Bijgaand de private key on in te loggen. Wachtwoord c.q. passphrase, tevens wachtwoord van de zipper zit je WhatsApp. 

De username is **django** op de server en op de CVAT website

- Installeer deze key in **<user home>/.ssh** (weet niet hoe dat op een Mac werkt 😉)
- Log in met iets als **ssh -i ~/.ssh/gcp-django** [**django@35.204.53.250**](mailto:django@35.204.53.250 "mailto:django@35.204.53.250")
- Binnen kun je de yolov5 container starten met: **/opt/myColab/start_yolov5.sh**
- De CVAT Annotatie site kun je bereiken via: [**http://35.204.53.250:8080/auth/login**](http://35.204.53.250:8080/auth/login "http://35.204.53.250:8080/auth/login")

In theorie is de server _rock solid_ en zou na reboots gewoon moeten werken.

Er is een forse installatie handleiding aan de hand waarvan het hele ding bewezen opgebouwd is.

Mocht je iets missen, wat wel structureel tot de machine hoort, dan hoor ik dat graag om dat toe te voegen

De machine kost €1/h en dus € 24/dag. Ik laat hem aan staan zodat jij kan kijken en testen.  
Als hij uit mag/kan dan app je maar even.

Ik zal nog uitzoeken hoe jij de server zelf kan starten/stoppen, afhankelijk van Google Cloud Platform IAM.

---


OK, probeer dit:

[https://console.cloud.google.com/compute/instances?project=eastwicktrader](https://console.cloud.google.com/compute/instances?project=eastwicktrader "https://console.cloud.google.com/compute/instances?project=eastwicktrader")

op de drie puntjes rechts achter de instance staat start en stop (suspend werkt niet)

Je zal moeten inloggen met je gmail.com account

In de console:

In de console:

[https://console.cloud.google.com/welcome?project=eastwicktrader&cloudshell=true](https://console.cloud.google.com/welcome?project=eastwicktrader&cloudshell=true "https://console.cloud.google.com/welcome?project=eastwicktrader&cloudshell=true")

# Set project  
gcloud config set project eastwicktrader

# Start / stop / check status

gcloud compute instances describe mycolab --zone=europe-west4-c --format="get(status)"  
  
gcloud compute instances start mycolab --zone=europe-west4-c    
gcloud compute instances stop mycolab --zone=europe-west4-c