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

#%%
""" FUNCTIONS TO IMPORT """

""" The functions made for the assignment are saved in a separate script 
            and imported here, to make the script cleaner,
            you can open both side by side to follow easily"""
            
from functions_for_EBE_spyder_final import (
    
    #functions
    load_location_and_solar_angles, find_dni, compare_dni, create_utrecht_dni_scatters, create_surfaces_POAs, 
    calculate_optimal_angles, create_bar_charts, load_ModuleParameters, get_building_angles_areas, find_panels_capacity,
    
    #global variables
    MODELS, LOCATIONS, KEY_LIST, TILTS, ORIENTATIONS, BUILDINGS, SURFACES_TO_CALCULATE, BUILDING_SIZES,
   
    #parameters
    HouseRoofHeight
    ) 
    
import pandas as pd
import numpy as np
import seaborn as sns

#%%
"""Question 1"""

###SUB-QUESTION 1.1
#Calculate the DNI based on four models
#First load the data set and solar angles for Utrecht
Utrecht_data = load_location_and_solar_angles('Utrecht')

#Then for loop through the models to get the DNI values and error functions
for model in MODELS:
    modelled_dni_utrecht = find_dni(model, 'Utrecht')[model+"_DNI"]
    compare_dni(model, Utrecht_data.DNI, modelled_dni_utrecht)


###SUB-QUESTION 1.3
scatter_modelled_dnis = create_utrecht_dni_scatters()

#%%
"""Question 2"""

#the data prep steps are in the load_location_and_solar_angles() function, which gets called as part of the find_dni function. See lines 64-76 of functions script
Eind_data = find_dni('dirindex','Eindhoven') 

#DICTIONARY in the global variables list, made it into a dataframe here to manipulate
BUILDINGS_df = pd.DataFrame(BUILDINGS)

###SUB-QUESTION 2.3 - get the POA data in one big dataframe, then manipulate the dataframe to get just the 3 POA dfs we want
all_surface_POA_data = create_surfaces_POAs('dirindex', "Eindhoven", BUILDINGS_df)

POA_direct = all_surface_POA_data.loc[:,[x for x in all_surface_POA_data.columns if "direct" in x]]
POA_diffuse = all_surface_POA_data.loc[:,[x for x in all_surface_POA_data.columns if "diffuse" in x]]
#note POA_total = POA_global
POA_total = all_surface_POA_data.loc[:,[x for x in all_surface_POA_data.columns if "global" in x]]

###SUB-QUESTION 2.4
#surfaces to calculate is a dictionary of the roof A and B tilts and orientations to loop through
POA_sums_RoofA_and_B = calculate_optimal_angles('dirindex', 'Eindhoven', SURFACES_TO_CALCULATE)
create_bar_charts('RoofA')
create_bar_charts('RoofB')

###SUB-QUESTION 2.5
#this function filters the POA table by Roof A only
POA_sums_RoofA = POA_sums_RoofA_and_B.loc[lambda df: df['surface'] == "RoofA" ]
POA_sums_RoofA
# return the row with the highest POA value of the Roof A POAs
max_a_row = POA_sums_RoofA.iloc[POA_sums_RoofA['sum of POA global'].idxmax(axis=0)]
max_a_row['tilt']
max_a_row['orientation']

#filter by roof B
POA_sums_RoofB = POA_sums_RoofA_and_B.loc[lambda df: df['surface'] == "RoofB"]
POA_sums_RoofB['sum of POA global'].max()

# create a new DF of the optimum A and B tilts and orientations
AB = [[max_a_row['tilt'], 20], [max_a_row['orientation'],180]]
ABdf = pd.DataFrame(data = AB, index = ['tilt', 'orientation'], columns = ["RoofA", "RoofB"])

#merge the roofA and roof B tilts and orientations to the BUILDINGS_df, called it BUILDINGS_df_update
BUILDINGS_df = pd.DataFrame(BUILDINGS)
BUILDINGS_df_update =  BUILDINGS_df.merge(ABdf, left_index=True, right_index=True, how = 'left')
BUILDINGS_df_update

