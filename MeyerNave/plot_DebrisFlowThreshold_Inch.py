# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 10:50:45 2020

@author: sardekani
"""
import pandas as pd
import numpy as np
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
import sys 
sys.path.append("//westfolsom/Office/Python/WEST_Python_FunctionAug2019");
import BasicFunction_py3 as BF
import matplotlib.pyplot as plt
import math

indir = 'P:/2020/Meyers Nave/GIS/Raster/'
duration = [5, 10, 15, 30, 60]

RainRateAr = []
for i in range(len(duration)):
    TiffFile = indir + 'spas1721_' + str(duration[i]) +'min_mask_allWatershed.tif'
    dataset = gdal.Open(TiffFile, GA_ReadOnly) 
    rb = dataset.GetRasterBand(1)
    RainRate = rb.ReadAsArray()
    RainRate = RainRate.flatten()
    RainRate = RainRate[[RainRate>=0]]
    RainRate = RainRate *60/duration[i]  # convert tot rain to in/hr
    RainRateAr.append(RainRate)


DurationAr = np.repeat(duration, len(RainRateAr[0])) 
DurationAr = DurationAr/60    #min to hr
RainRateArFlat = np.concatenate( RainRateAr, axis=0 )

x = np.arange(0.06, 1.2, 0.05)
Conversion = 0.03937  
Units = 'in'
y_upper = 11.6*Conversion*x**(-0.7)
y_lower = 6.5*Conversion*x**(-0.7)

fig=plt.figure(1)
fig.set_figheight(8)
fig.set_figwidth(12)
plt.loglog(DurationAr, RainRateArFlat, '+', label = 'GARR pixel maximum rainfall intensity over the Montecito sub-watersheds'  ) #upstream from the inundated area
plt.loglog(x,y_upper, '--', label = 'Debris-flow threshold: I = 0.46 D$^{-0.7}$')
plt.loglog(x,y_lower, '--',  label = 'Lower-bound threshold: I = 0.26 D$^{-0.7}$')
plt.xlim([10**-1*0.6,10**0*1.1])
plt.ylim([0.09,4.25])
#plt.ylim([10**-1*0.6,10**0*1.1])
RainDuration = np.array([0.06, 1.1]) 
LightRain_hline = np.array([0.1,0.1])    
ModerateRain_hline = np.array([0.3,0.3])
plt.loglog(RainDuration,LightRain_hline, '-', color='lightgreen')
plt.loglog(RainDuration,ModerateRain_hline, '-', color='yellow')
plt.axhspan(0.0, 0.1, color='lightgreen', alpha=0.2)
plt.axhspan(0.1, 0.3, color='yellow', alpha=0.2)
plt.axhspan(0.3, 4.25, color='red', alpha=0.2)


plt.xlabel('Precipitation Duration (hr)', fontweight = 'bold', fontsize=12)
plt.ylabel('Rainfall Intensity (in/hr)', fontweight = 'bold', fontsize=12)

plt.text(duration[0]/60, 4.4, "5 min", ha='center', fontsize=11)
plt.text(duration[1]/60, 4.4, "10 min", ha='center', fontsize=11)
plt.text(duration[2]/60, 4.4, "15 min", ha='center', fontsize=11)
plt.text(duration[3]/60, 4.4, "30 min", ha='center', fontsize=11)
plt.text(duration[4]/60, 4.4, "60 min", ha='center', fontsize=11)

plt.text(duration[0]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[1]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[2]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[3]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[4]/60, 4.25,"-", rotation=90, ha='center')

plt.text(1.25, 3,"(in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=11)
plt.text(1.1, 0.1,"- 0.1", verticalalignment='center', fontsize=11)
plt.text(1.1, 0.2,"- 0.2", verticalalignment='center', fontsize=11)
plt.text(1.1, 0.3,"- 0.3", verticalalignment='center', fontsize=11)
plt.text(1.1, 0.4,"- 0.4", verticalalignment='center', fontsize=11)
plt.text(1.1, 0.5,"- 0.5", verticalalignment='center', fontsize=11)
plt.text(1.1, 0.6,"- 0.6", verticalalignment='center', fontsize=11)
plt.text(1.1, 0.7,"- 0.7", verticalalignment='center', fontsize=11)
plt.text(1.1, 0.8,"- 0.8", verticalalignment='center', fontsize=11)
plt.text(1.1, 0.9,"- 0.9 ", verticalalignment='center', fontsize=11)
plt.text(1.1,1,"- 1", verticalalignment='center', fontsize=11)
plt.text(1.1, 2,"- 2", verticalalignment='center', fontsize=11)
plt.text(1.1,3,"- 3", verticalalignment='center', fontsize=11)
plt.text(1.1,4,"- 4", verticalalignment='center', fontsize=11)

plt.text(0.77, 0.096,"Light Rain", verticalalignment='center', fontsize=11, color='darkgreen')
plt.text(0.77,0.109,"Moderate Rain", verticalalignment='center', fontsize=11, color='goldenrod')
plt.text(0.77,0.32,"Heavy Rain", verticalalignment='center', fontsize=11, color='darkred')

plt.legend(loc='lower left', fontsize=11.5)

#plt.show()
img_path = '‪P:/2020/Meyers Nave/GIS/Figure/DebrisThreshold_Keaton_in_per_hr.jpg'
plt.savefig(img_path.strip('\u202a'))  



