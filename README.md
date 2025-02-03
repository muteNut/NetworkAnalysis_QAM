# Netzwerkanalyse
## Vorgehensweise
Allgemeine Methodologie für die Berechnung
### Vorbereitung
Vorbereitung vom Datensatz in mehreren Schritten
#### Gefälle für Bike-Network berechnen
1. Herunterladen der [DTM-Rasterzellen](https://doi.org/10.48677/5b510b4a-f592-4c02-991f-012cb1a65ea9)
2. Zusammenfügen der Rasterzellen (*Mosaic to New Raster*)
3. Rasterzellen simplifizieren (*Focal Statistics, 10x10m mean*)
4. Extrahieren der Start- und Endpunkte (*Feature Vertices To Points*)
	- Layer mit Start Nodes
	- Layer mit End Nodes
5. Projizieren der Start- und End-Nodes auf DTM-Rasterzellen (*Extract Multi Values to Points*)
6. Join an Linknetz (*Join Field, FROM-Node, TO-Node*)
7. Gefälle berechnen: (Z_TO - Z_FROM) / !Shape_Length! x 100

#### Bike Network bauen
1. Costs:
Dritte Wurzel von Slope in Verbindung mit Distanz, Base Speed = 20 km/h. Die Ausreißer jenseits von 25% Gefälle werden bereinigt. 

**Towards:**
```python
from math import pow
def time(slope, length):
    speed = 20 # km/h
    speedmm = speed * 1000 / 60 # in m/min
    if slope > 25: # ausreisser bereinigen
        slope = 25
    elif slope < -25:
        slope = -25

    if slope < 0: #-2:
        v = speedmm * pow(abs(slope), 1/3)
        return length / v # t = s / v (in m/min)
    elif slope == 0: #>= -1 and slope <= 1:
        v = speedmm
        return length / speedmm # t = s / v (in m/min)
    else:
        v = speedmm / pow(slope, 1/3)
        return length / v # t = s / v (in m/min)
```
**Backwards:**
```python
from math import pow
def time(slope, length):
    speed = 20 # km/h
    speedmm = speed * 1000 / 60 # in m/min
    if slope > 25: # ausreisser bereinigen
        slope = 25
    elif slope < -25:
        slope = -25

    if slope < 0: #-2:
        v = speedmm / pow(abs(slope), 1/3)
        return length / v # t = s / v (in m/min)
    elif slope == 0: #>= -1 and slope <= 1:
        v = speedmm
        return length / speedmm # t = s / v (in m/min)
    else:
        v = speedmm * pow(slope, 1/3)
        return length / v # t = s / v (in m/min)
```
2. Restrictions:
Befahrbarkeit für Fahrrad erlaubt (realitätsnähe?)

**Towards:**
```python
def restriction(bike):
	if bike == 1:
		return False
	else:
		return True
```
**Backwards:**
```python
def restriction(bike):
	if bike == 1:
		return True
	else:
		return False
```

#### DEM & ERW vorbereiten
1. Pairwise Clip von DEM-Rasterdatensatz mit Region
2. Pairwise Clip von Statistikraster (Poly) mit Region
3. DEM: Summieren von Altersgruppen m+w
	- Altersgruppe 1: 5 bis 9-jährige
	- Altersgruppe 2: 10 bis 14-jährige
	- Altersgruppe 3: 15 bis 19-jährige
	- Löschen aller unbenötigten Spalten
	
#### Zusätzliche Layer laden & vorbereiten
1. Administrative Grenzen
	- Bundesländer vereinfacht (*Simplify Polygon, Algorithm Wang-Müller, Tolerance 500 m*)
	- Gemeinden
2. Flüsse
	- nach Flussmenge eingefärbt
3. Waldfläche

### Import von Zielen
* Öffentliche Schulen nach [Bildungsstufe](https://de.wikipedia.org/wiki/Bildungssystem_in_%C3%96sterreich#/media/Datei:SCHULSYSTEM%C3%B6sterreich2.png)
	- Primärstufe:
		- VS (Volksschule)
		- SS (Sonderschule)
	- Sekundarstufe 1:
		- NMSA (Mittelschule AHS)
		- NMSH (Mittelschule)
		- SS (Sonderschule)
	- Sekundarstufe 2:
		- AHS
		- BMHSK
		- BMHSP
		- BMHST
		- BS
		- LFHS
		- PS

## Maps
In den Maps wird nur exemplarisch eine Bildungsstufe dargestellt, z.B. Sekundarstufe 1

### Einzugsbereiche je Schultyp
- Cutoffs noch festzulegen
- Darstellung von erreichbaren Rasterzellen (!), daher auf Grundlage von O-D-Matrix ausarbeiten
### Fahrzeit nur nächsten Schule je Rasterzelle
- Auf Basis von O-D-Matrix, nur Rang 1
- Darstellung auf Rasterebene
### Anzahl erreichbarer Schulen in Zeitraum
- noch festzulegen, z.B. in unter 30 Minuten
- Auf Basis von O-D-Matrix, Join mit Rasterzellen
- Darstellung auf Rasterebene
### Mittlere Reisedauer je Gemeinde
- gew. nach Bevölkerung und Schultyp: Zuweisung von Rastermittelpunkt zu Gemeinde, Weg zu nächster Schule; Aggregieren auf Gemeindeebene mit betr. Bevölkerung (Kinder)
- Darstellung auf Gemeindeebene
### Gravitationsbasiertes Potenzial
- Darstellung je Einrichtung
- entweder HWS oder Kinder, die Schultyp zugeordnet werden.

  | Variable      | Bedeutung                          |
  |---------------|------------------------------------|
  | $` A_j `$     | Anzahl Kinder oder Hauptwohnsitze  |
  | $` t_{ij} `$  | Reisezeit |
  | $` \lambda `$ | Halbwertszeit |

Die Formel dafür lautet:\
  $P = \sum_{j=1}^{n} A_j \cdot e^{\beta \cdot t_{ij}}$
wobei
  $\beta = \frac{\ln(2)}{\lambda_t}$

### Vergleichende Darstellung bei konstanter Geschwindigkeit (?)
  Eventuell machen, vielleicht weglassen
## Diagramme
Wie Maps, aber für alle Bildungsstufen: Diagramm mit y = Zielgruppe, x = Zeitklasse
### Base Speed anpassen 

| Bildungsstufe | Geschwindigkeit |
|---------------|-----------------|
| Primär | 12 km/h |
| Sekundär 1 | 16 km/h |
| Sekundär 2 | 20 km/h |

Anschließend Vergleich mit O-D ohne Gefälle.
