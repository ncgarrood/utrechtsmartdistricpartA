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

from pvlib.irradiance import get_total_irradiance,disc,dirint,dirindex,erbs,aoi
from pvlib.solarposition import ephemeris
from pvlib.atmosphere import get_relative_airmass,get_absolute_airmass
from pvlib.clearsky import lookup_linke_turbidity,ineichen
from pvlib.pvsystem import sapm_effective_irradiance, sapm
from pvlib.temperature import sapm_cell

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
TILTS = [90, 90, 90, 90, 90, 40, 40, 40, 40]
ORIENTATIONS = [135, 225, 90, 180, 270, 180, 0, 270, 90]
KEY_LIST = ["SurfaceASE","SurfaceASW","SurfaceBE","SurfaceBS","SurfaceBW","RoofCS","RoofCN","RoofDW","RoofDE"]
SURFACES_TO_CALCULATE = {'RoofA':{'tilt': list(range(10,45,5)), "orientation":[135,225] } ,'RoofB':{'tilt': list(range(10,45,5)), "orientation": [180]}}

HouseRoofHeight = 3/np.sin(np.deg2rad(40))
BUILDING_SIZES = {"SurfaceASE": {"H":100, "W":60, "percentage_covered":0.3},"SurfaceASW" : {"H":100, "W":50, "percentage_covered":0.3},"SurfaceBE" : {"H":30, "W":30, "percentage_covered":0.3},"SurfaceBS": {"H":30, "W":50, "percentage_covered":0.3},"SurfaceBW": {"H":30, "W":30, "percentage_covered":0.3},"RoofCS": {"H":HouseRoofHeight, "W":50, "percentage_covered":0.6},"RoofCN": {"H":HouseRoofHeight, "W":50, "percentage_covered":0.6},"RoofDW": {"H":HouseRoofHeight, "W":50, "percentage_covered":0.6},"RoofDE": {"H":HouseRoofHeight, "W":50, "percentage_covered":0.6},"RoofA": {"H":60, "W":50, "percentage_covered":0.5},"RoofB":{"H":30, "W":50, "percentage_covered":0.5}}
# For the office rooftops, assume that the area of the systems will be equal to the 50% of the area of the rooftop. 
#Assume these to be mounted on top of the existing roof with the proper tilt.


### FUNCTIONS

"""Question 1 Functions"""

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
            .assign( datetime = lambda df:pd.date_range(start = '1/1/2019 00:30:00', periods = len(df), freq = 'H', tz='CET'), 
            #weird think appaz to start at 00.30 since its the middle of the measured hour seems a bit hakcy
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
        .loc[lambda df: df.elevation > 4.5]
    )
    
    location_data = location_data.merge(solar_angles, left_index=True, right_index=True, how='right')
    
    return location_data
    
def find_dni(model:str, location: str)-> pd.Series:
    
    location_data = load_location_and_solar_angles(location)
      
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

    return location_data.assign( **{model+"_DNI" : output})

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

