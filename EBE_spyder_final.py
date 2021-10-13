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
    get_DC_output, create_bar_charts_DC_outputs_module_groups, get_PV_systems_table, 
    
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
BUILDINGS_df_update = BUILDINGS_df.merge(ABdf, left_index=True, right_index=True, how = 'left')
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
#this one works when you run only the selected lines, it gets fucked when you run the whole cell, not sure why.
def create_bar_sum_poa_each_facade(POA_total): 
    poaglobal_sum = POA_total.sum(axis = None)
    poaglobal_sum = poaglobal_sum.rename(index = {'SurfaceASE_poa_global':'ASE',  'SurfaceASW_poa_global' : 'ASW','SurfaceBE_poa_global' : 'BE', 'SurfaceBS_poa_global' : 'BS', 'SurfaceBW_poa_global' : 'BW', 'RoofCS_poa_global' : 'CS', 'RoofCN_poa_global' : 'CN', 'RoofDW_poa_global' : 'DW', 'RoofDE_poa_global' : 'DE', 'RoofA_poa_global' : 'A', 'RoofB_poa_global' : 'B'})
    poaglobal_sum = poaglobal_sum/1000 #convert to kW
    
    #New_colors = ['red', 'crimson', 'purple','mediumslateblue', 'blue', 'deepskyblue','springgreen' ,'green', 'lime',  'yellow', 'orange']
    New_colors_fr = ['peru', 'peru', 'peru','peru', 'peru', 'slategray','slategray' ,'slategray', 'slategray',  'slategray', 'slategray']
    
    bar_sum = plt.bar(poaglobal_sum.index, poaglobal_sum, color = New_colors_fr)
    bar_sum = plt.xlabel('Surface')
    bar_sum = plt.ylabel('Sum of Total POA [kWh/m2]')
    
    colors = {'Façade':'peru', 'Roof':'slategray'}         
    labels = list(colors.keys())
    handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
    plt.legend(handles, labels)
    plt.grid(axis = 'x')
    plt.show(bar_sum)
    
create_bar_sum_poa_each_facade(POA_total)

#%% alternative option for 2.6

POA_surface = pd.read_excel("2.6 bar.xlsx")

def create_bar_charts_DC_outputs_module_groups(POA_surface):
    
    sns.set_theme(style="whitegrid")
    
    # Draw a nested barplot by tilt and orientation
    g = sns.catplot(
        data = POA_surface, kind="bar",
        x="Surface", y="SumPOA", hue=None,
        ci = None, palette="dark", alpha=.6, height=6
    )
    g.despine(left=True)
    g.set_axis_labels("", "Annual Irradiance [kWh/m2]")
    g.set_xticklabels(rotation=90)
    
create_bar_charts_DC_outputs_module_groups(POA_surface)
#%%

