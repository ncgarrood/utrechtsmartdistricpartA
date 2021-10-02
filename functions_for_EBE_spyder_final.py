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
                    x = x/10**3 #NOTE CONVERSION TO kW
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

def get_aoi(Surfaces_angles_areas:dict, location_data, surface):
    
    surface_tilt = Surfaces_angles_areas[surface]['tilt']
    surface_azimuth = Surfaces_angles_areas[surface]['orientation']
    solar_zenith =  location_data.zenith
    solar_azimuth = location_data.azimuth
    
    sr_aoi = aoi(surface_tilt, surface_azimuth, solar_zenith, solar_azimuth)
    return sr_aoi

def get_sapm_effective(location_data, ModuleParameters, surface, module):
    
    poa_direct = location_data[surface+'_poa_direct']
    poa_diffuse = location_data[surface+'_poa_diffuse']
    airmass_absolute = location_data[surface+'_abs_airmass']
    aoi = location_data[surface+'_aoi']
    module = ModuleParameters[module]
    
    sapm_parameters = sapm_effective_irradiance(poa_direct, poa_diffuse, airmass_absolute, aoi, module)
    return sapm_parameters

def get_sapm_cell(location_data, ModuleParameters, surface, module):
    
    poa_global = location_data[surface+'_poa_global']
    temp_air = location_data.temp
    wind_speed = location_data.wind
    a =  ModuleParameters[module]['A']
    b =  ModuleParameters[module]['B']
    deltaT = ModuleParameters[module]['DTC']
    irrad_ref=1000.0
    
    sapm_cell_data = sapm_cell(poa_global, temp_air, wind_speed, a, b, deltaT, irrad_ref=1000.0)
    return sapm_cell_data     

###### FINAL FUNCTION FOR 3.2


def get_DC_output(location_data:pd.DataFrame, Surfaces_angles_areas:dict, all_surface_POA_data, surface, module):
    
    apparent_zenith = location_data.apparent_zenith
    #add the dhi, aoi to the location_data df.
    sr_aoi = get_aoi(Surfaces_angles_areas, location_data, surface) 
    sr_aoi.rename(surface+'_aoi', inplace = True)
    location_data = location_data.assign(dhi_from_dni = lambda df: df.ghi  - np.cos(np.deg2rad(df.zenith))*df.dirindex_DNI)
    location_data = location_data.merge(sr_aoi, left_index=True, right_index=True, how= 'left')
    
    # and relative and abs airmass
    location_data[surface+'_rel_airmass'] = get_relative_airmass(apparent_zenith)
    location_data[surface+'_abs_airmass'] =  get_absolute_airmass(location_data[surface+'_rel_airmass'])
    
    #add the POA data previously defined
    location_data = location_data.merge(all_surface_POA_data.loc[:,[x for x in all_surface_POA_data.columns if surface in x]], left_index=True, right_index=True, how= 'left')
    
    #Load Module Parameters
    ModuleParameters = load_ModuleParameters()
    
    #add the SAPM Effective Irradiance Output
    sapm_eff_irr = (get_sapm_effective(location_data, ModuleParameters, surface, module))
    location_data[surface+'_SAPM_eff_irr'] = sapm_eff_irr
    
    #add the SAPM Cell info
    sapm_celltemp = get_sapm_cell(location_data, ModuleParameters, surface, module)
    location_data[surface+'_SAPM_cell_temp'] = sapm_celltemp
    
    #calculate the power output
    effective_irradiance =  location_data[surface+'_SAPM_eff_irr']
    temp_cell = location_data[surface+'_SAPM_cell_temp']
    module = ModuleParameters[module]
    power_df = sapm(effective_irradiance, temp_cell, module)   
    
    location_data[surface+'_p_mp'] = power_df['p_mp']
    
    return location_data

