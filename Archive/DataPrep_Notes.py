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
       
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 12:27:16 2021

@author: NCG
"""

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


""" Question 1 - Model Testing """

### Global Variables

LOCATIONS = {
    "UPOT":{
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

### Functions
def find_dni(model:str, location: str)-> pd.Series:
    
    location_data = load_location_data(location)
      
    if model == 'disc':
        output = disc(location_data.ghi,location_data.zenith, location_data.index).dni
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
"""   
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
    subplot.scatter(UPOT_data.DNI, UPOT_data[model], s=0.0005, c= 'lightcoral')
    subplot.set_title(model.upper())
    subplot.set(xlabel='Observed DNI [W/m2]', ylabel='Modelled DNI [W/m2]')
    subplot.plot([0,999],[0,999], c = 'gray', linewidth = 1)

"""
#%%
""" Question 2 - Irradiance on building surfaces """



### SUB-QUESTION 2.2
#building a dictionary of surfaces, note 0s for surfaces we are going to calculate in next question
TILTS = [90, 90, 90, 90, 90, 40, 40, 40, 40, np.nan, np.nan]
ORIENTATIONS = [135, 225, 90, 180, 270, 180, 0, 270, 90, np.nan, np.nan]
KEY_LIST = ["SurfaceASE","SurfaceASW","SurfaceBE","SurfaceBS","SurfaceBW","RoofCS","RoofCN","RoofDW","RoofDE","RoofA","RoofB"]

def create_surface_dict(KEY_LIST:list,TILTS:list,ORIENTATIONS: list) -> dict:

    buildings = {}
    
    for index, name in enumerate(KEY_LIST):
        buildings[name] = {
            'tilt': TILTS [index],
            'orientation' : ORIENTATIONS [index]
        }
        
    return buildings



from pvlib.irradiance import get_total_irradiance
from pvlib.solarposition import ephemeris
import numpy as np


def load_location_data(location:str)-> pd.DataFrame:
    knmi_data = (
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
    
    eind_data = (
        ephemeris(knmi_data.index, LOCATIONS[location]["latitude"],  LOCATIONS[location]["longitude"], knmi_data.temp)
        .loc[lambda df: df.elevation > 4  ]
        .merge(knmi_data, left_index=True, right_index=True, how='left')
    )
    
    return eind_data



###SUB-QUESTION 2.3


###SUB-QUESTION 2.4
model = 'dirindex'
location = 'Eindhoven'

Eind_data_dirindex = (
    find_dni(model,location)
    .assign(dhi_dirindex = lambda df: df.ghi  - np.cos(np.rad2deg(df.zenith))*df[model] )
)

#Calculate the POAs
def calculate_POA_with_dirindex(surface:str, location_data:pd.DataFrame, surface_tilt:int, surface_azimuth:int):
    
    solar_zenith = location_data.zenith
    solar_azimuth = location_data.azimuth
    dni = location_data.dirindex
    ghi = location_data.ghi
    dhi = location_data.dhi_dirindex
    return get_total_irradiance(surface_tilt, surface_azimuth, solar_zenith, solar_azimuth, dni, ghi, dhi)


surfaces = {'RoofA':{'tilt': list(range(10,45,5)), "orientation":[135,225] } ,'RoofB':{'tilt': list(range(10,45,5)), "orientation": [180]} }

def calculate_optimal_angles(surfaces:dict):
    df = pd.DataFrame(columns = ['surface', 'tilt', 'orientation', 'sum of POA global'])
    for surface in surfaces:
        for tilt in surfaces[surface]['tilt']:
            for orientation in surfaces[surface]['orientation']:
                x = calculate_POA_with_dirindex(surface, modelled_dni_Eind, tilt, orientation)['poa_global'].sum()
                x = x/10**6 #NOTE CONVERSION TO MW
                df.loc[len(df)] = [surface,tilt,orientation,x] 
    return df
            

POA_sums = calculate_optimal_angles(surfaces)
def create_bar_charts(roof):
    """Enter roof A or B and get the bar chart of it"""
    sns.set_theme(style="whitegrid")
    
    #filter the POA_sums dataframe by roof A and roof B
    POA_totals = POA_sums[POA_sums['surface'] == roof]
    
    # Draw a nested barplot by species and sex
    g = sns.catplot(
        data = POA_totals, kind="bar",
        x="tilt", y="sum of POA global", hue="orientation",
        ci = None, palette="dark", alpha=.6, height=6
    )
    g.despine(left=True)
    g.set(ylim=(1, 1.65))
    g.set_axis_labels("Tilt [rad]", "Sum of POA_global [MW/m2]")
    g.legend.set_title('Orientation')
    
create_bar_charts('RoofA')
create_bar_charts('RoofB')

