'''
Geschwindigkeitsberechnung basierend auf physikalischen Kennzahlen.
Basierend auf http://www.kreuzotter.de/deutsch/speed.htm (Walter Zorn)

Für Nutzung in ArcGIS:
Konstanten für Gewichte, Körperhöhe und Power Output festlegen und aus Funktionsdefinition entfernen
d. h. gew_r, gew_b, h_r, p_r
return statement tauschen durch die auskommentierte Variante
'''

from math import atan, cos, sin, sqrt, exp, pow, acos
from numpy import cbrt, float64
def speedcalc(slp, length, gew_r, gew_b, h_r, p_r):
    # Rider Properties
    m_rider = gew_r # 40 # --> je Altersklasse in kg
    m_bike = gew_b # 10 # --> je Altersklasse, z.B. woom
    h_rider = h_r # 1.45 # je Altersklasse in m
    power = p_r # 100 # in Watt --> je Altersklasse anpassen
    cad = 90 # rpm trittgeschwindigkeit (cadence)

    # Environment Properties
    temp = 20 # celsius
    altitude = 250 # int((Z_Start + Z_End)/2) statt 300
    slp = atan(slp * 0.01) # SLOPE statt 1
    wind_speed = 0 * .27778 # rückenwind = negative werte

    # Global Variables
    CrDyn = 0.1 * cos(slp)
    afCm = 1.025
    afCdBike = 1.5

    # CrEff
    afLoadV = 0.4
    afCCrV = 1.0
    CrVH = 0.005  # Tourenreifen, CrV = CrH
    CrEff = afLoadV * afCCrV * CrVH + (1.0 - afLoadV) * CrVH

    # CwaBike
    afAFrame = 0.048
    afCATireV = 1.1
    afCATireH = 0.9
    ATireVH = 0.042  # Stirnfläche Reifen, ATireV = ATireH
    CwaBike = afCdBike * (afCATireV * ATireVH + afCATireH * ATireVH + afAFrame)

    # CwaRider
    cCad = .002
    afSin = 0.89
    afCd = 0.89
    adipos = sqrt(m_rider / (h_rider * 750))
    CwaRider = (1 + cad * cCad) * afCd * adipos * (((h_rider - adipos) * afSin) + adipos)

    # Frg
    g = 9.81
    Frg = g * (m_bike + m_rider) * (CrEff * cos(slp) + sin(slp))

    Ka = 176.5 * exp(-altitude * .0001253) * (CwaRider + CwaBike) / (273 + temp)
    cardB = ((3 * Frg - 4 * wind_speed * CrDyn) / (9 * Ka) - pow(CrDyn, 2) / (9 * pow(Ka, 2)) - (
                wind_speed * wind_speed) / 9)
    cardA = -((pow(CrDyn, 3) - pow(wind_speed, 3)) / 27 + wind_speed * (
                5 * wind_speed * CrDyn + 4 * pow(CrDyn, 2) / Ka - 6 * Frg) / (18 * Ka) - power / (
                          2 * Ka * afCm) - CrDyn * Frg / (6 * pow(Ka, 2)))
    sq = pow(cardA, 2) + pow(cardB, 3)

    # calculate velocity
    if sq >= 0:
        ire = cardA - sqrt(sq)
        if ire < 0:
            Vms = cbrt(cardA + sqrt(sq)) - cbrt(-ire)
        else:
            Vms = cbrt(cardA + sqrt(sq)) + cbrt(ire)
    else:
        Vms = 2*sqrt(-cardB)*cos(acos(cardA/sqrt(pow(-cardB,3)))/3)

    Vms -= 2*wind_speed/3 + CrDyn/(3*Ka)
    Vms = float64(Vms)
    Vms = Vms.item()
    # return round((length / Vms / 60),3), round((Vms * 3.6), 3)
    return f"Fahrzeit: {round((length / Vms / 60),3)} min, Geschindigkeit: {round((Vms * 3.6), 3)} km/h"


# basic output
print(speedcalc(slp=-5, length=1000, gew_r=70, gew_b=10, h_r=1.7, p_r=200))
