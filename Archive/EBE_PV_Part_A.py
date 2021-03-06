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

# Locations
lat_UU, long_UU = 52.08746136865645, 5.168080610130638 # used long/lat from googlemaps for uithof
lat_Eind, long_Eind = 51.451, 5.377

MODELS = ['disc', 'dirint', 'dirindex','erbs']

# Functions
def find_dni(model, ghi, solar_position, input_data):
    """Return a DNI series based on the model, ghi, and solar position"""
    if input_data == "UPOT":
        time = UPOT_data.index
        ghi = UPOT_data.GHI
        zenith = solar_df['zenith']
        apparent_zenith = solar_df['apparent_zenith']
        latitude = lat_UU
        longitude = long_UU
    if input_data == "KNMI_EIND":
        time = knmi_data.index
        ghi = knmi_data.ghi
        zenith = solarangles_Eind['zenith']
        apparent_zenith = solarangles_Eind['apparent_zenith']
        latitude = lat_Eind
        longitude = long_Eind
   
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

def print_errors(model,rmse, mbe, mae, r2):
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
     print_errors(model,rmse,mbe,mae,r2)
     
# Get Irrandiance (UPOT data GHI) and solar angles (Zenith and Apparent Zenith)
UPOT_data = pd.read_csv("Irradiance_2015_UPOT.csv", sep = ';', index_col = "timestamp", parse_dates= True) 
#UPOT_data = UPOT_data.resample("5min").mean()
#UPOT_data = UPOT_data.dropna()

solar_df = pvlib.solarposition.ephemeris(UPOT_data.index, lat_UU, long_UU, temperature= UPOT_data["temp_air"])
solar_df= solar_df[solar_df.elevation > 4] #hours when enough sun to not be neglible generation, avoiding inf values in dirindex later

UPOT_data = UPOT_data[UPOT_data.index.isin(solar_df.index)]

#Calculate the Models and compare to observed GHIs from UPOT dataset
for model in MODELS:
    modelled_dni = find_dni(model, UPOT_data, solar_df, 'UPOT')
    UPOT_data[model] = modelled_dni
    compare_dni(model, UPOT_data.DNI, modelled_dni)
    
#%%    
### GRAPHS for Sub-Question 3

fig, axs = plt.subplots(2, 2)
#formatting
fig.subplots_adjust(wspace = 0.2, hspace = 0.3)

