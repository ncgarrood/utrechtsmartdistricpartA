# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 12:27:16 2021

@author: NCG
"""

import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import pvlib
import numpy as np

from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score

""" Question 1 - Model Testing """

# Location
latitude, longitude = 52.08746136865645, 5.168080610130638 # used long/lat from googlemaps for uithof

MODELS = ['disc', 'dirint', 'dirindex','erbs']

# Functions
def find_dni(model, ghi, solar_position):
    """Return a DNI series based on the model, ghi, and solar position"""
    time = UPOT_data.index
    ghi = UPOT_data.GHI
    zenith = solar_df['zenith']
    apparent_zenith = solar_df['apparent_zenith']
    
    if model == 'disc':
        return pvlib.irradiance.disc(ghi, zenith, time).dni
    if model == 'dirint':
        return pvlib.irradiance.dirint(ghi, zenith, time)
    if model == 'dirindex':
        relative_airmass = pvlib.atmosphere.get_relative_airmass(apparent_zenith)
        absolute_airmass = pvlib.atmosphere.get_absolute_airmass(relative_airmass)
        linke_turbidity = pvlib.clearsky.lookup_linke_turbidity(time, latitude, longitude)
        clearsky = pvlib.clearsky.ineichen(apparent_zenith, absolute_airmass, linke_turbidity, perez_enhancement=True)
        return pvlib.irradiance.dirindex(ghi, clearsky['ghi'], clearsky['dni'], zenith=zenith, times=time)
    if model == 'erbs':
        return pvlib.irradiance.erbs(ghi, zenith, time).dni
    raise Exception('Invalid model')

def print_errors(rmse, mbe, mae, r2):
    print('{} RMSE: {}, MBE: {}, MAE: {}, R2: {}'
        .format(model.upper().ljust(8),       
            rmse,
            mbe,
            mae,
            r2))
        
def compare_dni(model, true_value, predicted_value):
     """Print the RMSE, MBE, MAE, R2 for UPOT data series compared to model values"""
     rmse = round(((mean_squared_error(true_value, predicted_value)) ** 0.5),3)
     mbe = round((true_value - predicted_value).mean(),3)
     mae = round(mean_absolute_error(true_value, predicted_value),3)
     r2 = round(r2_score(true_value, predicted_value),3)
     print_errors(rmse,mbe,mae,r2)
     
# Get Irrandiance (UPOT data GHI) and solar angles (Zenith and Apparent Zenith)
UPOT_data = pd.read_csv(r"C:\Users\NCG\OneDrive\Documents\Utrecht University\Energy in Built\6.2 Photovoltaic (PV) systems, irradiance and PV performance evaluation\PVpartA\Irradiance_2015_UPOT.csv", sep = ';', index_col = "timestamp", parse_dates= True) 
#UPOT_data = UPOT_data.resample("5min").mean()
#UPOT_data = UPOT_data.dropna()

solar_df = pvlib.solarposition.ephemeris(UPOT_data.index, latitude, longitude, temperature= UPOT_data["temp_air"])
solar_df= solar_df[solar_df.elevation > 4] #hours when enough sun to not be neglible generation, avoiding inf values in dirindex later

UPOT_data = UPOT_data[UPOT_data.index.isin(solar_df.index)]

#Calculate the Models and compare to observed GHIs from UPOT dataset
for model in MODELS:
    modelled_dni = find_dni(model, UPOT_data, solar_df)
    UPOT_data[model] = modelled_dni
    compare_dni(model, UPOT_data.DNI, modelled_dni)
#%%    
### GRAPHS for Sub-Question 3

fig, axs = plt.subplots(2, 2)
#formatting
fig.subplots_adjust(wspace = 0.2, hspace = 0.3)

for index, model in enumerate(MODELS):
    subplot = axs[index//2][index % 2]
    subplot.scatter(UPOT_data.DNI, UPOT_data[model], s=0.0005, c= 'lightcoral')
    subplot.set_title(model.upper())
    subplot.set(xlabel='True DNI [W/m2]', ylabel='Modelled DNI [W/m2]')
    subplot.plot([0,999],[0,999], c = 'gray', linewidth = 1)


#%%
""" Question 2 - Irradiance on building surfaces """

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

knmi = pd.read_csv('knmi_ij_sch_vlie_vlis_rott_maas.csv', index_col = "STN", sep = ';',  parse_dates = True)
    #set empty rows to NaN
knmi = knmi.replace(r'\s+', np.nan, regex = True)
    #delete all rows with NaN
knmi = knmi.dropna()
    #change column names
knmi = knmi.rename({"H": "Hour", knmi.columns[4]: "Temperature", knmi.columns[5]: "GHI", knmi.columns[2]: "FH", knmi.columns[3]: "FF"  }, axis = 'columns')

#keep rows of certain STN value
knmi = knmi.loc[(knmi.index == 240)] #keep data coming from weather station Schiphol. 

#resample time
    #add a column with corresponding date time from 1/1/2019 01:00:00 (because dataset starts with Hour 1), of extent of the datafrime and per hourly frequency. 
knmi['Date'] = pd.date_range(start = '1/1/2019 01:00:00', periods = len(knmi), freq = 'H')
    #remove the YYMMDD and Hour columns from dataframe 
knmi = knmi.drop(['YYYYMMDD', 'Hour'], axis = 1)
    #put the 'date' column at the first place in the dataframe
knmi = knmi[[ 'Date', 'FH', 'FF', 'Temperature', 'GHI']]   

#change GHI from j/cm2 per  hour to W/m2
knmi['GHI_W/M2'] = pd.to_numeric(knmi.GHI) * 10000 /3600

### SUB-QUESTION 2.2

hu