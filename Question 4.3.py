# -*- coding: utf-8 -*-
"""
Created on Sun Oct 10 21:51:38 2021

@author: Jens
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from EBE_spyder_final import (Power_AC, Area_per_surface)

#4.3 plots of each building for 3 days: 23/4, 23/7 and 23/10
Power_AC_total = Power_AC*Area_per_surface['Area']

x4 = Power_AC_total.loc['2019-04-23'].index
x7 = Power_AC_total.loc['2019-07-23'].index
x10 = Power_AC_total.loc['2019-10-23'].index

#Building A
yA4 = Power_AC_total.loc['2019-04-23'].A
yASE4 = Power_AC_total.loc['2019-04-23'].ASE
yASW4 = Power_AC_total.loc['2019-04-23'].ASW

yA7 = Power_AC_total.loc['2019-07-23'].A
yASE7 = Power_AC_total.loc['2019-07-23'].ASE
yASW7 = Power_AC_total.loc['2019-07-23'].ASW

yA10 = Power_AC_total.loc['2019-10-23'].A
yASE10 = Power_AC_total.loc['2019-10-23'].ASE
yASW10 = Power_AC_total.loc['2019-10-23'].ASW

#Building B
yB4 = Power_AC_total.loc['2019-04-23'].B
yBE4 = Power_AC_total.loc['2019-04-23'].BE
yBS4 = Power_AC_total.loc['2019-04-23'].BS
yBW4 = Power_AC_total.loc['2019-04-23'].BW

yB7 = Power_AC_total.loc['2019-07-23'].B
yBE7 = Power_AC_total.loc['2019-07-23'].BE
yBS7 = Power_AC_total.loc['2019-07-23'].BS
yBW7 = Power_AC_total.loc['2019-07-23'].BW

yB10 = Power_AC_total.loc['2019-10-23'].B
yBE10 = Power_AC_total.loc['2019-10-23'].BE
yBS10 = Power_AC_total.loc['2019-10-23'].BS
yBW10 = Power_AC_total.loc['2019-10-23'].BW

#Building C
yCS4 = Power_AC_total.loc['2019-04-23'].CS
yCN4 = Power_AC_total.loc['2019-04-23'].CN

yCS7 = Power_AC_total.loc['2019-07-23'].CS
yCN7 = Power_AC_total.loc['2019-07-23'].CN

yCS10 = Power_AC_total.loc['2019-10-23'].CS
yCN10 = Power_AC_total.loc['2019-10-23'].CN

#Building D
yDE4 = Power_AC_total.loc['2019-04-23'].DE
yDW4 = Power_AC_total.loc['2019-04-23'].DW

yDE7 = Power_AC_total.loc['2019-07-23'].DE
yDW7 = Power_AC_total.loc['2019-07-23'].DW

yDE10 = Power_AC_total.loc['2019-10-23'].DE
yDW10 = Power_AC_total.loc['2019-10-23'].DW

fig, ((A_234, A_237, A_2310), (B_234, B_237, B_2310), (C_234, C_237, C_2310), (D_234, D_237, D_2310)) = plt.subplots(4, 3)
fig.suptitle('AC power per facsade per building per day')
A_234.plot(x4, yA4)
A_234.plot(x4, yASE4)
A_234.plot(x4, yASW4)
A_237.plot(x7, yA7)
A_237.plot(x7, yASE7)
A_237.plot(x7, yASW7)
A_2310.plot(x10, yA10)
A_2310.plot(x10, yASE10)
A_2310.plot(x10, yASW10)

B_234.plot(x4, yB4)
B_234.plot(x4, yBE4)
B_234.plot(x4, yBS4)
B_234.plot(x4, yBW4)
B_237.plot(x7, yB7)
B_237.plot(x7, yBE7)
B_237.plot(x7, yBS7)
B_237.plot(x7, yBW7)
B_2310.plot(x10, yB10)
B_2310.plot(x10, yBE10)
B_2310.plot(x10, yBS10)
B_2310.plot(x10, yBW10)

C_234.plot(x4, yCS4)
C_234.plot(x4, yCN4)
C_237.plot(x7, yCS7)
C_237.plot(x7, yCN7)
C_2310.plot(x10, yCS10)
C_2310.plot(x10, yCN10)

D_234.plot(x4, yDE4)
D_234.plot(x4, yDW4)
D_237.plot(x7, yDE7)
D_237.plot(x7, yDW7)
D_2310.plot(x10, yDE10)
D_2310.plot(x10, yDW10)