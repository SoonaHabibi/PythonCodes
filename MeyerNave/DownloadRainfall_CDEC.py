# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 11:07:14 2020

@author: sardekani
"""

#This code downloads data California snow course SWE data adjusted (sensor 82) and raw (sensor 3)
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

#search CDEC csv for hourlyy Precipitation (in) data                    
station_id = 'MTC'
dur_code = 'H'
sensor_num = 2
start_date = '1900-01-01'
end_date = '2020-06-01'
url = 'http://cdec.water.ca.gov/dynamicapp/req/CSVDataServlet'
url =  url+'?Stations=' + station_id 
url =  url+'&dur_code=' + dur_code 
url =  url+'&SensorNums=' + str(sensor_num)
url =  url+'&Start=' + start_date 
url =  url+'&End=' + end_date

csv_out = pptDataDir+'rainfall1.csv'
dat82 = pd.read_csv(url, parse_dates=[4,5], index_col='DATE TIME', na_values='---', error_bad_lines=(False))
dat82.to_csv(csv_out, index=False)

#fill Missing Value
csv_out = pptDataDir+'rainfall.csv'
dat82=pd.read_csv(csv_out, parse_dates=[4], index_col='OBS DATE')    ### I fix some irregularity manually and save it into rainfall.csv

csvNoNA_out = pptDataDir+'rainfall_NoNA.csv'
df=dat82.iloc[:,[5,-1]].bfill()

#Find number of missing value for each month
#Extract rainfall during Dec 1998 to Dec 2017
dfWithNA = dat82.loc['1998-12':'2017-12']
dfNoNA = dfWithNA[dfWithNA.VALUE.notnull()]
avai = {'mon':range(1,13),'AllLen':[],'AvaLen':[],'Missing':[], 'PercentMissing':[]}
for m in range(1,13):
    mon_alllen = len(dfWithNA[dfWithNA.index.month==m])
    mon_avalen = len(dfNoNA[dfNoNA.index.month==m])
    mon_miss = mon_alllen-mon_avalen
    avai['AllLen'].append(mon_alllen)
    avai['AvaLen'].append(mon_avalen)
    avai['Missing'].append(mon_miss)
    avai['PercentMissing'].append(round(mon_miss/mon_alllen,2)*100)
csv_ava = pptDataDir+'monthly_data_availability.csv'
df_ava=pd.DataFrame(avai)
df_ava.to_csv(csv_ava, index=False)

#find incremental value
PPThrly=[0]
for i in range(len(df)-1):
    inc = df['VALUE'][i+1]-df['VALUE'][i]
    if inc<0:
        PPThrly.append(df['VALUE'][i+1])
    else:
        PPThrly.append(inc)
df['hrly_value']=PPThrly
df.to_csv(csvNoNA_out)

# Just in order to skip running the previouse lines
df = pd.read_csv(csvNoNA_out, parse_dates=['OBS DATE'], index_col='OBS DATE')
df = df.loc['1998-12':'2017-12']        
#Convert Hourly to daily Data
df_daily = pd.DataFrame(df['hrly_value'].resample('D', label='right').sum())
df_daily.columns = ['daily_value']
df_daily['UNITS'] = ['INCHES']*len(df_daily)
daily_csv = pptDataDir+'DailyRainfall.csv'
df_daily.to_csv(daily_csv)

df_daily=pd.read_csv(daily_csv, parse_dates=[0],index_col='OBS DATE')
#create boxplot of number of days between different rainfall ranges
NumDay = {'NumD':[], 'RainRange':[]}

for ij in range(1,7):
    df2=df_daily[(df_daily['daily_value']>=ij)&(df_daily['daily_value']<ij+1)]
    
    r=str(ij)+'-'+str(ij+1)
    NumDay['RainRange'].append(r)
    NumDay['NumD'].append(len(df2))
    
    out = pptDataDir+ 'RainBetween' + str(ij)+ 'and' + str(ij+1) + 'inch.csv'
    df2.to_csv(out)

NumDay_df = pd.DataFrame(NumDay)
NumDay_df['NumD'][2]=NumDay_df['NumD'][2]-1     #To manually remove 5/13/2005 events
stat_csv = pptDataDir+'NumOfDaySummary1.csv'
NumDay_df.to_csv(stat_csv)

plt.figure()
ax=sns.barplot(x='RainRange', y='NumD', data=NumDay, color='blue')
ax.set_ylabel("  Number of Rainy Days \nDec 1998 to Dec 2017", fontweight='bold')
ax.set_xlabel("Rainfall Range (in)", fontweight='bold')
ax.set_title("Montecito Rain Gage", fontweight='bold')
for p in ax.patches:
    ax.annotate(format(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 4), textcoords = 'offset points')
#plt.show()
out0 = PlotDir + 'Montecito_DailyHistogram.jpg'
plt.savefig(out0, dpi=1000)


#
# Create histogram for hourly data
#
NumHr = {'NumH':[], 'RainRange':[]}
c = 0 
for ij in np.arange(0,1.75,0.25):
    df3=df[(df['hrly_value']>ij)&(df['hrly_value']<=ij+0.25)]
    
    c = c+1
    r=str(ij)+'-'+str(ij+0.25)
    NumHr['RainRange'].append(r)
    NumHr['NumH'].append(len(df3))
    
    out2 = pptDataDir+ 'Hourly_RainBetween' + str(c) + 'quarter_inch.csv'
    df3.drop('VALUE', axis=1).to_csv(out2)

NumHr_df = pd.DataFrame(NumHr)
stat_csv2 = pptDataDir+'NumOfHourSummary.csv'
NumHr_df.to_csv(stat_csv2, index=False)

#histogram
plt.figure()
ax=sns.barplot(x='RainRange', y='NumH', data=NumHr, color='gray')
ax.set_ylabel("Number of Hours", fontweight='bold')
ax.set_xlabel("Rainfall Range (in)", fontweight='bold')
ax.set_title("Montecito Rain Gage", fontweight='bold')
for p in ax.patches:
    ax.annotate(format(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 3.5), textcoords = 'offset points')
#plt.show()
out0 = PlotDir + 'Montecito_hourlyHistogram.jpg'
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
        df3=df[(df['hrly_value']>IntRange[ij])&(df['hrly_value']<=IntRange[ij+1])]
    else:
        df3=df[(df['hrly_value']>IntRange[ij])]
        
    NumHr1['RainRange'].append(cat0[ij])
    NumHr1['NumH'].append(len(df3))
    
    out2 = pptDataDir+ 'Hourly_RainIn'+ cat1[ij]+ 'Range.csv'
    df3.drop('VALUE', axis=1).to_csv(out2)

NumHr_df1 = pd.DataFrame(NumHr1)
stat_csv2 = pptDataDir+'NumOfHourSummary_RainfallIntensityDef.csv'
NumHr_df1.to_csv(stat_csv2, index=False)

#histogram
plt.figure()
ax=sns.barplot(x='RainRange', y='NumH', data=NumHr1,palette=('green', 'yellow', 'red'))
#ax=plt.bar(NumHr1['RainRange'], NumHr1['NumH'])
#ax.text(1, NumHr1['NumH']+ .25, str(NumHr1['NumH']), color='black')
ax.set_ylabel("Number of Hours", fontweight='bold')
ax.set_xlabel("Rainfall Intensity (in/hr)", fontweight='bold')
ax.set_title("Montecito Rain Gage", fontweight='bold')
for p in ax.patches:
    ax.annotate(format(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 3.5), textcoords = 'offset points')
#plt.show()
out0 = PlotDir + 'Montecito_hourlyHistogram_RainfallIntensityDef.jpg'
plt.savefig(out0, dpi=1000)

