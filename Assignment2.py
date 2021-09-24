# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 13:56:59 2021

@author: Jens
"""

import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import pvlib
import numpy as np

surface = pd.read_csv('Surfaceparameters.csv', index_col = 'Surface')

data = pd.read_csv('knmi.txt')
del data['# STN']
data.columns = ['date', 'HH', 'wind', 'temp', 'ghi']
data.date = data.date.astype(str)
data.HH = data.HH.apply( lambda x: str(x).zfill(2))
data.HH = data.HH.replace('24', '00')

data['datetime'] = data.date + data.HH + '00'
data.datetime = pd.to_datetime( data.datetime, format = '%Y%m%d%H%M')
data.index = data.datetime
data = data[['wind', 'temp', 'ghi']]

data.ghi = data.ghi * 2.77778
data.temp = data.temp / 10
data.wind = data.wind / 10

data.index = data.index.tz_localize('UTC')

data.to_csv('Assignment2.csv')

# parameters
lat_Eind = 51.451
lon_Eind = 5.377
pi = 3.14159265359

# solar Zenith
solarangles = pvlib.solarposition.ephemeris(data.index, lat_Eind, lon_Eind, data.temp)
solarangles = solarangles[solarangles.index.isin(data.index)]

data = data[data.index.isin(solarangles.index)]

## model 3 (dirindex)
AMR = pvlib.atmosphere.get_relative_airmass(solarangles.zenith, model='kastenyoung1989')
AMM = pvlib.atmosphere.get_absolute_airmass(AMR)
linkeTurb = pvlib.clearsky.lookup_linke_turbidity(data.index, lat_Eind, lon_Eind)
clearsky = pvlib.clearsky.ineichen(solarangles.apparent_zenith, AMM, linkeTurb)
clearsky = clearsky.dropna()
clearsky = clearsky[clearsky.index.isin(data.index)]
DNIEind = pvlib.irradiance.dirindex(data.ghi, clearsky.ghi, clearsky.dni, solarangles.zenith, data.index)
DNIEind = DNIEind.dropna()
DNIEind = DNIEind[DNIEind.index.isin(data.index)]
data = data[data.index.isin(DNIEind.index)]

DHIEind = data.ghi - np.cos(solarangles.zenith/180*pi)*DNIEind

#CS_tilt = 40
#CS_azimuth = 180

POAtotal = pd.DataFrame(index=data.index, columns = surface.index)
POAdirect = pd.DataFrame(index=data.index, columns = surface.index)
POAdiffuse = pd.DataFrame(index=data.index, columns = surface.index)

for i in surface.index:
    POAtotal[i] = pvlib.irradiance.get_total_irradiance(surface.loc[i, 'Slope'], surface.loc[i, 'Azimuth'], solarangles.zenith, solarangles.azimuth, DNIEind, data.ghi, DHIEind)['poa_global']
    POAdirect[i] = pvlib.irradiance.get_total_irradiance(surface.loc[i, 'Slope'], surface.loc[i, 'Azimuth'], solarangles.zenith, solarangles.azimuth, DNIEind, data.ghi, DHIEind)['poa_direct']
    POAdiffuse[i] = pvlib.irradiance.get_total_irradiance(surface.loc[i, 'Slope'], surface.loc[i, 'Azimuth'], solarangles.zenith, solarangles.azimuth, DNIEind, data.ghi, DHIEind)['poa_diffuse']

#POA = pvlib.irradiance.get_total_irradiance(CS_tilt, CS_azimuth, solarangles.zenith, solarangles.azimuth, DNIEind, data.ghi, DHIEind)['poa_global']


#POA = POA.dropna()
