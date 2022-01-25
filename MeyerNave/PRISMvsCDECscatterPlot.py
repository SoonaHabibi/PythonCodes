# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 15:47:01 2020

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
from datetime import timedelta

#
# PRISM vs CDEC Scatter plot using data between '1998-12-01':'2018-01-01'
#
CDEC_csv_d = '//westfolsom/Projects/2020/Meyers Nave/CDEC/ChangeTimeZone/DailyRainfall.csv'
PRISM_csv_d = '//westfolsom/Projects/2020/Meyers Nave/PRISM/ppt_Prism.csv'
df_PRISM = pd.read_csv(PRISM_csv_d, parse_dates=['Date'],index_col=0)
df_CDEC = pd.read_csv(CDEC_csv_d, parse_dates=[0],index_col='OBS DATE')

df_PRISM_1998 = df_PRISM['1998-12-02':'2018-01-02']

# plot    
fig, axs = plt.subplots(2, 2)
fig.set_figheight(15)
fig.set_figwidth(15)
    

axs[0, 0].scatter(df_CDEC.iloc[:,0], df_PRISM_1998.iloc[:,0])
axs[0, 0].set_ylabel('Upper Montecito Watershed Daily Rainfall (in)')
axs[0, 0].set_xlabel('CDEC Daily Rainfall (in)')
x = df_CDEC.iloc[:,0]
y = df_PRISM_1998.iloc[:,0]
m, b = np.polyfit(x, y, 1)
axs[0, 0].plot(x, m*x + b, color='red')
r = round(np.corrcoef(x, y)[0,1],2)
axs[0, 0].set_title('correlation: ' + str(r))

axs[0, 1].scatter(df_CDEC.iloc[:,0], df_PRISM_1998.iloc[:,1])
axs[0, 1].set_ylabel('Upper San Ysidro Watershed Daily Rainfall (in)')
axs[0, 1].set_xlabel('CDEC Daily Rainfall (in)')
y = df_PRISM_1998.iloc[:,1]
m, b = np.polyfit(x, y, 1)
axs[0, 1].plot(x, m*x + b, color='red')
r = round(np.corrcoef(x, y)[0,1],2)
axs[0, 1].set_title('correlation: ' + str(r))

axs[1, 0].scatter(df_CDEC.iloc[:,0], df_PRISM_1998.iloc[:,2])
axs[1, 0].set_ylabel('Upper Romero Watershed Daily Rainfall (in)')
axs[1, 0].set_xlabel('CDEC Daily Rainfall (in)')
y = df_PRISM_1998.iloc[:,2]
m, b = np.polyfit(x, y, 1)
axs[1, 0].plot(x, m*x + b, color='red')
r = round(np.corrcoef(x, y)[0,1],2)
axs[1, 0].set_title('correlation: ' + str(r))

# plt.show()
# plt.tight_layout()
out0 = '//westfolsom/Projects/2020/Meyers Nave/PRISM/plot/PRISMAvsCDECscatter.jpg'
plt.savefig(out0)


#
# PRISM vs CDEC Scatter plot for days with greater than 3 inches of rainfall
#
CDEC_csv_3_7 = '//westfolsom/Projects/2020/Meyers Nave/CDEC/ChangeTimeZone/RainBetween3and7inch.csv'
df_CDEC_3_7 = pd.read_csv(CDEC_csv_3_7, parse_dates=[0],index_col='OBS DATE')
PRISM_csv_3_7 = '//westfolsom/Projects/2020/Meyers Nave/PRISM/raingreater3inches.csv'    
df_PRISM_3_7 = pd.read_csv(PRISM_csv_3_7, parse_dates=[0],index_col='Date')

# ind1 = df_CDEC_3_7.index
ind1 = df_PRISM_3_7.index 
dic_3day = {'Date':[],'PRISM-left':[],'PRISM-mid':[],'PRISM-right':[],'CDEC':[]} 
for i in ind1[25:]:
    beg = i-timedelta(days=1)
    end = i+timedelta(days=1)
    dic_3day['Date'].append(end)
    PRISM_3 = df_PRISM_1998.loc[beg:end].sum(axis = 0)
    dic_3day['PRISM-left'].append(PRISM_3[0])
    dic_3day['PRISM-mid'].append(PRISM_3[1])
    dic_3day['PRISM-right'].append(PRISM_3[2])
    CDEC_3 = df_CDEC.loc[beg:end, 'daily_value'].sum(axis = 0)
    dic_3day['CDEC'].append(CDEC_3)
    
