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
latitude_UU, longitude_UU = 52.08746136865645, 5.168080610130638 # used long/lat from googlemaps for uithof

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
        linke_turbidity = pvlib.clearsky.lookup_linke_turbidity(time, latitude_UU, longitude_UU)
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
UPOT_data = pd.read_csv("Irradiance_2015_UPOT.csv", sep = ';', index_col = "timestamp", parse_dates= True) 
#UPOT_data = UPOT_data.resample("5min").mean()
#UPOT_data = UPOT_data.dropna()

solar_df = pvlib.solarposition.ephemeris(UPOT_data.index, latitude_UU, longitude_UU, temperature= UPOT_data["temp_air"])
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
    subplot.set(xlabel='Observed DNI [W/m2]', ylabel='Modelled DNI [W/m2]')
    subplot.plot([0,999],[0,999], c = 'gray', linewidth = 1)


#%%
""" Question 2 - Irradiance on building surfaces """

kmni_data = pd.read_csv('knmi.txt')
del kmni_data['# STN']
kmni_data.columns = ['date', 'HH', 'wind', 'temp', 'ghi']
kmni_data.date = kmni_data.date.astype(str)
kmni_data.HH = kmni_data.HH.apply( lambda x: str(x).zfill(2))
kmni_data.HH = kmni_data.HH.replace('24', '00')

kmni_data['datetime'] = kmni_data.date + kmni_data.HH + '00'
kmni_data.datetime = pd.to_datetime( kmni_data.datetime, format = '%Y%m%d%H%M')
kmni_data.index = kmni_data.datetime
kmni_data = kmni_data[['wind', 'temp', 'ghi']]

kmni_data.ghi = kmni_data.ghi * 2.77778
kmni_data.temp = kmni_data.temp / 10
kmni_data.wind = kmni_data.wind / 10

kmni_data.index = kmni_data.index.tz_localize('UTC')


### SUB-QUESTION 2.2
#building a dictionary of surfaces, note 0s for surfaces we are going to calculate in next question
tilts = [90, 90, 90, 90, 90, 40, 40, 40, 40, 0, 0]
orientations = [135, 225, 90, 180, 270, 180, 0, 270, 90, 0, 0]

buildings_list = [list(x) for x in zip(tilts, orientations)]
keys_list = ["SurfaceASE","SurfaceASW","SurfaceBE","SurfaceBS","SurfaceBW","RoofCS","RoofCN","RoofDW","RoofDE","RoofA","RoofB"]

zip_iterator = zip(keys_list, buildings_list)
buildings = dict(zip_iterator)

###SUB-QUESTION 2.3

def find_dni_eind(model, ghi, solar_position):
    """Return a DNI series based on the model, ghi, and solar position"""
    time = kmni_data.index
    ghi = kmni_data.ghi
    zenith = solarangles_Eind['zenith']
    apparent_zenith = solarangles_Eind['apparent_zenith']
    
    if model == 'dirindex':
        relative_airmass = pvlib.atmosphere.get_relative_airmass(apparent_zenith)
        absolute_airmass = pvlib.atmosphere.get_absolute_airmass(relative_airmass)
        linke_turbidity = pvlib.clearsky.lookup_linke_turbidity(time, lat_Eind , lon_Eind)
        clearsky = pvlib.clearsky.ineichen(apparent_zenith, absolute_airmass, linke_turbidity, perez_enhancement=True)
        return pvlib.irradiance.dirindex(ghi, clearsky['ghi'], clearsky['dni'], zenith=zenith, times=time)
    raise Exception('Invalid model')

#Location Station
lat_Eind = 51.451
lon_Eind = 5.377

# Calculate Eindoven Solar Zenith
solarangles_Eind = pvlib.solarposition.ephemeris(kmni_data.index, lat_Eind, lon_Eind, kmni_data.temp)
solarangles_Eind = solarangles_Eind[solarangles_Eind > 4]
kmni_data = kmni_data[kmni_data.index.isin(solarangles_Eind.index)]
kmni_data = kmni_data.dropna()
#solarangles_Eind = solarangles_Eind[solarangles_Eind.index.isin(kmni_data.index)]
#kmni_data = kmni_data[kmni_data.index.isin(solarangles_Eind.index)]

#Calculate Eindhoven DNI using the dirindex model 
modelled_dni_Eind = find_dni_eind('dirindex', kmni_data, solarangles_Eind)
kmni_data['dni'] = modelled_dni_Eind
kmni_data = kmni_data.dropna()

#Calculate DHI from DNI
DHIEind = kmni_data.ghi - np.cos(solarangles_Eind.zenith/180*np.pi)*kmni_data['dni'] 
kmni_data['dhi'] = DHIEind

#Calculate the POAs
surface = pd.read_csv('Surfaceparameters.csv', index_col = 'Surface')

POAtotal = pd.DataFrame(index=kmni_data.index, columns = surface.index)
POAdirect = pd.DataFrame(index=kmni_data.index, columns = surface.index)
POAdiffuse = pd.DataFrame(index=kmni_data.index, columns = surface.index)

for i in surface.index:
    POAtotal[i] = pvlib.irradiance.get_total_irradiance(surface.loc[i, 'Slope'], surface.loc[i, 'Azimuth'], solarangles.zenith, solarangles.azimuth, DNIEind, data.ghi, DHIEind)['poa_global']
    POAdirect[i] = pvlib.irradiance.get_total_irradiance(surface.loc[i, 'Slope'], surface.loc[i, 'Azimuth'], solarangles.zenith, solarangles.azimuth, DNIEind, data.ghi, DHIEind)['poa_direct']
    POAdiffuse[i] = pvlib.irradiance.get_total_irradiance(surface.loc[i, 'Slope'], surface.loc[i, 'Azimuth'], solarangles.zenith, solarangles.azimuth, DNIEind, data.ghi, DHIEind)['poa_diffuse']