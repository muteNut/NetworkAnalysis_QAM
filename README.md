# Netzwerkanalyse
## Vorgehensweise
Allgemeine Methodologie für die Berechnung
### Vorbereitung
Vorbereitung vom Datensatz in mehreren Schritten
#### Gefälle für Bike-Network berechnen

| Schritt | Beschreibung | Screenshot |
|-|-|-|
| 1 | Herunterladen der [DTM-Rasterzellen](https://doi.org/10.48677/5b510b4a-f592-4c02-991f-012cb1a65ea9) | |
| 2 | Rasterzellen simplifizieren (*Focal Statistics, 10x10m mean*) | <img src="img/focal.png" alt="Screenshot vom Tool Focal Statistics mit Cell Size = 10" width="300"/> |
| 3 | Zusammenfügen der Rasterzellen (*Mosaic to New Raster*) | <img src="img/mosaic.png" alt="Screenshot vom Tool Mosaic to New Raster" width="300"/> |
| 4 | Extrahieren der Start- und Endpunkte (*Feature Vertices To Points*) <br> Layer mit Start Nodes <br> Layer mit End Nodes | <img src="img/vertices.png" alt="Screenshot vom Tool Feature Vertices To Points" width="300"/> |
| 5 | Projizieren der Start- und End-Nodes auf DTM-Rasterzellen (*Extract Multi Values to Points*) | <img src="img/extract.png" alt="Screenshot vom Tool Extract Multi Values to Points" width="300"/> |
| 6 | Join an Linknetz (*Join Field, FROM-Node, TO-Node*) | <img src="img/join.png" alt="Screenshot vom Tool Join Field" width="300"/> |
| 7 | Gefälle berechnen: (!Z_TO! - !Z_FROM!) / !Shape_Length! x 100 | <img src="img/field_calc.png" alt="Screenshot vom Field Calculator" width="300"/> |

#### Bike Network bauen
##### Costs (non-physical):
Dritte Wurzel von Slope in Verbindung mit Distanz, Base Speed = 20 km/h. Die Ausreißer jenseits von 25% Gefälle werden bereinigt.
Eine [realitätsnähere Berechnungsmethode](#physikalisches-modell) ist ebenso möglich.

**Towards:**
```python
from math import pow

def time(slope, length):
    speedmm = 20 * 1000 / 60  # km/h in m/min
    slope = max(-25, min(25, slope))  # Begrenzung
    if slope < -1:
        v = speedmm * pow(abs(slope), 1./3)
    elif slope >= -1 and slope <= 1:
        v = speedmm
    else:
        v = speedmm / pow(abs(slope), 1./3)
    return length / v  # t = s / v (in m/min)
```

**Backwards:**
```python
from math import pow

def time(slope, length):
    speedmm = 20 * 1000 / 60 # km/h in m/min
    slope = max(-25, min(25, slope))  # Begrenzung
    if slope < -1:
        v = speedmm / pow(abs(slope), 1./3)
    elif slope >= -1 and slope <= 1:
        v = speedmm
    else:
        v = speedmm * pow(abs(slope), 1./3)
    return length / v # t = s / v (in m/min)
```
Die Geschwindigkeit und Fahrzeit verteilt sich daher abhängig vom Gefälle wie folgt:

<img src="img/times.png" alt="Diagramm von Fahrzeit und Geschwindigkeit auf y-Achse, Gefälle auf x-Achse" width="500"/>

Für Fahrtrichtung Backwards ist die Funktion umgekehrt.

#### Physikalisches Modell
Das Diagramm zeigt den Vergleich zwischen dem vereinfachten Modell mit Wurzelfunktion und einem physikalischen Modell nach [Walter Zorn](http://kreuzotter.de/deutsch/speed.htm). Als Parameter wurde eine Gesamtmasse von 80kg bei Körperhöhe von 1.70m und einer Leistung von 200 Watt bei einer Kadenz von 90 rpm gewählt. Für Luft- und Rollwiderstandswerte wurde ein Rennrad bei aufrechter Sitzposition mit Tourenreifen (*vgl. Gravelbike*) angenommen. Die Seehöhe wird vereinfacht mit konstant 250m gleichgesetzt, die Windgeschwindigkeit mit 0 km/h.

<img src="img/phys_times.png" alt="Diagramm von Fahrzeit und Geschwindigkeit auf y-Achse, Gefälle auf x-Achse. Überlagerung mit dem vereinfachte Modell (Wurzelfunktion)" width="500"/>

Das [Script](speedcalc.py) kann in ArcGIS geladen werden. Für die Fahrtrichtung *backwards* muss nur das Vorzeichen von *Slope* umgekehrt werden. Parameter wie z.B. Gewicht müssen in der Funktion als Konstante definiert sein. Die Definition von *value* ist:
```
speedcalc(!SLOPE!, !Shape_Length!, !Z_Start!, !Z_End!)
```
##### Kennzahlen für Zielgruppen (physical model)
Die Parameter wurden grob abgeschätzt.
Die Kennzahlen für Körperhöhe und Gewicht sind Mittelwerte [dieser Tabelle](https://www.atlasrepos.ch/gewicht-kinder/), die Berechnung der Leistung basiert auf dem mittleren FTP (W/kg) im Profil *fair* von [Polar](https://support.polar.com/ch-de/ftp-class-table). Masse des Rads wird mit konstant 10 kg angenommen. Für den täglichen Pendelweg wird eine Leistung von 60% des FTP angenommen, in der Tabelle sind die absoluten Werte angeführt.
| Alter | Größe `[m]` | Gewicht `[kg]` | Leistung `[W]` |
|-|-|-|-|
| 5 - 9 | 1.27 | 27 | 66.3 |
| 10 - 14 | 1.56 | 48.7 | 119.2 |
| 15 - 19 | 1.71 | 67 | 163 |

##### Restrictions:
Befahrbarkeit für Fahrrad erlaubt (Realitätsnähe?)

**Towards:**
```python
def restriction(bike):
	if bike == 1:
		return False
	else:
		return True
```
**Backwards** ist das Field Script identisch, nur die Variable wird getauscht: statt *AccTow_Bike* wird *AccBkw_Bike* eingesetzt.

#### DEM & ERW vorbereiten
1. Pairwise Clip von DEM-Rasterdatensatz mit Region
2. Pairwise Clip von Statistikraster (Poly) mit Region
3. DEM: Summieren von Altersgruppen m+w
	- Altersgruppe 1: 5 bis 9-jährige
	- Altersgruppe 2: 10 bis 14-jährige
	- Altersgruppe 3: 15 bis 19-jährige
	- Löschen aller unbenötigten Spalten
	
#### Zusätzliche Layer laden & vorbereiten
1. [Administrative Grenzen](https://www.data.gv.at/katalog/de/dataset/stat_gliederung-osterreichs-in-gemeinden14f53)
	- Bundesländer vereinfacht (*Simplify Polygon, Algorithm Wang-Müller, Tolerance 500 m*)
	- Gemeinden
2. [Flüsse](https://www.data.gv.at/katalog/de/dataset/gesamtgewssernetzfliessgewsserrouten)
	- nach Flussmenge eingefärbt
3. [Waldfläche](https://www.data.gv.at/katalog/de/dataset/waldkarte-bfw-osterreich)

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
- Cutoff: 15km, dann Zuschlag je eine Minute am Quell- und Zielort und filtern nach 30 Minuten Fahrzeit.
- Darstellung von erreichbaren Rasterzellen (!), daher auf Grundlage von O-D-Matrize ausarbeiten
### Fahrzeit zur nächsten Schule je Rasterzelle
- Auf Basis von O-D-Matrize, nur Rang 1
- Darstellung auf Rasterebene
### Anzahl erreichbarer Schulen in Zeitraum
- in unter [27 Minuten](https://www.statistik.at/statistiken/arbeitsmarkt/erwerbstaetigkeit/arbeitsort-und-pendeln)
- Auf Basis von O-D-Matrize, Join mit Rasterzellen
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

Anschließend Vergleich mit O-D ohne Gefälle (Delta).