for index, model in enumerate(MODELS):
    subplot = axs[index//2][index % 2]
    subplot.scatter(UPOT_data.DNI, UPOT_data[model], s=0.001, c= 'lightcoral')
    subplot.set_title(model.upper())
    subplot.set(xlabel='Observed DNI [W/m2]', ylabel='Modelled DNI [W/m2]')
    subplot.plot([0,999],[0,999], c = 'gray', linewidth = 1)


#%%
""" Question 2 - Irradiance on building surfaces """

knmi_data = pd.read_csv('knmi.txt')
del knmi_data['# STN']
knmi_data.columns = ['date', 'HH', 'wind', 'temp', 'ghi']
knmi_data.date = knmi_data.date.astype(str)
knmi_data.HH = knmi_data.HH.apply( lambda x: str(x).zfill(2))
knmi_data.HH = knmi_data.HH.replace('24', '00')

knmi_data['datetime'] = knmi_data.date + knmi_data.HH + '00'
knmi_data.datetime = pd.to_datetime( knmi_data.datetime, format = '%Y%m%d%H%M')
knmi_data.index = knmi_data.datetime
knmi_data = knmi_data[['wind', 'temp', 'ghi']]

knmi_data.ghi = knmi_data.ghi * 2.77778
knmi_data.temp = knmi_data.temp / 10
knmi_data.wind = knmi_data.wind / 10

knmi_data.index = knmi_data.index.tz_localize('UTC')


### SUB-QUESTION 2.2
#building a dictionary of surfaces, note 0s for surfaces we are going to calculate in next question
tilts = [90, 90, 90, 90, 90, 40, 40, 40, 40, np.nan, np.nan]
orientations = [135, 225, 90, 180, 270, 180, 0, 270, 90, np.nan, 180]
keys_list = ["SurfaceASE","SurfaceASW","SurfaceBE","SurfaceBS","SurfaceBW","RoofCS","RoofCN","RoofDW","RoofDE","RoofA","RoofB"]

buildings = {}


for index, name in enumerate(keys_list):
    buildings[name] = {
        'tilt': tilts [index],
        'orientation' : orientations [index]
    }

###SUB-QUESTION 2.3
# Calculate Eindoven Solar Zenith
solarangles_Eind = pvlib.solarposition.ephemeris(knmi_data.index, lat_Eind, long_Eind, knmi_data.temp)
solarangles_Eind = solarangles_Eind[solarangles_Eind > 4]

knmi_data = knmi_data.dropna()
solarangles_Eind = solarangles_Eind[solarangles_Eind.index.isin(knmi_data.index)]
knmi_data = knmi_data[knmi_data.index.isin(solarangles_Eind.index)]

#Calculate Eindhoven DNI using the dirindex model 
modelled_dni_Eind = find_dni('dirindex', knmi_data, solarangles_Eind, "KNMI_EIND")
knmi_data['dni'] = modelled_dni_Eind
knmi_data = knmi_data.dropna(axis=0, how='any')

#Calculate DHI from DNI
DHIEind = knmi_data.ghi - np.cos(solarangles_Eind.zenith/180*np.pi)*knmi_data['dni'] 
knmi_data['dhi'] = DHIEind


#Calculate the POAs
surface = pd.read_csv('Surfaceparameters.csv', index_col = 'Surface')

POAtotal = pd.DataFrame(index=knmi_data.index, columns = surface.index)
POAdirect = pd.DataFrame(index=knmi_data.index, columns = surface.index)
POAdiffuse = pd.DataFrame(index=knmi_data.index, columns = surface.index)

for i in surface.index:
    POAtotal[i] = pvlib.irradiance.get_total_irradiance(surface.loc[i, 'Slope'], surface.loc[i, 'Azimuth'], solarangles_Eind.zenith, solarangles_Eind.azimuth, knmi_data.dni, knmi_data.ghi, knmi_data.dhi)['poa_global']
    POAdirect[i] = pvlib.irradiance.get_total_irradiance(surface.loc[i, 'Slope'], surface.loc[i, 'Azimuth'], solarangles_Eind.zenith, solarangles_Eind.azimuth, knmi_data.dni, knmi_data.ghi, knmi_data.dhi)['poa_direct']
    POAdiffuse[i] = pvlib.irradiance.get_total_irradiance(surface.loc[i, 'Slope'], surface.loc[i, 'Azimuth'], solarangles_Eind.zenith, solarangles_Eind.azimuth, knmi_data.dni, knmi_data.ghi, knmi_data.dhi)['poa_diffuse']

### SUB-QUESTION 2.4 - SLOPE B
TiltB = [10, 15, 20, 25, 30, 35, 40, 45] #slope of building B in degrees
OrientationB = 180 #facing south

POAtotalB = pd.DataFrame(index=knmi_data.index)
POAdirectB = pd.DataFrame(index=knmi_data.index)
POAdiffuseB = pd.DataFrame(index=knmi_data.index)

for i in range(len(TiltB)):
    POAtotalB[i] = pvlib.irradiance.get_total_irradiance(TiltB[i], OrientationB, solarangles_Eind.zenith, solarangles_Eind.azimuth, knmi_data.dni, knmi_data.ghi, knmi_data.dhi)['poa_global']
    POAdirectB[i] = pvlib.irradiance.get_total_irradiance(TiltB[i], OrientationB, solarangles_Eind.zenith, solarangles_Eind.azimuth, knmi_data.dni, knmi_data.ghi, knmi_data.dhi)['poa_direct']
    POAdiffuseB[i] = pvlib.irradiance.get_total_irradiance(TiltB[i], OrientationB, solarangles_Eind.zenith, solarangles_Eind.azimuth, knmi_data.dni, knmi_data.ghi, knmi_data.dhi)['poa_diffuse']

POAtotalB.columns = TiltB
POAdirectB.columns = TiltB
POAdiffuseB.columns = TiltB

### SUB-QUESTION 2.4 - SLOPE A
TiltA = [10, 15, 20, 25, 30, 35, 40, 45] #slope of building A in degrees
OrientationA135 = 135 #facing southeast
OrientationA225 = 225 #facing southwest

POAtotalA135 = pd.DataFrame(index=knmi_data.index)
POAdirectA135 = pd.DataFrame(index=knmi_data.index)
POAdiffuseA135 = pd.DataFrame(index=knmi_data.index)

for i in range(len(TiltA)):
    POAtotalA135[i] = pvlib.irradiance.get_total_irradiance(TiltA[i], OrientationA135, solarangles_Eind.zenith, solarangles_Eind.azimuth, knmi_data.dni, knmi_data.ghi, knmi_data.dhi)['poa_global']
    POAdirectA135[i] = pvlib.irradiance.get_total_irradiance(TiltA[i], OrientationA135, solarangles_Eind.zenith, solarangles_Eind.azimuth, knmi_data.dni, knmi_data.ghi, knmi_data.dhi)['poa_direct']
    POAdiffuseA135[i] = pvlib.irradiance.get_total_irradiance(TiltA[i], OrientationA135, solarangles_Eind.zenith, solarangles_Eind.azimuth, knmi_data.dni, knmi_data.ghi, knmi_data.dhi)['poa_diffuse']

POAtotalA135.columns = TiltA
POAdirectA135.columns = TiltA
POAdiffuseA135.columns = TiltA

POAtotalA225 = pd.DataFrame(index=knmi_data.index)
POAdirectA225 = pd.DataFrame(index=knmi_data.index)
POAdiffuseA225 = pd.DataFrame(index=knmi_data.index)

for i in range(len(TiltA)):
    POAtotalA225[i] = pvlib.irradiance.get_total_irradiance(TiltA[i], OrientationA225, solarangles_Eind.zenith, solarangles_Eind.azimuth, knmi_data.dni, knmi_data.ghi, knmi_data.dhi)['poa_global']
    POAdirectA225[i] = pvlib.irradiance.get_total_irradiance(TiltA[i], OrientationA225, solarangles_Eind.zenith, solarangles_Eind.azimuth, knmi_data.dni, knmi_data.ghi, knmi_data.dhi)['poa_direct']
    POAdiffuseA225[i] = pvlib.irradiance.get_total_irradiance(TiltA[i], OrientationA225, solarangles_Eind.zenith, solarangles_Eind.azimuth, knmi_data.dni, knmi_data.ghi, knmi_data.dhi)['poa_diffuse']

POAtotalA225.columns = TiltA
POAdirectA225.columns = TiltA
POAdiffuseA225.columns = TiltA

### SUB-QUESTION 2.4 - BAR CHART
POAtotalB.columns=['ten', 'fifteen', 'twenty', 'twentyfive', 'thirty', 'thirtyfive', 'fourty', 'fourtyfive']
POAtotalA135.columns=['ten', 'fifteen', 'twenty', 'twentyfive', 'thirty', 'thirtyfive', 'fourty', 'fourtyfive']
POAtotalA225.columns=['ten', 'fifteen', 'twenty', 'twentyfive', 'thirty', 'thirtyfive', 'fourty', 'fourtyfive']

x = ['total']
POAB_sum = pd.DataFrame(index = x, columns = TiltB)
POAB_sum.columns = ['ten', 'fifteen', 'twenty', 'twentyfive', 'thirty', 'thirtyfive', 'fourty', 'fourtyfive']

for i in POAtotalB[i]:
    POAB_sum[i] = sum(POAtotalB[i])


#POAtotalB = POAtotalB[['ten', 'fifteen', 'twenty', 'twentyfive', 'thirty', 'thirtyfive', 'fourty', 'fourtyfive']]

def calculate_optimal_angles():
    for surface in surfaces:
        for tilt in surfaces[surface]['tilt']:
            for orientation in surfaces[surface]['orientation']:
                x = calculate_POA_with_dirindex(surfaces[surface], modelled_dni_Eind)
                return x