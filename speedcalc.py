'''
Geschwindigkeitsberechnung basierend auf physikalischen Kennzahlen.
Basierend auf http://www.kreuzotter.de/deutsch/speed.htm (Walter Zorn)

Für Nutzung in ArcGIS:
Umwandlung in Funktion, benötigte Daten hineinladen (Z_Start, Z_End, SLOPE)
Eigenschaften für Bike und Rider an Zielgruppe anpassen
'''

from math import atan, cos, sin, sqrt, exp, pow, acos

# Rider Properties
m_rider = 70 # --> je Altersklasse in kg
m_bike = 10 # --> je Altersklasse, z.B. woom
h_rider = 1.70 # je Altersklasse in m
power = 200 # in Watt --> je Altersklasse anpassen
cad = 90 # rpm trittgeschwindigkeit (cadence)

# Environment Properties
temp = 20 # celsius
altitude = 300 # int((Z_Start + Z_End)/2) statt 300
slope = atan(1 * 0.01) # SLOPE statt 1
wind_speed = 0 # vereinfachte annahme, nicht mit werten != 0 getestet

# Global Variables
CrDyn = 0.1 * cos(slope)
afCm = 1.025
afCdBike = 1.5

def CrEff():
    afLoadV = 0.4
    afCCrV = 1.0
    CrVH = 0.005 # Tourenreifen, CrV = CrH
    return afLoadV * afCCrV * CrVH + (1.0 - afLoadV) * CrVH

def CwaBike():
    afAFrame = 0.048
    afCATireV = 1.1
    afCATireH = 0.9
    ATireVH = 0.042  # Stirnfläche Reifen, ATireV = ATireH
    return afCdBike * (afCATireV * ATireVH + afCATireH * ATireVH + afAFrame)

def CwaRider():
    cCad = .002
    afSin = 0.89
    afCd = 0.89
    adipos = sqrt(m_rider/(h_rider*750))
    return (1 + cad * cCad) * afCd * adipos * (((h_rider - adipos) * afSin) + adipos)

def Frg():
    g = 9.81
    return g * (m_bike + m_rider) * (CrEff() * cos(slope) + sin(slope))

Ka = 176.5 * exp(-altitude * .0001253) * (CwaRider() + CwaBike()) / (273 + temp)
cardB = ((3 * Frg() - 4 * wind_speed * CrDyn) / (9 * Ka) - pow(CrDyn, 2) / (9 * pow(Ka, 2))
         - (wind_speed * wind_speed) / 9)
cardA = -((pow(CrDyn, 3) - pow(wind_speed, 3)) / 27
          + wind_speed * (5*wind_speed*CrDyn + 4*pow(CrDyn, 2) / Ka - 6*Frg()) / (18 * Ka)
          - power / (2*Ka*afCm) - CrDyn*Frg() / (6*pow(Ka, 2)))
sq = pow(cardA, 2) + pow(cardB, 3)

if sq >= 0:
    ire = cardA - sqrt(sq)
    if ire < 0:
        Vms = pow(cardA + sqrt(sq), 1. / 3.) - pow(-ire, 1. / 3.)
    else:
        Vms = pow(cardA + sqrt(sq), 1. / 3.) + pow(ire, 1. / 3.)
else:
    Vms = 2*sqrt(-cardB)*cos(acos(cardA/sqrt(pow(-cardB,3)))/3)

Vms -= 2*wind_speed/3 + CrDyn/(3*Ka)
# print(" Vkmh:", Vms*3.6, "\n", "Cr:", CrEff(), "\n", "Cd*A:", CwaRider() + CwaBike())
