# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 12:47:16 2021

@author: wille
"""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

#from EBE_spyder_final.py import (POA_total)

POA_total_sums = POA_total.sum(axis = None, skipna = None, level=None, numeric_only=None, min_count=0)
POA_total_sums = POA_total_sums.rename(index = {'SurfaceASE_poa_global':'ASE',  'SurfaceASW_poa_global' : 'ASW','SurfaceBE_poa_global' : 'BE', 'SurfaceBS_poa_global' : 'BS', 'SurfaceBW_poa_global' : 'BW', 'RoofCS_poa_global' : 'CS', 'RoofCN_poa_global' : 'CN', 'RoofDW_poa_global' : 'DW', 'RoofDE_poa_global' : 'DE', 'RoofA_poa_global' : 'A', 'RoofB_poa_global' : 'B'})

barcolor = ['red', 'red','red','red','red','blue','blue','blue','blue','blue','blue']
barsum = plt.bar(POA_total_sums.index, POA_total_sums, color = barcolor)

colors = {'Facade':'red', 'Roof':'blue'}         
labels = list(colors.keys())
handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
plt.legend(handles, labels)

#plt.show(barsum)

#%%

poaglobal_sum = POA_total.sum(axis = None)

poaglobal_sum = poaglobal_sum.rename(index = {'SurfaceASE_poa_global':'ASE',  'SurfaceASW_poa_global' : 'ASW','SurfaceBE_poa_global' : 'BE', 'SurfaceBS_poa_global' : 'BS', 'SurfaceBW_poa_global' : 'BW', 'RoofCS_poa_global' : 'CS', 'RoofCN_poa_global' : 'CN', 'RoofDW_poa_global' : 'DW', 'RoofDE_poa_global' : 'DE', 'RoofA_poa_global' : 'A', 'RoofB_poa_global' : 'B'})

New_colors = ['red', 'crimson', 'purple','mediumslateblue', 'blue', 'deepskyblue','springgreen' ,'green', 'lime',  'yellow', 'orange']
New_colors_fr = ['red', 'red', 'red','red', 'red', 'blue','blue' ,'blue', 'blue',  'blue', 'blue']

bar_sum = plt.bar(poaglobal_sum.index, poaglobal_sum, color = New_colors_fr)
bar_sum = plt.title('Barchart of sum POA global per surface orientation')
bar_sum = plt.xlabel('Surface orientation')
bar_sum = plt.ylabel('Sum of POA values in kWh/m2')

colors = {'Facade':'red', 'Roof':'blue'}         
labels = list(colors.keys())
handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
plt.legend(handles, labels)

plt.show(bar_sum)

#%%

#Re-arange data to easier names and only MonoSi module
from EBE_spyder_final import p_mp_values
MonoSi_values = p_mp_values.drop(columns = ['HITSurfaceASE_p_mp', 'CdTeSurfaceASE_p_mp','HITSurfaceASW_p_mp', 'CdTeSurfaceASW_p_mp','HITSurfaceBE_p_mp', 'CdTeSurfaceBE_p_mp','HITSurfaceBS_p_mp', 'CdTeSurfaceBS_p_mp','HITSurfaceBW_p_mp', 'CdTeSurfaceBW_p_mp', 'HITRoofCS_p_mp', 'CdTeRoofCS_p_mp', 'HITRoofCN_p_mp', 'CdTeRoofCN_p_mp', 'HITRoofDW_p_mp', 'CdTeRoofDW_p_mp', 'HITRoofDE_p_mp', 'CdTeRoofDE_p_mp', 'HITRoofA_p_mp', 'CdTeRoofA_p_mp', 'HITRoofB_p_mp', 'CdTeRoofB_p_mp'])
MonoSi_values = MonoSi_values.rename(columns = {'monoSiSurfaceASE_p_mp':'ASE',  'monoSiSurfaceASW_p_mp' : 'ASW','monoSiSurfaceBE_p_mp' : 'BE', 'monoSiSurfaceBS_p_mp' : 'BS', 'monoSiSurfaceBW_p_mp' : 'BW', 'monoSiRoofCS_p_mp' : 'CS', 'monoSiRoofCN_p_mp' : 'CN', 'monoSiRoofDW_p_mp' : 'DW', 'monoSiRoofDE_p_mp' : 'DE', 'monoSiRoofA_p_mp' : 'A', 'monoSiRoofB_p_mp' : 'B'})

#DC to AC conversion
Pac0 = 280
nnom = 0.96
zeta = MonoSi_values/(Pac0/nnom)
eff = -0.0162*zeta-0.0059/zeta+0.9858
Power_AC = (eff * MonoSi_values)

#Sum of AC
Power_AC_sum = Power_AC.sum(axis = None)

#Bar chart of sums
bar_AC = plt.bar(Power_AC_sum.index, Power_AC, color = New_colors_fr)
bar_AC = plt.title('Barchart of sum AC per surface orientation')
bar_AC = plt.xlabel('Surface orientation')
bar_AC = plt.ylabel('Sum of AC values in kWh/m2')

colors = {'Facade':'red', 'Roof':'blue'}         
labels = list(colors.keys())
handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
plt.legend(handles, labels)

plt.show(bar_sum)