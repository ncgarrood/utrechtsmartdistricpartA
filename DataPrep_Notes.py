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


##Rooftops
#Building C and D --> it has two rooftops South and North
#CS 
    #orientation (azimuth) = 180 degrees
    #slope = 40 degrees 
#CN
    #orientation (azimuth) = 0 degrees
    #slope = 40 degrees  
#DW
    #orientation(azimuth) = 270 degrees
    #slope =  40 degrees
#DE
    #orientation (azimuth)= 90 degrees
    #slope =  40 degrees 

#Facades, A and B ((exclude façades facing North, NE & NW))
#ASE
    #orientation(azimuth) = 135
    #slope = 90
#ASW
    #orientation(azimuth) = 225 
    #slope = 90 
#BE 
    #orientation(azimuth) = 90
    #slope = 90
#BS
    #orientation(azimuth) = 180
    #slope = 90
#BW
    #orientation(azimuth) = 270
    #slope = 90
    
"""   
SurfaceASE - Tilt, Orientation
SurfaceASW - Tilt, Orientation
SurfaceBE  - Tilt, Orientation
SurfaceBS  - Tilt, Orientation
SurfaceBW  - Tilt, Orientation
RoofCS     - Tilt, Orientation
RoofCN     - Tilt, Orientation
RoofDW     - Tilt, Orientation
RoofDE     - Tilt, Orientation
RoofA      - Tilt = ?, Orientation = ?
RoofB      - Tilt = ?, Orientation = (??)
"""

###buildings = {'FacadeASE': [90,135], 'FacadeASW': [90,225], 'FacadeBE': [90,90], 'FacadeBS': [90,180], 'FacadeBW': [90,270], }

tilts = [90, 90, 90, 90, 90, 40, 40, 40, 40, 0, 0]
orientations = [135, 225, 90, 180, 270, 180, 0, 270, 90, 0, 0]

buildings = []

def create_building_dict(surface):
    for value in surface:
        buildings = tilts[] + orientations[]

#surfacelist=["SurfaceASE","SurfaceASW","SurfaceBE","SurfaceBS", ]

#mydict = {x: some_function(x) for x in surfacelist}