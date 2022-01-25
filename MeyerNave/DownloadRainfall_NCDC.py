# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 11:07:14 2020

@author: sardekani
"""
 """
 Processing NCDC precipitation daily summary data (USC00047902) for Santa Barbara Location
 Processing NCDC precipitation hourly data (COOP:047902) for Santa Barbara Location
 """
 import pandas as pd
 import numpy as np

Indir = 'P:/2020/Meyers Nave/NCDC/'
PlotDir="P:/2020/Meyers Nave/NCDC/plot/"
file_d = Indir + 'USC00047902.csv'
file_hr = Indir + '2322446.csv'
df_daily = pd.read_csv(file_d, parse_dates=[5], index_col=['DATE'])

# Check to see all the data are available and timeseries is continuous if not reindexing is required
beg = df_daily.index[0]
end = df_daily.index[-1]
ind = pd.date_range(start=beg, end=end, freq='D')
df_daily = df_daily.reindex(ind)
df_daily['PRCP'] = df_daily['PRCP'].fillna(0)


#create boxplot of number of days between different rainfall ranges
NumDay = {'NumD':[], 'RainRange':[]}

for ij in range(1,7):
    df2=df_daily[(df_daily['PRCP']>=ij)&(df_daily['PRCP']<ij+1)]
    
    r=str(ij)+'-'+str(ij+1)
    NumDay['RainRange'].append(r)
    NumDay['NumD'].append(len(df2))
    
    out = Indir+ 'NCDC_USC_RainBetween' + str(ij)+ 'and' + str(ij+1) + 'inch.csv'
    df2.to_csv(out)

NumDay_df = pd.DataFrame(NumDay)
stat_csv = Indir+'NCDC_USC_NumOfDaySummary.csv'
NumDay_df.to_csv(stat_csv)

plt.figure()
ax=sns.barplot(x='RainRange', y='NumD', data=NumDay, color='gray')
ax.set_ylabel("Number of Days", fontweight='bold')
ax.set_xlabel("Rainfall Range (in)", fontweight='bold')
ax.set_title("Santa Barbara Rain Gage", fontweight='bold')
for p in ax.patches:
    ax.annotate(format(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 4), textcoords = 'offset points')
#plt.show()
out0 = PlotDir + 'SantaBarbara_NCDC_USC_DailyHistogram.jpg'
plt.savefig(out0, dpi=1000)