# added a text string here of some ideas for this one, was quite lazy answering it, think we should add more
"""best is 135 orientation, 30 tilt for A, and 20 tilt for B

seems  plausible since when you compare RoofB with SurfaceCS and SurfaceBS (all same orientation):
RoofB - tilt 30 - POA at 12.00 = 38
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

module_yields_per_m2 = pd.read_excel("annualyieldpermodule.xlsx")
create_bar_charts_DC_outputs_module_groups(module_yields_per_m2)

###SUB-QUESTION 3.4 - create a PV systems table (note its not dynamic, if we change the data we need to change this function)
PV_table = get_PV_systems_table(BUILDINGS_df_update, Surfaces_Panel_info)
PV_table['Total Capacity'] = round(PV_table['Total Capacity']/1000)


#%%
"""Question 4"""

#4.1 AC modeling
#Re-arange data to easier names and only HIT module
HIT_values = p_mp_values.drop(columns = ['monoSiSurfaceASE_p_mp', 'CdTeSurfaceASE_p_mp','monoSiSurfaceASW_p_mp', 'CdTeSurfaceASW_p_mp','monoSiSurfaceBE_p_mp', 'CdTeSurfaceBE_p_mp','monoSiSurfaceBS_p_mp', 'CdTeSurfaceBS_p_mp','monoSiSurfaceBW_p_mp', 'CdTeSurfaceBW_p_mp', 'monoSiRoofCS_p_mp', 'CdTeRoofCS_p_mp', 'monoSiRoofCN_p_mp', 'CdTeRoofCN_p_mp', 'monoSiRoofDW_p_mp', 'CdTeRoofDW_p_mp', 'monoSiRoofDE_p_mp', 'CdTeRoofDE_p_mp', 'monoSiRoofA_p_mp', 'CdTeRoofA_p_mp', 'monoSiRoofB_p_mp', 'CdTeRoofB_p_mp'])
HIT_values = HIT_values.rename(columns = {'HITSurfaceASE_p_mp':'ASE',  'HITSurfaceASW_p_mp' : 'ASW','HITSurfaceBE_p_mp' : 'BE', 'HITSurfaceBS_p_mp' : 'BS', 'HITSurfaceBW_p_mp' : 'BW', 'HITRoofCS_p_mp' : 'CS', 'HITRoofCN_p_mp' : 'CN', 'HITRoofDW_p_mp' : 'DW', 'HITRoofDE_p_mp' : 'DE', 'HITRoofA_p_mp' : 'A', 'HITRoofB_p_mp' : 'B'})


#DC to AC conversion
Pac0 = 240 #capacity of HIT in parameters file
nnom = 0.96
zeta = HIT_values/(Pac0/nnom)
eff = -0.0162*zeta-0.0059/zeta+0.9858
Power_AC = (eff * HIT_values)
Power_AC[Power_AC < 0 ] = 0
Power_AC[Power_AC > Pac0] = Pac0

#4.2 bar chart of sums per surface

## calculated AC totals per surface

Surfaces_Panel_info_trans = Surfaces_Panel_info.transpose()
Power_AC_sum = pd.Series(data=Power_AC.sum(axis = None), name = 'ACperModule') #still in Wh per MODULE
Power_AC_sum = Power_AC_sum.to_frame(name = 'ACperModule')
Power_AC_sum.index = Surfaces_Panel_info_trans.index
Power_AC_sum['no. panels']  = Surfaces_Panel_info_trans['Number_panels_HIT']
Power_AC_sum['ACperFacade'] = Power_AC_sum['no. panels']*Power_AC_sum['ACperModule']/10**6 #now in MWh/facade

Power_AC_sum = Power_AC_sum.rename(index = {'SurfaceASE' : 'Façade ASE', 'SurfaceASW' : 'Façade ASW', 'SurfaceBE' : 'Façade BE', 'SurfaceBS' : 'Façade BS', 'SurfaceBW' : 'Façade BW', 'RoofCS' : 'Roof CS', 'RoofCN' : 'Roof CN', 'RoofDW' : 'Roof DW', 'RoofDE' : 'Roof DE','RoofA' : 'Roof A','RoofB' : 'Roof B'})
Power_AC_sum['surface'] = Power_AC_sum.index

def create_bar_charts_AC_facade(Power_AC_sum):
    sns.set_theme(style="whitegrid")
    
    g = sns.catplot(
        data = Power_AC_sum, kind="bar",
        x="surface", y="ACperFacade", hue=None,
        ci = None, palette="dark", alpha=.6, height=6
    )
    g.despine(left=True)
    g.set_xticklabels(rotation=90)
    g.set_axis_labels("", "Annual AC Energy [MWh]")


create_bar_charts_AC_facade(Power_AC_sum)

## calculated AC totals per building

ACA = Power_AC_sum['ACperFacade']['Façade ASE']+Power_AC_sum['ACperFacade']['Façade ASW']+Power_AC_sum['ACperFacade']['Roof A']
ACB = Power_AC_sum['ACperFacade']['Façade BE']+Power_AC_sum['ACperFacade']['Façade BS']+Power_AC_sum['ACperFacade']['Roof B']
ACC = Power_AC_sum['ACperFacade']['Roof CS']+Power_AC_sum['ACperFacade']['Roof CN']
ACD = Power_AC_sum['ACperFacade']['Roof DE']+Power_AC_sum['ACperFacade']['Roof DW']
Power_AC_sum_buildings = pd.DataFrame(index = ['Building A', 'Building B', 'Building C', 'Building D'] , columns = ['AC per Building'], data = [ACA,ACB,ACC,ACD] )

Power_AC_sum_buildings['surface'] = Power_AC_sum_buildings.index

def create_bar_charts_AC_building(Power_AC_sum_buildings):
    sns.set_theme(style="whitegrid")

    g = sns.catplot(
        data = Power_AC_sum_buildings, kind="bar",
        x="surface", y="AC per Building", hue=None,
        ci = None, palette="dark", alpha=.6, height=6
    )
    g.despine(left=True)
    
    g.set_axis_labels("", "Annual AC Energy [MWh]")


create_bar_charts_AC_building(Power_AC_sum_buildings)



# #Bar chart of sums
# New_colors_fr = ['peru', 'peru', 'peru','peru', 'peru', 'slategray','slategray' ,'slategray', 'slategray',  'slategray', 'slategray']

# bar_AC = plt.bar(Power_AC_sum_total.index, Power_AC_sum_total, bottom = None,align='center', data = None, color = New_colors_fr)
# bar_AC = plt.title('Barchart of sum AC per surface')
# bar_AC = plt.xlabel('Surface orientation')
# bar_AC = plt.ylabel('Sum of AC values in kWh')

# colors = {'Facade':'peru', 'Roof':'slategray'}         
# labels = list(colors.keys())
# handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
# plt.legend(handles, labels)

# plt.show(bar_AC)

# #Barchart per building
# BuildingA = Power_AC_sum_total.ASE + Power_AC_sum_total.ASW + Power_AC_sum_total.A
# BuildingB = Power_AC_sum_total.BE + Power_AC_sum_total.BW + Power_AC_sum_total.BS + Power_AC_sum_total.B
# BuildingC = Power_AC_sum_total.CS + Power_AC_sum_total.CN
# BuildingD = Power_AC_sum_total.DW + Power_AC_sum_total.DE
# AC_per_Building = pd.DataFrame(data = [BuildingA, BuildingB, BuildingC, BuildingD], index = ['A', 'B', 'C', 'D'])

# bar_Buildings = plt.bar(AC_per_Building.index, AC_per_Building[0])
# bar_Buildings = plt.title('Barchart of sum AC per Building')
# bar_Buildings = plt.xlabel('Building')
# bar_Buildings = plt.ylabel('Sum of AC values in kWh')

# plt.show(bar_Buildings)
