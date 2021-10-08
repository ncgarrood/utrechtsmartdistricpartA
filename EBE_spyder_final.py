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
    get_DC_output, create_bar_charts_DC_outputs_surface_groups, create_bar_charts_DC_outputs_module_groups, 
    create_bar_charts_DC_outputs_module_groups_whole,  create_bar_charts_DC_outputs_surface_groups_whole, get_PV_systems_table, whole_facade_tables_charts,
    
    #global variables
    MODELS, LOCATIONS, KEY_LIST, TILTS, ORIENTATIONS, BUILDINGS, SURFACES_TO_CALCULATE, BUILDING_SIZES,
   
    #parameters
    HouseRoofHeight
    ) 
    
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

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
AB = [[max_a_row['tilt'], 30], [max_a_row['orientation'],180]]
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
poaglobal_sum = POA_total.sum(axis = None)

poaglobal_sum = poaglobal_sum.rename(index = {'SurfaceASE_poa_global':'ASE',  'SurfaceASW_poa_global' : 'ASW','SurfaceBE_poa_global' : 'BE', 'SurfaceBS_poa_global' : 'BS', 'SurfaceBW_poa_global' : 'BW', 'RoofCS_poa_global' : 'CS', 'RoofCN_poa_global' : 'CN', 'RoofDW_poa_global' : 'DW', 'RoofDE_poa_global' : 'DE', 'RoofA_poa_global' : 'A', 'RoofB_poa_global' : 'B'})

#New_colors = ['red', 'crimson', 'purple','mediumslateblue', 'blue', 'deepskyblue','springgreen' ,'green', 'lime',  'yellow', 'orange']
New_colors_fr = ['peru', 'peru', 'peru','peru', 'peru', 'slategray','slategray' ,'slategray', 'slategray',  'slategray', 'slategray']

bar_sum = plt.bar(poaglobal_sum.index, poaglobal_sum, color = New_colors_fr)
bar_sum = plt.title('Barchart of sum POA global per surface orientation')
bar_sum = plt.xlabel('Surface orientation')
bar_sum = plt.ylabel('Sum of POA values in kWh/m2')

colors = {'Façade':'peru', 'Roof':'slategray'}         
labels = list(colors.keys())
handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
plt.legend(handles, labels)
plt.grid(axis = 'x')
plt.show(bar_sum)

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


###SUB-QUESTION 3.2 - get the dc power outputs

p_mp_values = pd.DataFrame(index = Eind_data.index)

for surface in Surfaces_angles_areas.columns:
    for module in ['HIT', 'CdTe', 'monoSi']:
        module_dc = get_DC_output(Eind_data, Surfaces_angles_areas, all_surface_POA_data, surface, module)

        p_mp_values[module+surface+'_p_mp'] = module_dc[surface+'_p_mp']

###SUB-QUESTION 3.3 - put annual yield into bar chart (annual yield = p_mp.sum() = sum of dc power)

p_mp_sums = p_mp_values.sum(axis=0)

module_yields = pd.DataFrame(columns = ['surface','module','annualyield'])

module_yields['surface'] = BUILDINGS_df_update.columns.repeat(3)
module_yields['module'] = ['HIT','CdTe', 'monoSi']*11
module_yields['annualyield'] = p_mp_sums.values/1000

#create the bar charts in either surface or module type groupings    
create_bar_charts_DC_outputs_surface_groups(module_yields)
create_bar_charts_DC_outputs_module_groups(module_yields)

#re-create the bar charts in either surface or module type groupings but this time per whole facade, not /m2  
module_yields_whole_facade = whole_facade_tables_charts(Eind_data, Surfaces_angles_areas, all_surface_POA_data, BUILDINGS_df_update)
module_yields_whole_facade
create_bar_charts_DC_outputs_module_groups_whole(module_yields_whole_facade)
create_bar_charts_DC_outputs_surface_groups_whole(module_yields_whole_facade)

###SUB-QUESTION 3.4 - create a PV systems table (note its not dynamic, if we change the data we need to change this function)
PV_table = get_PV_systems_table(BUILDINGS_df_update, Surfaces_Panel_info)
PV_table

#%%
"""Question 4"""

