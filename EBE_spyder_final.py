# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 14:14:06 2021

@author: NCG
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 12:27:16 2021

@author: NCG
"""

from EBE_PartA_update import (
    #functions
    load_location_and_solar_angles, find_dni, compare_dni, create_utrecht_dni_scatters, create_surfaces_POAs, calculate_optimal_angles, create_bar_charts, 
    #global variables
    MODELS, LOCATIONS, KEY_LIST, TILTS, ORIENTATIONS, BUILDINGS, SURFACES_TO_CALCULATE
    ) 
    
import pandas as pd
import numpy as np
import seaborn as sns

##Calculate the DNI based on four models

#First load the data set and solar angles for Utrecht
Utrecht_data = load_location_and_solar_angles('Utrecht')

###SUB-QUESTION 1.2
for model in MODELS:
    modelled_dni_utrecht = find_dni(model, 'Utrecht')[model]
    compare_dni(model, Utrecht_data.DNI, modelled_dni_utrecht)

###SUB-QUESTION 1.3
scatter_modelled_dnis = create_utrecht_dni_scatters()


"""Question 2"""

Eind_data = find_dni('dirindex','Eindhoven')
Eind_data 

BUILDINGS_df = pd.DataFrame(BUILDINGS)
BUILDINGS_df 

###SUB-QUESTION 2.3
all_surface_POA_data = create_surfaces_POAs('dirindex', "Eindhoven", BUILDINGS_df)
all_surface_POA_data
POA_direct = all_surface_POA_data.loc[:,[x for x in all_surface_POA_data.columns if "direct" in x]]
POA_direct
POA_diffuse = all_surface_POA_data.loc[:,[x for x in all_surface_POA_data.columns if "diffuse" in x]]
POA_diffuse
POA_total = all_surface_POA_data.loc[:,[x for x in all_surface_POA_data.columns if "global" in x]]
POA_total

POA_sums_RoofA_and_B = calculate_optimal_angles('dirindex', 'Eindhoven', SURFACES_TO_CALCULATE)
POA_sums_RoofA_and_B

create_bar_charts('RoofA')
create_bar_charts('RoofB')

###SUB-QUESTION 2.4

POA_sums_RoofA_and_B

###SUB-QUESTION 2.5
POA_sums_RoofA = POA_sums_RoofA_and_B.loc[lambda df: df['surface'] == "RoofA" ]
POA_sums_RoofA

max_a_row = POA_sums_RoofA.iloc[POA_sums_RoofA['sum of POA global'].idxmax(axis=0)]
max_a_row['tilt']
max_a_row['orientation']


POA_sums_RoofB['sum of POA global'].max()
AB = [[max_a_row['tilt'], 20], [max_a_row['orientation'],180]]
ABdf = pd.DataFrame(data = AB, index = ['tilt', 'orientation'], columns = ["RoofA", "RoofB"])
ABdf
BUILDINGS_df = pd.DataFrame(BUILDINGS)
BUILDINGS_df_update =  BUILDINGS_df.merge(ABdf, left_index=True, right_index=True, how = 'left')
BUILDINGS_df_update

all_surface_POA_data = create_surfaces_POAs('dirindex', "Eindhoven", BUILDINGS_df_update)
all_surface_POA_data

POA_direct = all_surface_POA_data.loc[:,[x for x in all_surface_POA_data.columns if "direct" in x]]
POA_direct
POA_diffuse = all_surface_POA_data.loc[:,[x for x in all_surface_POA_data.columns if "diffuse" in x]]
POA_diffuse
POA_total = all_surface_POA_data.loc[:,[x for x in all_surface_POA_data.columns if "global" in x]]
POA_total

###SUB-QUESTION 2.6

"""best is 135 orientation, 30 tilt for A, and 20 tilt for B

