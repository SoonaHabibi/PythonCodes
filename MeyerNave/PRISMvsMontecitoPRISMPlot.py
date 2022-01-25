# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:08:21 2020

@author: sardekani
"""
import pandas as pd
import sys
sys.path.append("//westfolsom/office/Python/WEST_Python_FunctionAug2019/")
import BasicFunction_py3 as BF   
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from datetime import timedelta

#
# upper watersheds PRISM rainfall versus PRISM rainfall at Monetico gauge location
#
PRISM_csv_d = '//westfolsom/Projects/2020/Meyers Nave/PRISM/ppt_Prism.csv'
df_PRISM = pd.read_csv(PRISM_csv_d, parse_dates=['Date'],index_col=0)

df_PRISM_1981 = df_PRISM['1981-12-02':'2018-01-01']
df_PRISM_gr3 = df_PRISM_1981.loc[(df_PRISM_1981.iloc[:,0]>3) | (df_PRISM_1981.iloc[:,1]>3) | (df_PRISM_1981.iloc[:,2]>3) | (df_PRISM_1981.iloc[:,3]>3)]

PRISM_csv_gr3 = '//westfolsom/Projects/2020/Meyers Nave/PRISM/raingreater3inchesAll4pixel.csv'    
df_PRISM_gr3.to_csv(PRISM_csv_gr3)

#
# Extract 3 day rainfall centered at event days
#
ind1 = df_PRISM_gr3.index 
dic_3day = {'Date':[],'PRISM-left':[],'PRISM-mid':[],'PRISM-right':[],'PRISM-Monte':[]} 
for i in ind1:
    beg = i-timedelta(days=1)
    end = i+timedelta(days=1)
    dic_3day['Date'].append(end)
    PRISM_3 = df_PRISM_1981.loc[beg:end].sum(axis = 0)
    dic_3day['PRISM-left'].append(PRISM_3[0])
    dic_3day['PRISM-mid'].append(PRISM_3[1])
    dic_3day['PRISM-right'].append(PRISM_3[2])
    dic_3day['PRISM-Monte'].append(PRISM_3[3])
    
df_all3d_orig = pd.DataFrame(dic_3day)
out_all3d_orig = '//westfolsom/Projects/2020/Meyers Nave/PRISM/3daysSumofPRISMeventgreater3inch_vsPRISMmont.csv'
df_all3d_orig.to_csv(out_all3d_orig, index=False)

# remove Consecetive Days
df_all3d = df_all3d_orig.drop([7,14,16,24,28,34,36,44])
out_all3d = '//westfolsom/Projects/2020/Meyers Nave/PRISM/3daysPRISMeventgr3inch_vsPRISMmont_rmConseDay.csv'
df_all3d.to_csv(out_all3d, index=False)
#
# Plot combine all colors_3days rainfall
#

fig, axs = plt.subplots(1, 3)
fig.set_figheight(15)
fig.set_figwidth(55)
matplotlib.rc('xtick', labelsize=25) 
matplotlib.rc('ytick', labelsize=25) 

axs[0].scatter(df_all3d.iloc[:,4], df_all3d.iloc[:,1], s=190)
axs[0].plot([0,16],[0,16],color='black')
axs[0].set_ylabel('Upper Montecito Watershed 3 Days Rainfall (in)',fontsize=26, fontweight='bold')
axs[0].set_xlabel('Lower Montecito Watershed 3 Days Rainfall (in)',fontsize=26, fontweight='bold')
axs[0].set_xlim([0,16])
axs[0].set_ylim([0,16])
# plt.xticks(fontsize=16)
# plt.yticks(fontsize=16)
x = df_all3d.iloc[:,4]
y = df_all3d.iloc[:,1]
m, b = np.polyfit(x, y, 1)
# axs[0, 0].plot(x, m*x + b)
r = round(np.corrcoef(x, y)[0,1],2)
axs[0].set_title('Upper Montecito Watershed\ncorrelation: ' + str(r) ,fontsize=32, fontweight='bold')


axs[1].scatter(df_all3d.iloc[:,4], df_all3d.iloc[:,2], s=190)
axs[1].plot([0,16],[0,16],color='black')
axs[1].set_ylabel('Upper San Ysidro Watershed 3 Days Rainfall (in)',fontsize=26, fontweight='bold')
axs[1].set_xlabel('Lower Montecito Watershed 3 Days Rainfall (in)',fontsize=26, fontweight='bold')
axs[1].set_xlim([0,16])
axs[1].set_ylim([0,16])
# plt.xticks(fontsize=16)
# plt.yticks(fontsize=16)
y =df_all3d.iloc[:,2]
m, b = np.polyfit(x, y, 1)
# axs[0, 1].plot(x, m*x + b)
r = round(np.corrcoef(x, y)[0,1],2)
axs[1].set_title('Upper San Ysidro Watershed\ncorrelation: ' + str(r) ,fontsize=32, fontweight='bold')


axs[2].scatter(df_all3d.iloc[:,4], df_all3d.iloc[:,3], s=190)
axs[2].plot([0,16],[0,16],color='black')
axs[2].set_ylabel('Upper Romero Watershed 3 Days Rainfall (in)',fontsize=26, fontweight='bold')
axs[2].set_xlabel('Lower Montecito Watershed 3 Days Rainfall (in)',fontsize=26, fontweight='bold')
axs[2].set_xlim([0,16])
axs[2].set_ylim([0,16])
# axs[2].set_xticklabels(xlabels,size = 16)
# axs[2].set_yticklabels(size = 14)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
y = df_all3d.iloc[:,3]
m, b = np.polyfit(x, y, 1)
# axs[1, 0].plot(x, m*x + b)
r = round(np.corrcoef(x, y)[0,1],2)
axs[2].set_title('Upper Romero Watershed\ncorrelation: ' + str(r) ,fontsize=32, fontweight='bold')

plt.show()
plt.close()




#
# Plot combine all colors_ 1 day rainfall for days with rainfall greater than 3 inch
#
df_1day = df_PRISM_1981.loc[ind1]

fig, axs = plt.subplots(1, 3)
fig.set_figheight(15)
fig.set_figwidth(55)
matplotlib.rc('xtick', labelsize=25) 
matplotlib.rc('ytick', labelsize=25) 

axs[0].scatter(df_1day.iloc[:,3], df_1day.iloc[:,0], s=190)
axs[0].plot([0,16],[0,16],color='black')
axs[0].set_ylabel('Upper Montecito Watershed 3 Days Rainfall (in)',fontsize=26, fontweight='bold')
axs[0].set_xlabel('Lower Montecito Watershed 3 Days Rainfall (in)',fontsize=26, fontweight='bold')
axs[0].set_xlim([0,9])
axs[0].set_ylim([0,9])
x = df_1day.iloc[:,3]
y = df_1day.iloc[:,0]
m, b = np.polyfit(x, y, 1)
# axs[0, 0].plot(x, m*x + b)
r = round(np.corrcoef(x, y)[0,1],2)
axs[0].set_title('Upper Montecito Watershed\ncorrelation: ' + str(r) ,fontsize=32, fontweight='bold')


axs[1].scatter(df_1day.iloc[:,3], df_1day.iloc[:,1], s=190)
axs[1].plot([0,16],[0,16],color='black')
axs[1].set_ylabel('Upper San Ysidro Watershed 3 Days Rainfall (in)',fontsize=26, fontweight='bold')
axs[1].set_xlabel('Lower Montecito Watershed 3 Days Rainfall (in)',fontsize=26, fontweight='bold')
axs[1].set_xlim([0,9])
axs[1].set_ylim([0,9])
y =df_1day.iloc[:,1]
m, b = np.polyfit(x, y, 1)
# axs[0, 1].plot(x, m*x + b)
r = round(np.corrcoef(x, y)[0,1],2)
axs[1].set_title('Upper San Ysidro Watershed\ncorrelation: ' + str(r) ,fontsize=32, fontweight='bold')


axs[2].scatter(df_1day.iloc[:,3], df_1day.iloc[:,2], s=190)
axs[2].plot([0,16],[0,16],color='black')
axs[2].set_ylabel('Upper Romero Watershed 3 Days Rainfall (in)',fontsize=26, fontweight='bold')
axs[2].set_xlabel('Lower Montecito Watershed 3 Days Rainfall (in)',fontsize=26, fontweight='bold')
axs[2].set_xlim([0,9])
axs[2].set_ylim([0,9])
y = df_1day.iloc[:,2]
m, b = np.polyfit(x, y, 1)
# axs[1, 0].plot(x, m*x + b)
r = round(np.corrcoef(x, y)[0,1],2)
axs[2].set_title('Upper Romero Watershed\ncorrelation: ' + str(r) ,fontsize=32, fontweight='bold')

plt.show()
