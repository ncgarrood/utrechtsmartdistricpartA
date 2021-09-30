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


DC = pd.read_csv('Irradiance_2015_UPOT.csv', sep = ';', index_col = 'timestamp')
DC = DC.temp_air

Pac0 = 240
nnom = 0.96
zeta = DC/(Pac0/nnom)
eff = -0.0162*zeta-0.0059/zeta+0.9858
AC = eff*DC