df_all3d = pd.DataFrame(dic_3day)
out_all3d = '//westfolsom/Projects/2020/Meyers Nave/PRISM/3daysSumofPRISMeventgreater3inch.csv'
df_all3d.to_csv(out_all3d, index=False)

# days with rainfall greater than 3 inches at Montecito but not PRISM
ind = df_CDEC_3_7.index 
ind2 = ['2000-04-18', '2005-01-01', '2005-03-23', '2010-02-28','2015-12-16', '2017-01-21']
ind2 = ind[[0,7,10,14,16,17]]
dic_3day_2 = {'Date':[],'PRISM-left':[],'PRISM-mid':[],'PRISM-right':[],'CDEC':[]} 
for i in ind2:
    beg = i-timedelta(days=1)
    end = i+timedelta(days=1)
    dic_3day_2['Date'].append(end)
    PRISM_3 = df_PRISM_1998.loc[beg:end].sum(axis = 0)
    dic_3day_2['PRISM-left'].append(PRISM_3[0])
    dic_3day_2['PRISM-mid'].append(PRISM_3[1])
    dic_3day_2['PRISM-right'].append(PRISM_3[2])
    CDEC_3 = df_CDEC.loc[beg:end, 'daily_value'].sum(axis = 0)
    dic_3day_2['CDEC'].append(CDEC_3)
    
df_all3d_2 = pd.DataFrame(dic_3day_2)
out_all3d_2 = '//westfolsom/Projects/2020/Meyers Nave/PRISM/3daysSumofCDECeventgreater3inchNotPRISM.csv'
df_all3d_2.to_csv(out_all3d_2, index=False)

#
# Plot
#
fig, axs = plt.subplots(2, 2)
fig.set_figheight(15)
fig.set_figwidth(15)


axs[0, 0].scatter(df_all3d.iloc[:,4], df_all3d.iloc[:,1])
axs[0, 0].scatter(df_all3d_2.iloc[:,4], df_all3d_2.iloc[:,1], color='black')
axs[0, 0].set_ylabel('Upper Montecito Watershed 3 Days Rainfall (in)',fontsize=12, fontweight='bold')
axs[0, 0].set_xlabel('CDEC 3 Days Rainfall (in)',fontsize=12, fontweight='bold')
axs[0, 0].set_xlim([-.2,15])
axs[0, 0].set_ylim([-0.2,15])
x = df_all3d.iloc[:,4]
y = df_all3d.iloc[:,1]
m, b = np.polyfit(x, y, 1)
axs[0, 0].plot(x, m*x + b)
x2 = df_all3d_2.iloc[:,4]
y2 = df_all3d_2.iloc[:,1]
m2, b2 = np.polyfit(x2, y2, 1)
axs[0, 0].plot(x2, m2*x2 + b2, color='black')
r = round(np.corrcoef(x, y)[0,1],2)
r2 = round(np.corrcoef(x2, y2)[0,1],2)
axs[0, 0].set_title('correlation-blue: ' + str(r) + ' correlation-black: ' + str(r2),fontsize=12, fontweight='bold')


axs[0, 1].scatter(df_all3d.iloc[:,4], df_all3d.iloc[:,2])
axs[0, 1].scatter(df_all3d_2.iloc[:,4], df_all3d_2.iloc[:,2], color='black')
axs[0, 1].set_ylabel('Upper San Ysidro Watershed 3 Days Rainfall (in)',fontsize=12, fontweight='bold')
axs[0, 1].set_xlabel('CDEC 3 Days Rainfall (in)',fontsize=12, fontweight='bold')
axs[0, 1].set_xlim([-.2,15])
axs[0, 1].set_ylim([-.2,15])
y =df_all3d.iloc[:,2]
m, b = np.polyfit(x, y, 1)
axs[0, 1].plot(x, m*x + b)
y2 = df_all3d_2.iloc[:,2]
m2, b2 = np.polyfit(x2, y2, 1)
axs[0, 1].plot(x2, m2*x2 + b2, color='black')
r = round(np.corrcoef(x, y)[0,1],2)
r2 = round(np.corrcoef(x2, y2)[0,1],2)
axs[0, 1].set_title('correlation-blue: ' + str(r) + ' correlation-black: ' + str(r2),fontsize=12, fontweight='bold')