seems  plausible since when you compare RoofB with SurfaceCS and SurfaceBS (all same orientation):
RoofB - tilt 20 - POA at 12.00 = 38
RoofCS - tilt 40 - POA at 12.00 = 35
Surface BS - tilt 90 - POA at 12.00 = 24"""


"""Question 3"""

HouseRoofHeight = 3/np.sin(np.deg2rad(40))
# For the office rooftops, assume that the area of the systems will be equal to the 50% of the area of the rooftop. 
#Assume these to be mounted on top of the existing roof with the proper tilt.
    
Building_sizes_dict = {"SurfaceASE": {"H":100, "W":60, "percentage_covered":0.3},"SurfaceASW" : {"H":100, "W":50, "percentage_covered":0.3},"SurfaceBE" : {"H":30, "W":30, "percentage_covered":0.3},"SurfaceBS": {"H":30, "W":50, "percentage_covered":0.3},"SurfaceBW": {"H":30, "W":30, "percentage_covered":0.3},"RoofCS": {"H":HouseRoofHeight, "W":50, "percentage_covered":0.6},"RoofCN": {"H":HouseRoofHeight, "W":50, "percentage_covered":0.6},"RoofDW": {"H":HouseRoofHeight, "W":50, "percentage_covered":0.6},"RoofDE": {"H":HouseRoofHeight, "W":50, "percentage_covered":0.6},"RoofA": {"H":60, "W":50, "percentage_covered":0.5},"RoofB":{"H":30, "W":50, "percentage_covered":0.5}}
Building_sizes = pd.DataFrame(data = Building_sizes_dict).transpose()

Building_sizes["Area"] = round(Building_sizes['H']*Building_sizes['W']*Building_sizes['percentage_covered'])

Building_sizes = Building_sizes.transpose()
Building_sizes

BUILDINGS_tilts_areas = BUILDINGS_df_update.copy()
BUILDINGS_tilts_areas = pd.concat([BUILDINGS_tilts_areas, Building_sizes])
BUILDINGS_tilts_areas = BUILDINGS_tilts_areas.drop(['H', 'W', 'percentage_covered'])
BUILDINGS_tilts_areas

###SUB-QUESTION 3.2

def load_ModuleParameters():
    df = pd.read_excel("ModuleParameters.xlsx", index_col = 'Parameters')
    return df

ModuleParameters = load_ModuleParameters()
ModuleParameters

Utrecht_data #recall this was called using load_location_and_solar_angles function

from pvlib.irradiance import get_total_irradiance,disc,dirint,dirindex,erbs,aoi
from pvlib.solarposition import ephemeris
from pvlib.atmosphere import get_relative_airmass,get_absolute_airmass
from pvlib.clearsky import lookup_linke_turbidity,ineichen
from pvlib.pvsystem import sapm_effective_irradiance, sapm
from pvlib.temperature import sapm_cell

def get_aoi_and_POAs(BUILDINGS_tilts_areas:dict, location_data):
    
    #note most of same variables so one function, using brackets notation for things that will eventually need to be in a for loop
    
    surface_tilt = BUILDINGS_tilts_areas['SurfaceASE']['tilt']
    surface_azimuth = BUILDINGS_tilts_areas['SurfaceASE']['orientation']
    solar_zenith =  location_data.zenith
    solar_azimuth = location_data.azimuth
    
    df_aoi = aoi(surface_tilt, surface_azimuth, solar_zenith, solar_azimuth)
    
    dni = location_data.DNI #note for Eindhoven it would need to be .dirindex (could use previous function?)
    ghi = location_data.ghi
    dhi = location_data.DHI #and again for Eind -> .assign(dhi_from_dni = lambda df: df.ghi  - np.cos(np.rad2deg(df.zenith))*df[model] )
    
    df_POAs = get_total_irradiance(surface_tilt, surface_azimuth, solar_zenith, solar_azimuth, dni, ghi, dhi)
    df_aoi_POA = df_aoi.to_frame().merge(df_POAs, left_index=True, right_index=True, how= 'left')   
    return df_aoi_POA
    
def get_DC_output(location:str, BUILDINGS_tilts_areas:dict):
    
    location_data = load_location_and_solar_angles(location)
    df_aoi_POA = get_aoi_and_POAs(BUILDINGS_tilts_areas, location_data)
    location_data = location_data.merge(df_aoi_POA, left_index=True, right_index=True, how= 'left')
    return location_data

get_DC_output('Eindhoven', BUILDINGS_tilts_areas)

#get_aoi_and_POAs(BUILDINGS_tilts_areas, Utrecht_data)