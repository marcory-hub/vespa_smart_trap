
# 2025-04-18

Beste Jelle, Doeke en Sjoerd,

Doeke, bedankt voor je reactie. Jelle, geniet van de mooie tijd, ik hoop dat je niet alleen naar Marokko fietst maar ook tijd hebt om het land zelf te bezoeken. Sjoerd, wat een toeval dat je ook bekend bent in de bijenwereld.

Fijn dat er wellicht mogelijkheden zijn om de hoornaarsdetector van pilot naar bruikbare versie te ontwikkelen. Laat me het project wat concreter toelichten:

Het project betreft een open-source oplossing voor imkers om Aziatische hoornaars te detecteren. De technische kern bestaat uit:
- Een YOLO (You Only Look Once) model voor real-time detectie van hoornaars (momenteel YOLOv8 en YOLOv10, met YOLOv11 training in de planning)
- Een Raspberry Pi 4 (4GB) als minimale basis voor de hardware
- Automatische foto-opslag voor meldingen op waarnemingen.nl
- GPIO-integratie voor het aansturen van een elektrische harp (dit deel wordt verder ontwikkeld door een Belgische imker/ingenieur die het harpmodel heeft verbeterd)
- Een gebruiksvriendelijke interface voor imkers

Huidige status:
- Functionerende testscripts (ik heb 2 korte filmpje met testopstelling toegevoegd voor het idee wat het doet)
- Werkende opstelling met Pi en powerbank in vogelnestkast voor buitengebruik
- Doel: ontwikkeling naar een 'plug & play' versie die 6 uur autonoom kan werken in het veld

Waar ik specifiek ondersteuning bij zoek is het python code deel:
1. Het opzetten van een goed gestructureerde codebase met duidelijke architectuur
2. Het ontwikkelen van een intuïtieve gebruikersinterface

Graag hoor ik van jullie of dit binnen jullie mogelijkheden valt en welke vorm van ondersteuning het beste zou passen.

Met vriendelijke groet,
Marcory


---

Beste Marcory,

Bedankt voor je bericht. Jelle heeft op het moment een sabbatical en
fietst naar Marokko, vandaar dat ik de mail even oppak. Hij zal de mail
waarschijnlijk wel lezen binnenkort.

Het project om hoornaars te detecteren met computer vision klink super
interessant, zeker als deze iets kan triggeren in bijenkasten om ze te
beschermen. Ik heb mijn collega Sjoerd Mol ook toegevoegd in de CC, hij
vervangt dit academiejaar Jelle en heeft zelf onlangs een imkercursus
afgerond en een aantal bijenvolken. Hij is bekend met de problemen die
de Aziatische hoornaar veroorzaakt.

Helaas kunnen we als HSLab niets betekenen omdat we een interne
werkplaats voor studenten van ArtEZ zijn. Wel hebben zowel Jelle, Sjoerd
en ik alle drie een eigen praktijk waarin we dit soort opdrachten kunnen
aannemen. Wellicht kunnen we op die manier iets voor jullie betekenen?

Ik hoor het graag.

Met vriendelijke groet,

Doeke Wartena


Beste Jelle en Doeke,

Zeven dagen geleden heb ik Jelle onderstaand bericht gestuurd met een vraag over de toegankelijkheid van het SHlab voor niet-studenten en een mogelijk samenwerkingsproject rond een computer vision-toepassing voor de detectie van Aziatische hoornaars.
Omdat ik tot op heden nog geen reactie heb ontvangen, wilde ik vriendelijk informeren of mijn mail goed is aangekomen. Ik hoor heel graag of dit project binnen de mogelijkheden van het SHlab valt en of jullie wellicht interesse of tijd hebben om mee te denken.

Alvast dank voor de moeite, ik zie je reactie met belangstelling tegemoet!

Met vriendelijke groet,

Marcory


Op wo 9 apr 2025 om 13:18 schreef Marcory van Dijk <marcoryvandijk@gmail.com>:
Beste Jelle,

Ik heb een vraag: Is het SHlab ook toegankelijk voor niet-studenten?

Zo ja, dan zou ik graag je hulp willen inroepen voor een project waarbij ik computer vision toepas op een Raspberry Pi. Het project betreft een Aziatische hoornaars detector die:
- Foto's maakt van de hoornaars
- Deze foto's opslaat voor meldingen op waarnemingen.nl
- Een elektrische harp kan activeren om bijenkasten te beschermen tegen deze invasieve exoot (Dit stukje neemt een ingenieur voor zijn rekening)

Ik heb al een pilot opstelling gemaakt, maar zou graag gebruikmaken van de expertise en faciliteiten van het SHlab om dit verder te ontwikkelen. Het gaat dan om het maken van een gebruiksvriendelijk open source product voor imkers dat liefst plug & play in het veld kan werken.

Ik hoor graag van je of dit project binnen de mogelijkheden van het SHlab valt.

Met vriendelijke groet,

Marcory




Beste Jelle, Doeke en Sjoerd,

Bedankt voor jullie reactie. Ik begrijp dat het SHlab zelf niet toegankelijk is voor niet-studenten, maar dat jullie wel mogelijkheden zien om als individuele professionals te ondersteunen. Laat me het project wat concreter toelichten:

Het project betreft een open-source oplossing voor imkers om Aziatische hoornaars te detecteren en bijenkasten te beschermen. De technische kern bestaat uit:
- Een YOLO (You Only Look Once) model voor real-time detectie van hoornaars
- Een Raspberry Pi als basis voor de hardware
- Een gebruiksvriendelijke interface voor imkers
- Automatische foto-opslag voor meldingen op waarnemingen.nl

De software zal volledig open-source worden ontwikkeld, zodat imkers en ontwikkelaars kunnen bijdragen aan de verbetering ervan.

Waar ik specifiek ondersteuning bij zoek is:
1. Het opzetten van een goed gestructureerde codebase met duidelijke architectuur
2. Het ontwikkelen van een intuïtieve gebruikersinterface
3. Het implementeren van best practices voor software-ontwikkeling
4. Code review en optimalisatie van de bestaande implementatie

Zouden jullie als individuele professionals bereid zijn om hierin te adviseren of te ondersteunen? Ik denk dan aan een aantal sessies waarin we de code kunnen bespreken en verbeteren.

Ik hoor graag van jullie of dit binnen jullie mogelijkheden valt en welke vorm van ondersteuning het beste zou passen.

---