#SUB QUESTION 3.3
def create_bar_charts_DC_outputs_surface_groups(module_yields):
    
    sns.set_theme(style="whitegrid")
    
    # Draw a nested barplot by tilt and orientation
    g = sns.catplot(
        data = module_yields, kind="bar",
        x="surface", y="annualyield", hue="module",
        ci = None, palette="dark", alpha=0.6, height=6,
    )
    g.despine(left=True)
    g.set_axis_labels('', "Annual Yield [kWh/m2]")
    g.legend.set_title('Module Type')
    g.set_xticklabels(rotation=90)
    

def create_bar_charts_DC_outputs_module_groups(module_yields):
    
    sns.set_theme(style="whitegrid")
    
    # Draw a nested barplot by tilt and orientation
    g = sns.catplot(
        data = module_yields, kind="bar",
        x="module", y="annualyield", hue="surface",
        ci = None, palette="dark", alpha=.6, height=6
    )
    g.despine(left=True)
    g.set_axis_labels("Module", "Annual Yield [kWh/m2]")
    g.legend.set_title(' ')

def whole_facade_tables_charts(Eind_data, Surfaces_angles_areas, all_surface_POA_data, BUILDINGS_df_update):
    
    p_mp_values_wholefacade = pd.DataFrame(index = Eind_data.index)

    for surface in Surfaces_angles_areas.columns:
        for module in ['HIT', 'CdTe', 'monoSi']:
            module_dc = get_DC_output(Eind_data, Surfaces_angles_areas, all_surface_POA_data, surface, module)

            p_mp_values_wholefacade[module+surface+'_p_mp'] = module_dc[surface+'_p_mp']

    p_mp_sums = p_mp_values_wholefacade.sum(axis=0)

    module_yields = pd.DataFrame(columns = ['surface','module','Annual Yield [kW/m2]' ])

    module_yields['surface'] = BUILDINGS_df_update.columns.repeat(3)
    module_yields['module'] = ['HIT','CdTe', 'monoSi']*11
    module_yields['Annual Yield [kW/m2]'] = (p_mp_sums.values/1000).astype(int)

    Area_series = (Surfaces_angles_areas.loc['Area']).repeat(3)
    Area_series.values

    module_yields['Areas [m2]'] = Area_series.values.astype(int)
    module_yields['Yield, Whole Facade [kW]'] = module_yields['Annual Yield [kW/m2]']*module_yields['Areas [m2]'].astype(int)
    return module_yields

def create_bar_charts_DC_outputs_surface_groups_whole(module_yields):
    
    sns.set_theme(style="whitegrid")
    
    # Draw a nested barplot by tilt and orientation
    g = sns.catplot(
        data = module_yields, kind="bar",
        x="surface", y="Yield, Whole Facade [kW]", hue="module",
        ci = None, palette="dark", alpha=0.6, height=6,
    )
    g.despine(left=True)
    g.set_axis_labels('', "Annual Yield [kWh]")
    g.legend.set_title('Module Type')
    g.set_xticklabels(rotation=90)

def create_bar_charts_DC_outputs_module_groups_whole(module_yields):
    
    sns.set_theme(style="whitegrid")
    
    # Draw a nested barplot by tilt and orientation
    g = sns.catplot(
        data = module_yields, kind="bar",
        x="module", y="Yield, Whole Facade [kW]", hue="surface",
        ci = None, palette="dark", alpha=.6, height=6
    )
    g.despine(left=True)
    g.set_axis_labels("Module", "Annual Yield [kWh]")
    g.legend.set_title(' ')


def get_PV_systems_table(BUILDINGS_df_update, Surfaces_Panel_info):
    
    df = pd.DataFrame(columns = ['Surface', 'Best Module', 'Total Capacity', 'Tilt', 'Orientation'])
    df['Surface'] = BUILDINGS_df_update.columns
    df['Best Module'] = ('Mono Si')
    Surfaces_Panel_info_transposed = Surfaces_Panel_info.transpose()
    df['Total Capacity'] = Surfaces_Panel_info_transposed['Capacity_monoSi'].values.astype(int) 
    df['Tilt'] = Surfaces_Panel_info_transposed['tilt'].values.astype(int) 
    df['Orientation'] = Surfaces_Panel_info_transposed['orientation'].values.astype(int) 
    df.set_index('Surface', inplace = True )

    return df
