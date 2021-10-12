# -*- coding: utf-8 -*-
"""
Created on Sun Oct 10 21:51:38 2021

@author: Jens
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

from EBE_spyder_final import (Power_AC, Area_per_surface)

#4.3 plots of each building for 3 days: 23/4, 23/7 and 23/10
Power_AC_total = Power_AC*Area_per_surface['Area']
Power_AC_total = Power_AC_total/1000


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

dfmt = DateFormatter("%H") # proper formatting Year-month-day

fig, ((A_234, A_237, A_2310), (B_234, B_237, B_2310), (C_234, C_237, C_2310), (D_234, D_237, D_2310)) = plt.subplots(4, 3, figsize=(10, 15))
fig.suptitle('AC power per fascade per building per day')
A_234.plot(x4, yA4, label = 'Roof')
A_234.plot(x4, yASE4, label = 'SE fascade')
A_234.plot(x4, yASW4, label = 'SW fascade')
A_234.legend(loc='upper right', prop={'size': 6})
A_234.set_xlabel('time')
A_234.set_ylabel('AC power (kW)')
A_234.set_title('Building A on 23 April 2019')
A_234.xaxis.set_major_formatter(dfmt)
A_234.grid(False)
A_237.plot(x7, yA7, label = 'Roof')
A_237.plot(x7, yASE7, label = 'SE fascade')
A_237.plot(x7, yASW7, label = 'SW fascade')
A_237.legend(loc='upper right', prop={'size': 6})
A_237.set_xlabel('time')
A_237.set_ylabel('AC power (kW)')
A_237.set_title('Building A on 23 July 2019')
A_237.xaxis.set_major_formatter(dfmt)
A_237.grid(False)
A_2310.plot(x10, yA10, label = 'Roof')
A_2310.plot(x10, yASE10, label = 'SE fascade')
A_2310.plot(x10, yASW10, label = 'SW fascade')
A_2310.legend(loc='upper right', prop={'size': 6})
A_2310.set_xlabel('time')
A_2310.set_ylabel('AC power (kW)')
A_2310.set_title('Building A on 23 October 2019')
A_2310.xaxis.set_major_formatter(dfmt)
A_2310.grid(False)

B_234.plot(x4, yB4, label = 'Roof')
B_234.plot(x4, yBE4, label = 'E fascade')
B_234.plot(x4, yBS4, label = 'S fascade')
B_234.plot(x4, yBW4, label = 'W fascade')
B_234.legend(loc='upper right', prop={'size': 6})
B_234.set_xlabel('time')
B_234.set_ylabel('AC power (kW)')
B_234.set_title('Building B on 23 April 2019')
B_234.xaxis.set_major_formatter(dfmt)
B_234.grid(False)
B_237.plot(x7, yB7, label = 'Roof')
B_237.plot(x7, yBE7, label = 'E fascade')
B_237.plot(x7, yBS7, label = 'S fascade')
B_237.plot(x7, yBW7, label = 'W fascade')
B_237.legend(loc='upper right', prop={'size': 6})
B_237.set_xlabel('time')
B_237.set_ylabel('AC power (kW)')
B_237.set_title('Building B on 23 July 2019')
B_237.xaxis.set_major_formatter(dfmt)
B_237.grid(False)
B_2310.plot(x10, yB10, label = 'Roof')
B_2310.plot(x10, yBE10, label = 'E fascade')
B_2310.plot(x10, yBS10, label = 'S fascade')
B_2310.plot(x10, yBW10, label = 'W fascade')
B_2310.legend(loc='upper right', prop={'size': 6})
B_2310.set_xlabel('time')
B_2310.set_ylabel('AC power (kW)')
B_2310.set_title('Building B on 23 October 2019')
B_2310.xaxis.set_major_formatter(dfmt)
B_2310.grid(False)

C_234.plot(x4, yCS4, label = 'S roof')
C_234.plot(x4, yCN4, label = 'N roof')
C_234.legend(loc='upper right', prop={'size': 6})
C_234.set_xlabel('time')
C_234.set_ylabel('AC power (kW)')
C_234.set_title('Building C on 23 April 2019')
C_234.xaxis.set_major_formatter(dfmt)
C_234.grid(False)
C_237.plot(x7, yCS7, label = 'S roof')
C_237.plot(x7, yCN7, label = 'N roof')
C_237.legend(loc='upper right', prop={'size': 6})
C_237.set_xlabel('time')
C_237.set_ylabel('AC power (kW)')
C_237.set_title('Building C on 23 July 2019')
C_237.xaxis.set_major_formatter(dfmt)
C_237.grid(False)
C_2310.plot(x10, yCS10, label = 'S roof')
C_2310.plot(x10, yCN10, label = 'N roof')
C_2310.legend(loc='upper right', prop={'size': 6})
C_2310.set_xlabel('time')
C_2310.set_ylabel('AC power (kW)')
C_2310.set_title('Building C on 23 Cctober 2019')
C_2310.xaxis.set_major_formatter(dfmt)
C_2310.grid(False)

D_234.plot(x4, yDE4, label = 'E roof')
D_234.plot(x4, yDW4, label = 'W roof')
D_234.legend(loc='upper right', prop={'size': 6})
D_234.set_xlabel('time')
D_234.set_ylabel('AC power (kW)')
D_234.set_title('Building D on 23 April 2019')
D_234.xaxis.set_major_formatter(dfmt)
D_234.grid(False)
D_237.plot(x7, yDE7, label = 'E roof')
D_237.plot(x7, yDW7, label = 'W roof')
D_237.legend(loc='upper right', prop={'size': 6})
D_237.set_xlabel('time')
D_237.set_ylabel('AC power (kW)')
D_237.set_title('Building D on 23 July 2019')
D_237.xaxis.set_major_formatter(dfmt)
D_237.grid(False)
D_2310.plot(x10, yDE10, label = 'E roof')
D_2310.plot(x10, yDW10, label = 'W roof')
D_2310.legend(loc='upper right', prop={'size': 6})
D_2310.set_xlabel('time')
D_2310.set_ylabel('AC power (kW)')
D_2310.set_title('Building D on 23 October 2019')
D_2310.xaxis.set_major_formatter(dfmt)
D_2310.grid(False)
fig.tight_layout()