axs[1, 0].scatter(df_all3d.iloc[:,4], df_all3d.iloc[:,3])
axs[1, 0].scatter(df_all3d_2.iloc[:,4], df_all3d_2.iloc[:,3], color='black')
axs[1, 0].set_ylabel('Upper Romero Watershed 3 Days Rainfall (in)',fontsize=12, fontweight='bold')
axs[1, 0].set_xlabel('CDEC 3 Days Rainfall (in)',fontsize=12, fontweight='bold')
axs[1, 0].set_xlim([-0.2,15])
axs[1, 0].set_ylim([-0.2,15])
y = df_all3d.iloc[:,3]
m, b = np.polyfit(x, y, 1)
axs[1, 0].plot(x, m*x + b)
y2 = df_all3d_2.iloc[:,3]
m2, b2 = np.polyfit(x2, y2, 1)
axs[1, 0].plot(x2, m2*x2 + b2, color='black')
r = round(np.corrcoef(x, y)[0,1],2)
r2 = round(np.corrcoef(x2, y2)[0,1],2)
axs[1, 0].set_title('correlation-blue: ' + str(r) + ' correlation-black: ' + str(r2),fontsize=12, fontweight='bold')

plt.show()

#
# Plot combine all colors
#
df_all3 = pd.concat([df_all3d,df_all3d_2], axis=0)
fig, axs = plt.subplots(2, 2)
fig.set_figheight(15)
fig.set_figwidth(15)


axs[0, 0].scatter(df_all3.iloc[:,4], df_all3.iloc[:,1])
axs[0, 0].set_ylabel('Upper Montecito Watershed 3 Days Rainfall (in)',fontsize=12, fontweight='bold')
axs[0, 0].set_xlabel('CDEC 3 Days Rainfall (in)',fontsize=12, fontweight='bold')
axs[0, 0].set_xlim([-.2,15])
axs[0, 0].set_ylim([-0.2,15])
x = df_all3.iloc[:,4]
y = df_all3.iloc[:,1]
m, b = np.polyfit(x, y, 1)
axs[0, 0].plot(x, m*x + b)
r = round(np.corrcoef(x, y)[0,1],2)
axs[0, 0].set_title('correlation: ' + str(r) ,fontsize=12, fontweight='bold')


axs[0, 1].scatter(df_all3.iloc[:,4], df_all3.iloc[:,2])
axs[0, 1].set_ylabel('Upper San Ysidro Watershed 3 Days Rainfall (in)',fontsize=12, fontweight='bold')
axs[0, 1].set_xlabel('CDEC 3 Days Rainfall (in)',fontsize=12, fontweight='bold')
axs[0, 1].set_xlim([-.2,15])
axs[0, 1].set_ylim([-.2,15])
y =df_all3.iloc[:,2]
m, b = np.polyfit(x, y, 1)
axs[0, 1].plot(x, m*x + b)
r = round(np.corrcoef(x, y)[0,1],2)
axs[0, 1].set_title('correlation: ' + str(r),fontsize=12, fontweight='bold')


axs[1, 0].scatter(df_all3.iloc[:,4], df_all3.iloc[:,3])
axs[1, 0].set_ylabel('Upper Romero Watershed 3 Days Rainfall (in)',fontsize=12, fontweight='bold')
axs[1, 0].set_xlabel('CDEC 3 Days Rainfall (in)',fontsize=12, fontweight='bold')
axs[1, 0].set_xlim([-0.2,15])
axs[1, 0].set_ylim([-0.2,15])
y = df_all3.iloc[:,3]
m, b = np.polyfit(x, y, 1)
axs[1, 0].plot(x, m*x + b)
r = round(np.corrcoef(x, y)[0,1],2)
axs[1, 0].set_title('correlation-blue: ' + str(r) ,fontsize=12, fontweight='bold')

plt.show()
