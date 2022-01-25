# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 14:08:43 2020

@author: sardekani
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

pptDataDir="//westfolsom/Projects/2020/Meyers Nave/CDEC/"
csvNoNA_out = '//westfolsom/Projects/2020/Meyers Nave/CDEC/rainfall_NoNA.csv'
PlotDir="//westfolsom/Projects/2020/Meyers Nave/CDEC/plot/"
df = pd.read_csv(csvNoNA_out, parse_dates=['OBS DATE'], index_col='OBS DATE')

# extract data from Dec 1998 to Dec 2017
df_1998_2017_h = df['1998/12':'2017/12']
        
#Convert Hourly to daily Data
df_1998_2017_d = pd.DataFrame(df_1998_2017_h['hrly_value'].resample('D').sum())
df_1998_2017_d.columns = ['daily_value']
df_1998_2017_d['UNITS'] = ['INCHES']*len(df_1998_2017_d )
daily_csv = pptDataDir+'DailyRainfall_1998_2017.csv'
df_1998_2017_d.to_csv(daily_csv)

#create boxplot of number of days between different rainfall ranges
NumDay = {'NumD':[], 'RainRange':[]}

for ij in range(0,7):
    df2=df_1998_2017_d[(df_1998_2017_d['daily_value']>ij)&(df_1998_2017_d['daily_value']<=ij+1)]
    
    r=str(ij)+'-'+str(ij+1)
    NumDay['RainRange'].append(r)
    NumDay['NumD'].append(len(df2))
    
    out = pptDataDir+ 'RainBetween' + str(ij)+ 'and' + str(ij+1) + 'inch_1998_2017_d.csv'
    df2.to_csv(out)

NumDay_df = pd.DataFrame(NumDay)
stat_csv = pptDataDir+'NumOfDaySummary_1998_2017_d.csv'
NumDay_df.to_csv(stat_csv)

# Daily Histogram, Dec 1998 to Dec 2017
plt.figure()
ax=sns.barplot(x='RainRange', y='NumD', data=NumDay, color='blue')
ax.set_ylabel(" Number of Rainy Days \nDec 1998 to Dec 2017", fontweight='bold')
ax.set_xlabel("Rainfall Range (in)", fontweight='bold')
ax.set_title("Montecito Rain Gage", fontweight='bold')
for p in ax.patches:
    ax.annotate(format(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 4), textcoords = 'offset points')
#plt.show()
out0 = PlotDir + 'Montecito_DailyHistogram_1998_2017_d.jpg'
plt.savefig(out0, dpi=1000)



#
# Create histogram for hourly data-based on the rainfall intensity definitation 
#
NumHr1 = {'NumH':[], 'RainRange':[]}
IntRange = [0,0.1,0.3]
cat0 = ['Light Rain (0-0.1)', 'Moderate Rain (0.1-0.3)', 'Heavy Rain (>0.3)']
cat1 = ['LightRain', 'ModerateRain', 'HeavyRain']

for ij in range(len(IntRange)):
    if ij!=2:
        df3 = df_1998_2017_h[(df_1998_2017_h['hrly_value']>IntRange[ij])&(df_1998_2017_h['hrly_value']<=IntRange[ij+1])]
    else:
        df3=df_1998_2017_h[(df_1998_2017_h['hrly_value']>IntRange[ij])]
        
    NumHr1['RainRange'].append(cat0[ij])
    NumHr1['NumH'].append(len(df3))
    
    out2 = pptDataDir+ 'Hourly_RainIn'+ cat1[ij]+ 'Range_1998_2017.csv'
    df3.drop('VALUE', axis=1).to_csv(out2)

NumHr_df1 = pd.DataFrame(NumHr1)
stat_csv2 = pptDataDir+'NumOfHourSumm_RainIntenDef_1998_2017.csv'
NumHr_df1.to_csv(stat_csv2, index=False)

#histogram
plt.figure()
ax=sns.barplot(x='RainRange', y='NumH', data=NumHr1,palette=('green', 'yellow', 'red'))
#ax=plt.bar(NumHr1['RainRange'], NumHr1['NumH'])
#ax.text(1, NumHr1['NumH']+ .25, str(NumHr1['NumH']), color='black')
ax.set_ylabel(" Number of Rainy hours \nDec 1998 to Dec 2017", fontweight='bold')
ax.set_xlabel("Rainfall Intensity (in/hr)", fontweight='bold')
ax.set_title("Montecito Rain Gage", fontweight='bold')
for p in ax.patches:
    ax.annotate(format(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 3.5), textcoords = 'offset points')
#plt.show()
out0 = PlotDir + 'Montecito_hourlyHistogram_RainIntenDef_1998_2017.jpg'
plt.tight_layout()
plt.savefig(out0, dpi=1000)


