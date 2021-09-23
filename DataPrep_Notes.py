# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 11:58:15 2021

@author: NCG
"""

"""Data Prep"""

#nmi_ij
# STN         LON(east)   LAT(north)  ALT(m)      NAME				
# 225         4.555       52.463      4.40        IJmuiden    				
# 240         4.790       52.318      -3.30       Schiphol   # we picked for most complete data 				
# 242         4.921       53.241      10.80       Vlieland    				
# 310         3.596       51.442      8.00        Vlissingen  				
# 344         4.447       51.962      -4.30       Rotterdam   				
# 380         5.762       50.906      114.30      Maastricht  				
  	
# FH        Hourly mean wind speed (in 0.1 m/s)	-  Uurgemiddelde windsnelheid (in 0.1 m/s). Zie http://www.knmi.nl/kennis-en-datacentrum/achtergrond/klimatologische-brochures-en-boeken / 
# FF        Mean wind speed (in 0.1 m/s) during the 10-minute period preceding the time of observation	/ : Windsnelheid (in 0.1 m/s) gemiddeld over de laatste 10 minuten van het afgelopen uur / 
# Temp      Temperature (in 0.1 degrees Celsius) at 1.50 m at the time of observation	/ : Temperatuur (in 0.1 graden Celsius) op 1.50 m hoogte tijdens de waarneming / 
# GHI       Global radiation (in J/cm2) during the hourly division	/  Globale straling (in J/cm2) per uurvak 