#4.1 AC modeling
#Re-arange data to easier names and only MonoSi module
MonoSi_values = p_mp_values.drop(columns = ['HITSurfaceASE_p_mp', 'CdTeSurfaceASE_p_mp','HITSurfaceASW_p_mp', 'CdTeSurfaceASW_p_mp','HITSurfaceBE_p_mp', 'CdTeSurfaceBE_p_mp','HITSurfaceBS_p_mp', 'CdTeSurfaceBS_p_mp','HITSurfaceBW_p_mp', 'CdTeSurfaceBW_p_mp', 'HITRoofCS_p_mp', 'CdTeRoofCS_p_mp', 'HITRoofCN_p_mp', 'CdTeRoofCN_p_mp', 'HITRoofDW_p_mp', 'CdTeRoofDW_p_mp', 'HITRoofDE_p_mp', 'CdTeRoofDE_p_mp', 'HITRoofA_p_mp', 'CdTeRoofA_p_mp', 'HITRoofB_p_mp', 'CdTeRoofB_p_mp'])
MonoSi_values = MonoSi_values.rename(columns = {'monoSiSurfaceASE_p_mp':'ASE',  'monoSiSurfaceASW_p_mp' : 'ASW','monoSiSurfaceBE_p_mp' : 'BE', 'monoSiSurfaceBS_p_mp' : 'BS', 'monoSiSurfaceBW_p_mp' : 'BW', 'monoSiRoofCS_p_mp' : 'CS', 'monoSiRoofCN_p_mp' : 'CN', 'monoSiRoofDW_p_mp' : 'DW', 'monoSiRoofDE_p_mp' : 'DE', 'monoSiRoofA_p_mp' : 'A', 'monoSiRoofB_p_mp' : 'B'})

#DC to AC conversion
Pac0 = 280
nnom = 0.96
zeta = MonoSi_values/(Pac0/nnom)
eff = -0.0162*zeta-0.0059/zeta+0.9858
Power_AC = (eff * MonoSi_values)


#4.2 bar chart of sums per surface
#Sum of AC
Power_AC_sum = Power_AC.sum(axis = None) #still in kWh per m2

Area_per_surface = np.transpose(Surfaces_angles_areas)
Area_per_surface = Area_per_surface.drop(columns = ['tilt', 'orientation'])
Area_per_surface = Area_per_surface.rename(index = {'SurfaceASE' : 'ASE', 'SurfaceASW' : 'ASW', 'SurfaceBE' : 'BE', 'SurfaceBS' : 'BS', 'SurfaceBW' : 'BW', 'RoofCS' : 'CS', 'RoofCN' : 'CN', 'RoofDW' : 'DW', 'RoofDE' : 'DE','RoofA' : 'A','RoofB' : 'B'})
Power_AC_sum_total = Power_AC_sum.values * Area_per_surface['Area']

#Bar chart of sums
New_colors_fr = ['peru', 'peru', 'peru','peru', 'peru', 'slategray','slategray' ,'slategray', 'slategray',  'slategray', 'slategray']

bar_AC = plt.bar(Power_AC_sum_total.index, Power_AC_sum_total, bottom = None,align='center', data = None, color = New_colors_fr)
bar_AC = plt.title('Barchart of sum AC per surface orientation')
bar_AC = plt.xlabel('Surface orientation')
bar_AC = plt.ylabel('Sum of AC values in kWh')

colors = {'Facade':'peru', 'Roof':'slategray'}         
labels = list(colors.keys())
handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
plt.legend(handles, labels)

plt.show(bar_AC)

#Barchart per building
BuildingA = Power_AC_sum_total.ASE + Power_AC_sum_total.ASW + Power_AC_sum_total.A
BuildingB = Power_AC_sum_total.BE + Power_AC_sum_total.BW + Power_AC_sum_total.BS + Power_AC_sum_total.B
BuildingC = Power_AC_sum_total.CS + Power_AC_sum_total.CN
BuildingD = Power_AC_sum_total.DW + Power_AC_sum_total.DE
AC_per_Building = pd.DataFrame(data = [BuildingA, BuildingB, BuildingC, BuildingD], index = ['A', 'B', 'C', 'D'])

bar_Buildings = plt.bar(AC_per_Building.index, AC_per_Building[0])
bar_Buildings = plt.title('Barchart of sum AC per Building')
bar_Buildings = plt.xlabel('Building')
bar_Buildings = plt.ylabel('Sum of AC values in kWh')

plt.show(bar_Buildings)
