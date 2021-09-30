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


DC = pd.read_csv('Irradiance_2015_UPOT.csv', sep = ';', index_col = 'timestamp')
DC = DC.temp_air

Pac0 = 240
nnom = 0.96
zeta = DC/(Pac0/nnom)
eff = -0.0162*zeta-0.0059/zeta+0.9858
AC = eff*DC

def create_bar_charts(roof:str):
    """Enter roof A or B and get the bar chart of it"""
    sns.set_theme(style="whitegrid")
    
    #filter the POA_sums dataframe by roof A and roof B
    POA_sums_RoofA_and_B = calculate_optimal_angles('dirindex', 'Eindhoven', SURFACES_TO_CALCULATE) #query on this, not optimal solution 
    POA_totals = POA_sums_RoofA_and_B[POA_sums_RoofA_and_B['surface'] == roof]
    
    # Draw a nested barplot by tilt and orientation
    q = sns.catplot(
        data = POA_totals, kind="bar",
        x="building surface", y="sum of POA global",
        ci = None, palette="dark", alpha=.6, height=6
    )
    q.despine(left=True)
    q.set(ylim=(0.8,1.3))
    q.set_axis_labels("Building surface", "Sum of POA_global [MW/m2]")