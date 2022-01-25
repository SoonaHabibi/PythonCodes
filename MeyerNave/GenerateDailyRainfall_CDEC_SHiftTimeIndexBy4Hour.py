# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 10:27:36 2020

@author: sardekani
"""

import pandas as pd
import sys
sys.path.append("//westfolsom/office/Python/WEST_Python_FunctionAug2019/")
import BasicFunction_py3 as BF   
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# from datetime import datetime
BaseDir="//westfolsom/Projects/2020/Meyers Nave/"
PlotDir="//westfolsom/Projects/2020/Meyers Nave/CDEC/plot/"
if not os.path.exists(PlotDir): os.mkdir(PlotDir)

pptDataDir="//westfolsom/Projects/2020/Meyers Nave/CDEC/"
if not os.path.exists(pptDataDir): os.mkdir(pptDataDir)

csvNoNA_out = pptDataDir+'rainfall_NoNA.csv'
# Just in order to skip running the previouse lines
df = pd.read_csv(csvNoNA_out, parse_dates=['OBS DATE'], index_col='OBS DATE')
df = df.loc['1998-12':'2017-12'] 
df.index = df.index + pd.DateOffset(hours=4)       
#Convert Hourly to daily Data
df_daily = pd.DataFrame(df['hrly_value'].resample('D', label='right').sum())
df_daily.columns = ['daily_value']
df_daily['UNITS'] = ['INCHES']*len(df_daily)
daily_csv = pptDataDir+'ChangeTimeZone/DailyRainfall.csv'
df_daily.to_csv(daily_csv)

df_daily=pd.read_csv(daily_csv, parse_dates=[0],index_col='OBS DATE')
#create boxplot of number of days between different rainfall ranges
NumDay = {'NumD':[], 'RainRange':[]}

# Days with rainfall greater than 3 inches
df3_7 = df_daily[(df_daily['daily_value']>=3)&(df_daily['daily_value']<7)]
out3_7 = pptDataDir+ 'ChangeTimeZone/RainBetween3and7inch.csv'
df3_7.to_csv(out3_7)


for ij in range(1,7):
    df2=df_daily[(df_daily['daily_value']>=ij)&(df_daily['daily_value']<ij+1)]
    
    r=str(ij)+'-'+str(ij+1)
    NumDay['RainRange'].append(r)
    NumDay['NumD'].append(len(df2))
    
    out = pptDataDir+ 'ChangeTimeZone/RainBetween' + str(ij)+ 'and' + str(ij+1) + 'inch.csv'
    df2.to_csv(out)

NumDay_df = pd.DataFrame(NumDay)
NumDay_df['NumD'][2]=NumDay_df['NumD'][2]-1     #To manually remove 5/13/2005 events
stat_csv = pptDataDir+'ChangeTimeZone/NumOfDaySummary1.csv'
NumDay_df.to_csv(stat_csv)

plt.figure()
ax=sns.barplot(x='RainRange', y='NumD', data=NumDay, color='blue')
ax.set_ylabel("  Number of Rainy Days \nDec 1998 to Dec 2017", fontweight='bold')
ax.set_xlabel("Rainfall Range (in)", fontweight='bold')
ax.set_title("Montecito Rain Gauge", fontweight='bold')
for p in ax.patches:
    ax.annotate(format(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 4), textcoords = 'offset points')
#plt.show()
out0 = PlotDir + 'Montecito_DailyHistogram2.jpg'
plt.savefig(out0, dpi=1000)
