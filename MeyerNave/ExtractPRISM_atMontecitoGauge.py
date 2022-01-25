# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 10:54:42 2020

@author: sardekani
"""

import pandas as pd
import numpy as np
from datetime import datetime 
from math import floor
import matplotlib.pyplot as plt
import seaborn as sns
import sys
sys.path.append("//westfolsom/Office/Python/WEST_Python_FunctionAug2019");
import BasicFunction_py3 as BF
from matplotlib.ticker import FormatStrFormatter

lonAr = np.array([-119.659,-119.626,-119.587,-119.648])
latAr = np.array([34.47, 34.47,34.47,34.42])
lonAr = np.array([-119.648])
latAr = np.array([34.42])

BegDate = datetime(1981,1,1)
EndDate = datetime(2020,3,26)I
Res = '4km'
Var = 'ppt'

datRange = pd.date_range(BegDate,EndDate, freq='D')
#yrAr = range(BegDate, EndDate, )
#mAr = range(1,13)
#mAr_lYr = range(1,EndDate.month+1)


#create disctionary w/ key for each month of each year
outfile = '//westfolsom/Projects/2020/Meyers Nave/PRISM/'+Var+'_Prism_AtSiteLocation.csv'
statfile = '//westfolsom/Projects/2020/Meyers Nave/PRISM/'+Var+'_stat_Prism_AtSiteLocation.csv'

pptdic={'PixelGageLoca':[]}

for dat in datRange:
    print(dat)
    dataset = BF.ReadPRISM(dat,Var,Res)
    #reading PRISM .bil file as raster
    rb = dataset.GetRasterBand(1)
    KeyMatrix = rb.ReadAsArray()
    ncol=dataset.RasterXSize 
    nrow=dataset.RasterYSize
    #Proj=dataset.GetProjection()               
    gt = dataset.GetGeoTransform()
    #yllcorner=gt[3]+nrow*gt[5]
    for i in range(len(latAr)):
        lat = latAr[i]
        lon = lonAr[i]
        #finding the col and row for the station
        col_start = int(floor((lon-gt[0])/gt[1]))           
        row_start = int(floor((lat-gt[3])/gt[5]))
        value = KeyMatrix[row_start,col_start]
        pptdic['PixelGageLoca'].append(value)
        
df = pd.DataFrame(pptdic, index=datRange)
df_in = df*0.03937
df_in.to_csv(outfile)
        
df_in = pd.read_csv(outfile, index_col=0)
pixel_pos = ['Left','Middle','Right']
PRISMfol = '//westfolsom/Projects/2020/Meyers Nave/PRISM/'
Plotfol = PRISMfol + 'plot/'
PlaAr = ['Left']*6+['Middle']*6+['Right']*6
NumDay = {'place':PlaAr, 'NumD':[], 'RainRange':[]}
for j, val in enumerate(pixel_pos):
    j_str = str(j)
    for ij in range(1,7):
        df=df_in[(df_in[j_str]>=ij)&(df_in[j_str]<ij+1)]
        
        r=str(ij)+'-'+str(ij+1)
        NumDay['RainRange'].append(r)
        NumDay['NumD'].append(len(df))

NumDay_df = pd.DataFrame(NumDay)

plt.figure()
ax=sns.barplot(x='RainRange', y='NumD', hue='place', data=NumDay)
ax.set_ylabel("Number of Day")
ax.set_xlabel("Rainfall Range (in)")
for p in ax.patches:
    ax.annotate(format(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 6), textcoords = 'offset points')
#plt.show()
out0 = PRISMfol + 'plot/bar.jpg'
plt.savefig(out0, dpi=1000)

out = PRISMfol + val + 'Pixel_RainBetween' + str(ij)+ 'and' + str(ij+1) + 'in.csv'
df.to_csv(out)



#
# Data from Jan 1981 to Dec 2017
#
outfile = '//westfolsom/Projects/2020/Meyers Nave/PRISM/ppt_Prism.csv'
df = pd.read_csv(outfile, parse_dates=['Date'],index_col=0)
df_1981_2017 = df['1981/1':'2017/12']

pixel_pos = ['Left','Middle','Right']
PRISMfol = '//westfolsom/Projects/2020/Meyers Nave/PRISM/'
Plotfol = PRISMfol + 'plot/'
PlaAr = ['Left']*6+['Middle']*6+['Right']*6
NumDay = {'place':PlaAr, 'NumD':[], 'RainRange':[]}
for j, val in enumerate(pixel_pos):
    j_str = str(j)
    for ij in range(1,7):
        df=df_1981_2017[(df_1981_2017[j_str]>=ij)&(df_1981_2017[j_str]<=ij+1)]
        
        r=str(ij)+'-'+str(ij+1)
        NumDay['RainRange'].append(r)
        NumDay['NumD'].append(len(df))
        
        out = PRISMfol + val + 'Pixel_RainBetween' + str(ij)+ 'and' + str(ij+1) + 'in_1981_2017_v2.csv'
        df.to_csv(out)

NumDay_df = pd.DataFrame(NumDay)

def change_width(ax, new_value) :
    for patch in ax.patches :
        current_width = patch.get_width()
        diff = current_width - new_value

        # we change the bar width
        patch.set_width(new_value)

        # we recenter the bar
        patch.set_x(patch.get_x() + diff * .5)

CreekAr = ['Upper Montecito Watershed']*6+['Upper San Ysidro Watershed']*6+['Upper Romero Watershed']*6
NumDay_df['Creek Name']=CreekAr
plt.figure()
ax=sns.barplot(x='RainRange', y='NumD', hue='Creek Name', data=NumDay_df)
ax.set_ylabel("  Number of Rainy Days \nJan 1981 to Dec 2017", fontweight='bold')
ax.set_xlabel("Rainfall Range (in)", fontweight='bold')
ax.set_title('PRISM Daily Data', fontweight='bold')
l = ax.legend()
l.set_title('')
#ax.set_yticklabels(ax.get_yticks(), size = 14, fontweight='bold')
#ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
# ax.xaxis.set_major_formatter(FormatStrFormatter('#%d'))
#ax.set_xticklabels(size = 14, fontweight='bold')
for p in ax.patches:
    ax.annotate(format(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 4.5), textcoords = 'offset points',fontsize=9)
change_width(ax, .26)
# plt.show()
plt.tight_layout()
out0 = PRISMfol + 'plot/PRISMA_bar_1981_2017.jpg'
plt.savefig(out0, dpi=1000)

# plt.figure(figsize=(20, 10))
# ax=sns.barplot(x='RainRange', y='NumD', hue='place', data=NumDay)
# ax.set_ylabel("  Number of Rainy Days \nJan 1981 to Dec 2017", fontweight='bold', fontsize=18)
# ax.set_xlabel("Rainfall Range (in)", fontweight='bold', fontsize=18)
# ax.set_title('PRISMA Daily Data', fontweight='bold',fontsize=18)
# plt.setp(ax.get_legend().get_texts(), fontsize=18)
# ax.set_yticklabels(ax.get_yticks(), size = 14, fontweight='bold')
# ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
# # ax.xaxis.set_major_formatter(FormatStrFormatter('#%d'))
# ax.set_xticklabels(size = 14, fontweight='bold')
# for p in ax.patches:
#     ax.annotate(format(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 6),fontsize=14, textcoords = 'offset points', fontweight='bold')
# change_width(ax, .26)
# plt.show()
# plt.tight_layout()
# out0 = PRISMfol + 'plot/PRISMA_bar_1981_2017.jpg'
# plt.savefig(out0, dpi=1000)




    

# PlaAr = ['Left']*7+['Middle']*7+['Right']*7
# NumDay = {'place':PlaAr, 'NumD':[], 'RainRange':[]}
# for j, val in enumerate(pixel_pos):
#     j_str = str(j)
#     for ij in range(0,7):
#         df=df_1981_2017[(df_1981_2017[j_str]>ij)&(df_1981_2017[j_str]<=ij+1)]
        
#         r=str(ij)+'-'+str(ij+1)
#         NumDay['RainRange'].append(r)
#         NumDay['NumD'].append(len(df))
#         out = PRISMfol + val + 'Pixel_RainBetween' + str(ij)+ 'and' + str(ij+1) + 'in_1981_2017_v2.csv'
#         df.to_csv(out)

# NumDay_df = pd.DataFrame(NumDay)
# out = PRISMfol + val + 'Pixel_Summary_in_1981_2017_v2.csv'
# NumDay_df.to_csv(out)

# Days with rainffall greater than 3 inch for at least one of the three pixels
outfile = '//westfolsom/Projects/2020/Meyers Nave/PRISM/ppt_Prism.csv'
df = pd.read_csv(outfile, parse_dates=['Date'],index_col=0)
df_1981_2017 = df['1981/1':'2017/12']

pixel_pos = ['Left','Middle','Right']
PRISMfol = '//westfolsom/Projects/2020/Meyers Nave/PRISM/raingreater3inches.csv'

df=df_1981_2017[(df_1981_2017[j_str]>=3)&(df_1981_2017[j_str]<=7)]
df1=df_1981_2017[(df_1981_2017['1']>=3)&(df_1981_2017['1']<=7)]
df2=df_1981_2017[(df_1981_2017['2']>=3)&(df_1981_2017['2']<=7)]

df_union=pd.concat([df,df1,df2])
df_union= df_union.drop_duplicates().sort_index()
df_union.to_csv(PRISMfol)