#now we make the POA tables again, with the new info for Roof A and Roof B
all_surface_POA_data = create_surfaces_POAs('dirindex', "Eindhoven", BUILDINGS_df_update)
all_surface_POA_data

POA_direct = all_surface_POA_data.loc[:,[x for x in all_surface_POA_data.columns if "direct" in x]]
POA_direct
POA_diffuse = all_surface_POA_data.loc[:,[x for x in all_surface_POA_data.columns if "diffuse" in x]]
POA_diffuse
POA_total = all_surface_POA_data.loc[:,[x for x in all_surface_POA_data.columns if "global" in x]]
POA_total

###SUB-QUESTION 2.6

# added a text string here of some ideas for this one, was quite lazy answering it, think we should add more
"""best is 135 orientation, 30 tilt for A, and 20 tilt for B

seems  plausible since when you compare RoofB with SurfaceCS and SurfaceBS (all same orientation):
RoofB - tilt 20 - POA at 12.00 = 38
RoofCS - tilt 40 - POA at 12.00 = 35
Surface BS - tilt 90 - POA at 12.00 = 24"""

#%%
"""Question 3"""

###SUB-QUESTION 3.1 - calculate the areas of solar panelling and number of panels per surface

#make the building sizes (height, width, length into a dataframe)
Surfaces_angles_areas = get_building_angles_areas(BUILDING_SIZES, BUILDINGS_df_update)

#load the module parameters
ModuleParameters = load_ModuleParameters()

#Load the number of panels and capaity of panels for each building surface
HIT = find_panels_capacity('HIT', Surfaces_angles_areas, ModuleParameters)
CDTE =  find_panels_capacity('CdTe', Surfaces_angles_areas, ModuleParameters)
MONOSI = find_panels_capacity('monoSi', Surfaces_angles_areas, ModuleParameters)

#merge all the info together so you get one dict
Surfaces_Panel_info = Surfaces_angles_areas.append([HIT,CDTE,MONOSI])

#%% 
###SUB-QUESTION 3.2

"""" Unfinished section, won't currently run, more testing in Jupyter Lab

 while building the function brackets notation marks things that will eventually need to be in a for loop, 
 so we only have to run the function once per solar panel type (HIT/CDTE/MONOSI)"""

from pvlib.irradiance import get_total_irradiance,disc,dirint,dirindex,erbs,aoi
from pvlib.solarposition import ephemeris
from pvlib.atmosphere import get_relative_airmass,get_absolute_airmass
from pvlib.clearsky import lookup_linke_turbidity,ineichen
from pvlib.pvsystem import sapm_effective_irradiance, sapm
from pvlib.temperature import sapm_cell

def get_aoi_and_POAs(model:str, Surfaces_angles_areas:dict, location_data):
    
    #while building the function brackets notation marks things that will eventually need to be in a for loop, so we only have to run the function once per solar panel type (HIT/CDTE/MONOSI)
    
    surface_tilt = Surfaces_angles_areas['SurfaceASE']['tilt']
    surface_azimuth = Surfaces_angles_areas['SurfaceASE']['orientation']
    solar_zenith =  location_data.zenith
    solar_azimuth = location_data.azimuth
    
    df_aoi = aoi(surface_tilt, surface_azimuth, solar_zenith, solar_azimuth)
    
    dni = location_data[model+"_DNI"] 
    ghi = location_data.ghi
    dhi = location_data.assign(dhi_from_dni = lambda df: df.ghi  - np.cos(np.deg2rad(df.zenith))*df[model+"_DNI"] )
    
    df_POAs = get_total_irradiance(surface_tilt, surface_azimuth, solar_zenith, solar_azimuth, dni, ghi, dhi)
    df_aoi_POA = df_aoi.to_frame().merge(df_POAs, left_index=True, right_index=True, how= 'left')   
    return df_aoi_POA
    
def get_DC_output(location:str, BUILDINGS_tilts_areas:dict):
    
    location_data = load_location_and_solar_angles(location)
    df_aoi_POA = get_aoi_and_POAs(BUILDINGS_tilts_areas, location_data)
    location_data = location_data.merge(df_aoi_POA, left_index=True, right_index=True, how= 'left')
    return location_data

