# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 15:28:31 2021

@author: Jens
"""

import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import pvlib
import numpy as np
import seaborn as sns

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
New_colors_fr = ['red', 'red', 'red','red', 'red', 'blue','blue' ,'blue', 'blue',  'blue', 'blue']
bar_AC = plt.bar(Power_AC_sum.index, Power_AC_sum, bottom = None,align='center', data = None, color = New_colors_fr)
bar_AC = plt.title('Barchart of sum AC per surface orientation')
bar_AC = plt.xlabel('Surface orientation')
bar_AC = plt.ylabel('Sum of AC values in kWh/m2')

colors = {'Facade':'red', 'Roof':'blue'}         
labels = list(colors.keys())
handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
plt.legend(handles, labels)

plt.show(bar_AC)