def create_utrecht_dni_scatters():
    fig, axs = plt.subplots(2, 2,figsize = (12,7))
    #formatting
    fig.subplots_adjust(wspace = 0.2, hspace = 0.3)

    for index, model in enumerate(MODELS):
        modelled_dni_scatter = find_dni(model,'Utrecht')
        subplot = axs[index//2][index % 2]
        subplot.scatter(modelled_dni_scatter.DNI, modelled_dni_scatter[model+"_DNI"], s=0.001, c= 'lightcoral')
        subplot.set_title(model.upper())
        subplot.set(xlabel='Observed DNI [W/m2]', ylabel='Modelled DNI [W/m2]')
        subplot.plot([0,999],[0,999], c = 'gray', linewidth = 1)


"""Question 2 Functions"""

def create_surface_dict(KEY_LIST:list,TILTS:list,ORIENTATIONS: list) -> dict:
    buildings = {}
    
    for index, name in enumerate(KEY_LIST):
        buildings[name] = {
            'tilt': TILTS [index],
            'orientation' : ORIENTATIONS [index]
        }
      
    return buildings 

BUILDINGS = create_surface_dict(KEY_LIST,TILTS,ORIENTATIONS) 

def calculate_POA_with_dirindex(location_data:pd.DataFrame , surface:str, surface_tilt:int, surface_azimuth:int):
    
    solar_zenith = location_data.zenith
    solar_azimuth = location_data.azimuth
    dni = location_data.dirindex_DNI
    ghi = location_data.ghi
    dhi = location_data.dhi_from_dni
    return get_total_irradiance(surface_tilt, surface_azimuth, solar_zenith, solar_azimuth, dni, ghi, dhi)

def create_surfaces_POAs(model:str , location:str, BUILDINGS_df:pd.DataFrame) -> pd.DataFrame:
    
    location_data = (
        find_dni(model,location)
        .assign(dhi_from_dni = lambda df: df.ghi  - np.cos(np.deg2rad(df.zenith))*df[model+"_DNI"] )
        )
    df = pd.DataFrame()
    
    for surface in BUILDINGS_df :
        POA = calculate_POA_with_dirindex(location_data, surface, BUILDINGS_df .loc["tilt",surface], BUILDINGS_df.loc["orientation",surface])
        POA = POA.drop(['poa_sky_diffuse', 'poa_ground_diffuse'],axis=1)
        POA =  POA.rename(columns=dict(zip(POA.columns, [x.replace("poa",surface+"_poa") for x in POA.columns])))
        df = pd.concat((df, POA), axis=1)
        
    return df

def calculate_optimal_angles(model:str , location:str, surfaces_to_calculate:dict) -> pd.DataFrame:
    
    if model == 'dirindex' and location == "Eindhoven":
        location_data = (
            find_dni(model,location)
            .assign(dhi_from_dni = lambda df: df.ghi  - np.cos(np.deg2rad(df.zenith))*df[model+"_DNI"] )
        )

        df = pd.DataFrame() #creates a dataframe of the POA sums at various tilts and orientations
        df = pd.DataFrame(columns = ['surface', 'tilt', 'orientation', 'sum of POA global'])
        for surface in surfaces_to_calculate:
            for tilt in surfaces_to_calculate[surface]['tilt']:
                for orientation in surfaces_to_calculate[surface]['orientation']:
                    x = calculate_POA_with_dirindex(location_data, surface, tilt, orientation)['poa_global'].sum()
                   
                    df.loc[len(df)] = [surface,tilt,orientation,x]
        return df

    else: 
        raise Exception('note that function is currently only set up for model: dirindex and location:Eindhoven')
    
def create_bar_charts(roof:str):
    """Enter roof A or B and get the bar chart of it"""
    sns.set_theme(style="whitegrid")
    
    #filter the POA_sums dataframe by roof A and roof B
    POA_sums_RoofA_and_B = calculate_optimal_angles('dirindex', 'Eindhoven', SURFACES_TO_CALCULATE) #query on this, not optimal solution 
    POA_totals = POA_sums_RoofA_and_B[POA_sums_RoofA_and_B['surface'] == roof]
    POA_totals.loc[:,'sum of POA global'] = POA_totals.loc[:,'sum of POA global']/10**3
    
    # Draw a nested barplot by tilt and orientation
    g = sns.catplot(
        data = POA_totals, kind="bar",
        x="tilt", y="sum of POA global", hue="orientation",
        ci = None, palette="dark", alpha=.6, height=6
    )
    g.despine(left=True)
    g.set(ylim=(800,1300))
    g.set_axis_labels("Tilt [degrees]", "Sum of POA_global [kW/m2]")
    g.legend.set_title('Orientation')

"""Question 3 Functions"""

def get_building_angles_areas(BUILDING_SIZES, BUILDINGS_df_update):
    """take the height info from the building_size dict and the tilt/orientation info from the surfaces dict and merge them"""
    Building_sizes = pd.DataFrame(data = BUILDING_SIZES).transpose()
    Building_sizes["Area"] = round(Building_sizes['H']*Building_sizes['W']*Building_sizes['percentage_covered'],2)
    Building_sizes = Building_sizes.transpose()

    BUILDINGS_tilts_areas = BUILDINGS_df_update.copy()
    BUILDINGS_tilts_areas = pd.concat([BUILDINGS_tilts_areas, Building_sizes])
    BUILDINGS_tilts_areas = BUILDINGS_tilts_areas.drop(['H', 'W', 'percentage_covered'])
    return BUILDINGS_tilts_areas

def load_ModuleParameters():
    df = pd.read_excel("ModuleParameters.xlsx", index_col = 'Parameters')
    df.rename({'mono-Si': "monoSi"}, axis=1,  inplace=True)
    return df

def find_panels_capacity(ModuleType:str, BUILDINGS_tilts_areas:pd.DataFrame, ModuleParameters:pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(columns = ['Surface', "Number_panels", "Capacity"])
    """Returns the capaicty and number of panels per surface as a dataframe"""
    for surface in BUILDINGS_tilts_areas:
        Number_panels = (BUILDINGS_tilts_areas[surface]['Area']//ModuleParameters[ModuleType]['Area'])//ModuleParameters[ModuleType]['Cells_in_Series']
        Capacity = Number_panels*ModuleParameters[ModuleType]['Wp']
        df.loc[len(df)] = [surface, Number_panels, Capacity]
    df.rename({'Number_panels':'Number_panels_'+ModuleType, 'Capacity': 'Capacity_'+ModuleType}, axis = 1, inplace = True)
    df.set_index('Surface', inplace = True)
    df = df.transpose()
    
    return df




