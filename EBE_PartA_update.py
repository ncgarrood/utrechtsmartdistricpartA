# -*- coding: utf-8 -*-
"""
Created on Sun Sep 26 18:40:24 2021

@author: NCG
"""
#%%

import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import seaborn as sns

from pvlib.irradiance import get_total_irradiance,disc,dirint,dirindex,erbs
from pvlib.solarposition import ephemeris
from pvlib.atmosphere import get_relative_airmass,get_absolute_airmass
from pvlib.clearsky import lookup_linke_turbidity,ineichen

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

#%%

### GLOBAL VARIABLES

LOCATIONS = {
    "Utrecht":{
        "latitude": 52.08746136865645,
        "longitude": 5.168080610130638,
        "filename":"Irradiance_2015_UPOT.csv"
    },
    "Eindhoven":{
        "latitude": 52.451,
        "longitude": 5.377,
        "filename":"knmi.txt"

    }
   
}

MODELS = ['disc', 'dirint', 'dirindex','erbs']
TILTS = [90, 90, 90, 90, 90, 40, 40, 40, 40, np.nan, np.nan]
ORIENTATIONS = [135, 225, 90, 180, 270, 180, 0, 270, 90, np.nan, 180]
KEY_LIST = ["SurfaceASE","SurfaceASW","SurfaceBE","SurfaceBS","SurfaceBW","RoofCS","RoofCN","RoofDW","RoofDE","RoofA","RoofB"]

### FUNCTIONS

def load_location_and_solar_angles(location:str)-> pd.DataFrame:
    
    if location == 'Utrecht':
     # UPOT = Utrecht Photovoltaic Outdoor Test
        location_data =  (
            pd.read_csv("Irradiance_2015_UPOT.csv", sep = ';', index_col = "timestamp", parse_dates= True)
            .rename({'temp_air':'temp', "GHI":'ghi'}, axis=1)
            .drop('Unnamed: 0', axis=1)
        )
        
    elif location == 'Eindhoven':
        location_data = (
            pd.read_csv(LOCATIONS[location]["filename"])
            .drop(["# STN","YYYYMMDD","H"],axis=1)
            .set_axis( [ 'wind', 'temp', 'ghi'], axis=1, inplace=False)
            .assign( datetime = lambda df:pd.date_range(start = '1/1/2019 00:00:00', periods = len(df), freq = 'H', tz='CET'),
                     ghi =  lambda df: df.ghi * 2.77778,
                     temp =   lambda df: df.temp / 10,
                     wind =   lambda df: df.wind / 10
                   )
            .replace(r'\s+', np.nan, regex = True)
            .dropna()
            .set_index(['datetime'])
        )
    
    else: 
        raise Exception('Invalid location')
    
    solar_angles = (
        ephemeris(location_data.index, LOCATIONS[location]["latitude"],  LOCATIONS[location]["longitude"], location_data.temp)
        .loc[lambda df: df.elevation > 4  ]
    )
    
    location_data = location_data.merge(solar_angles, left_index=True, right_index=True, how='right')
    
    return location_data
    
def find_dni(model:str, location: str)-> pd.Series:
    
    location_data = load_location_and_solar_angles(location)
      
    if model == 'disc':
        output = disc(location_data['ghi'],location_data['zenith'], location_data.index).dni
    elif model == 'dirint':
        output = dirint(location_data.ghi, location_data.zenith, location_data.index)
    elif model == 'dirindex':
        relative_airmass = get_relative_airmass(location_data.apparent_zenith)
        absolute_airmass = get_absolute_airmass(relative_airmass)
        linke_turbidity = lookup_linke_turbidity(location_data.index, LOCATIONS[location]["latitude"],LOCATIONS[location]["longitude"])
        clearsky = ineichen(location_data.apparent_zenith, absolute_airmass, linke_turbidity, perez_enhancement=True)
        output = dirindex(location_data.ghi, clearsky['ghi'], clearsky['dni'], zenith=location_data.zenith, times=location_data.index)
    elif model == 'erbs':
        output = erbs(location_data.ghi,location_data.zenith, location_data.index).dni
    else: 
        raise Exception('Invalid model or location')

    return location_data.assign( **{model : output})

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


""" Question 1 - Model Testing """

##Calculate the DNI based on four models

#First load the data set and solar angles for Utrecht
Utrecht_data = load_location_and_solar_angles('Utrecht')


for model in MODELS:
    modelled_dni_utrecht = find_dni(model, 'Utrecht')
    Utrecht_data[model] = modelled_dni
    compare_dni(model, Utrecht_data.DNI, modelled_dni_utrecht)

