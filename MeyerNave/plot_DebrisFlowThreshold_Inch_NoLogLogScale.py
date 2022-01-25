# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 21:13:16 2020

@author: sardekani
"""

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
from scipy.interpolate import interp1d

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

###############################################################################
# final plot
###############################################################################
fig=plt.figure(1)
fig.set_figheight(7.5)
fig.set_figwidth(12)
plt.xlim([10**-1*0.6,10**0*1.1])
plt.ylim([0.00,4.25])
#plt.ylim([10**-1*0.6,10**0*1.1])
RainDuration = np.array([0.06, 1.1]) 
LightRain_hline = np.array([0.1,0.1])    
ModerateRain_hline = np.array([0.3,0.3])
plt.plot(RainDuration,LightRain_hline, '-', color='lightgreen')
plt.plot(RainDuration,ModerateRain_hline, '-', color='yellow')
plt.plot(DurationAr, RainRateArFlat, 'o', label = 'Maximum rainfall intensity', color='royalblue'  ) #upstream from the inundated area
plt.plot(x,y_upper, '--') #, label = 'Debris flow upper-bound threshold$^{1}$')  #: I = 0.46 D$^{-0.7}$
plt.plot(x,y_lower, '--') #, label = 'Debris flow lower-bound threshold$^{1}$')  #: I = 0.26 D$^{-0.7}$
plt.axhspan(0.0, 0.1, color='lightgreen', alpha=0.2)
plt.axhspan(0.1, 0.3, color='yellow', alpha=0.2)
plt.axhspan(0.3, 4.25, color='red', alpha=0.2)


plt.xlabel('Rainfall Duration (hr)', fontweight = 'bold', fontsize=12)
plt.ylabel('Rainfall Intensity (in/hr)', fontweight = 'bold', fontsize=12)

plt.text(duration[0]/60, 4.3, "5 min", ha='center', fontsize=11)
plt.text(duration[1]/60, 4.3, "10 min", ha='center', fontsize=11)
plt.text(duration[2]/60, 4.3, "15 min", ha='center', fontsize=11)
plt.text(duration[3]/60, 4.3, "30 min", ha='center', fontsize=11)
plt.text(duration[4]/60, 4.3, "60 min", ha='center', fontsize=11)

plt.text(duration[0]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[1]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[2]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[3]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[4]/60, 4.25,"-", rotation=90, ha='center')

plt.text(1.165, 1.29,"Rainfall Intensity (in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=12)
plt.text(1.1,0.0,"- 0.0", verticalalignment='center', fontsize=11)
plt.text(1.1,0.5,"- 0.5", verticalalignment='center', fontsize=11)
plt.text(1.1,1,"- 1.0", verticalalignment='center', fontsize=11)
plt.text(1.1,1.5,"- 1.5", verticalalignment='center', fontsize=11)
plt.text(1.1, 2,"- 2.0", verticalalignment='center', fontsize=11)
plt.text(1.1,2.5,"- 2.5", verticalalignment='center', fontsize=11)
plt.text(1.1,3,"- 3.0", verticalalignment='center', fontsize=11)
plt.text(1.1,3.5,"- 3.5", verticalalignment='center', fontsize=11)
plt.text(1.1,4,"- 4.0", verticalalignment='center', fontsize=11)

plt.text(0.77, 0.056,"Light Rain", verticalalignment='center', fontsize=11, color='darkgreen')
plt.text(0.77,0.2,"Moderate Rain", verticalalignment='center', fontsize=11, color='goldenrod')
plt.text(0.77,0.4,"Heavy Rain", verticalalignment='center', fontsize=11, color='darkred')

plt.legend(loc='upper right', fontsize=11.5)    #, bbox_to_anchor=(-0.02,-.34)
#plt.tight_layout()
#plt.show()
img_path = '‪P:/2020/Meyers Nave/GIS/Figure/DebrisThreshold_Keaton_in_per_hr_noScale.jpg'
plt.savefig(img_path.strip('\u202a'))    


###############################################################################
# Template
###############################################################################
fig=plt.figure(1)
fig.set_figheight(7.5)
fig.set_figwidth(12)
plt.xlim([10**-1*0.6,10**0*1.1])
plt.ylim([0.00,4.25])
#plt.ylim([10**-1*0.6,10**0*1.1])
RainDuration = np.array([0.06, 1.1]) 
LightRain_hline = np.array([0.1,0.1])    
ModerateRain_hline = np.array([0.3,0.3])
plt.plot(RainDuration,LightRain_hline, '-', color='lightgreen')
plt.plot(RainDuration,ModerateRain_hline, '-', color='yellow')
plt.axhspan(0.0, 0.1, color='lightgreen', alpha=0.2)
plt.axhspan(0.1, 0.3, color='yellow', alpha=0.2)
plt.axhspan(0.3, 4.25, color='red', alpha=0.2)


plt.xlabel('Rainfall Duration (hr)', fontweight = 'bold', fontsize=12)
plt.ylabel('Rainfall Intensity (in/hr)', fontweight = 'bold', fontsize=12)

plt.text(duration[0]/60, 4.3, "5 min", ha='center', fontsize=11)
plt.text(duration[1]/60, 4.3, "10 min", ha='center', fontsize=11)
plt.text(duration[2]/60, 4.3, "15 min", ha='center', fontsize=11)
plt.text(duration[3]/60, 4.3, "30 min", ha='center', fontsize=11)
plt.text(duration[4]/60, 4.3, "60 min", ha='center', fontsize=11)

plt.text(duration[0]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[1]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[2]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[3]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[4]/60, 4.25,"-", rotation=90, ha='center')

#plt.text(1.15, 3,"(in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=11)
plt.text(1.165, 1.29,"Rainfall Intensity (in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=12)
plt.text(1.1,0.0,"- 0.0", verticalalignment='center', fontsize=11)
plt.text(1.1,0.5,"- 0.5", verticalalignment='center', fontsize=11)
plt.text(1.1,1,"- 1.0", verticalalignment='center', fontsize=11)
plt.text(1.1,1.5,"- 1.5", verticalalignment='center', fontsize=11)
plt.text(1.1, 2,"- 2.0", verticalalignment='center', fontsize=11)
plt.text(1.1,2.5,"- 2.5", verticalalignment='center', fontsize=11)
plt.text(1.1,3,"- 3.0", verticalalignment='center', fontsize=11)
plt.text(1.1,3.5,"- 3.5", verticalalignment='center', fontsize=11)
plt.text(1.1,4,"- 4.0", verticalalignment='center', fontsize=11)

plt.text(0.77, 0.056,"Light Rain", verticalalignment='center', fontsize=11, color='darkgreen')
plt.text(0.77,0.2,"Moderate Rain", verticalalignment='center', fontsize=11, color='goldenrod')
plt.text(0.77,0.4,"Heavy Rain", verticalalignment='center', fontsize=11, color='darkred')
#plt.legend(loc='upper right', fontsize=11.5)
#plt.tight_layout()
img_path = '‪P:/2020/Meyers Nave/GIS/Figure/DebrisThreshold_Template.jpg'
plt.savefig(img_path.strip('\u202a'))  


###############################################################################
# Template & both Thresholds
###############################################################################
fig=plt.figure(1)
fig.set_figheight(7.5)
fig.set_figwidth(12)
plt.xlim([10**-1*0.6,10**0*1.1])
plt.ylim([0.00,4.25])
#plt.ylim([10**-1*0.6,10**0*1.1])
RainDuration = np.array([0.06, 1.1]) 
LightRain_hline = np.array([0.1,0.1])    
ModerateRain_hline = np.array([0.3,0.3])
plt.plot(RainDuration,LightRain_hline, '-', color='lightgreen')
plt.plot(RainDuration,ModerateRain_hline, '-', color='yellow')
plt.plot(x,y_upper, '--') #, label = 'Debris flow upper-bound threshold$^{1}$')  #: I = 0.46 D$^{-0.7}$
plt.plot(x,y_lower, '--')
plt.axhspan(0.0, 0.1, color='lightgreen', alpha=0.2)
plt.axhspan(0.1, 0.3, color='yellow', alpha=0.2)
plt.axhspan(0.3, 4.25, color='red', alpha=0.2)


plt.xlabel('Rainfall Duration (hr)', fontweight = 'bold', fontsize=12)
plt.ylabel('Rainfall Intensity (in/hr)', fontweight = 'bold', fontsize=12)

plt.text(duration[0]/60, 4.3, "5 min", ha='center', fontsize=11)
plt.text(duration[1]/60, 4.3, "10 min", ha='center', fontsize=11)
plt.text(duration[2]/60, 4.3, "15 min", ha='center', fontsize=11)
plt.text(duration[3]/60, 4.3, "30 min", ha='center', fontsize=11)
plt.text(duration[4]/60, 4.3, "60 min", ha='center', fontsize=11)

plt.text(duration[0]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[1]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[2]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[3]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[4]/60, 4.25,"-", rotation=90, ha='center')

#plt.text(1.15, 3,"(in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=11)
plt.text(1.165, 1.29,"Rainfall Intensity (in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=12)
plt.text(1.1,0.0,"- 0.0", verticalalignment='center', fontsize=11)
plt.text(1.1,0.5,"- 0.5", verticalalignment='center', fontsize=11)
plt.text(1.1,1,"- 1.0", verticalalignment='center', fontsize=11)
plt.text(1.1,1.5,"- 1.5", verticalalignment='center', fontsize=11)
plt.text(1.1, 2,"- 2.0", verticalalignment='center', fontsize=11)
plt.text(1.1,2.5,"- 2.5", verticalalignment='center', fontsize=11)
plt.text(1.1,3,"- 3.0", verticalalignment='center', fontsize=11)
plt.text(1.1,3.5,"- 3.5", verticalalignment='center', fontsize=11)
plt.text(1.1,4,"- 4.0", verticalalignment='center', fontsize=11)

plt.text(0.77, 0.056,"Light Rain", verticalalignment='center', fontsize=11, color='darkgreen')
plt.text(0.77,0.2,"Moderate Rain", verticalalignment='center', fontsize=11, color='goldenrod')
plt.text(0.77,0.4,"Heavy Rain", verticalalignment='center', fontsize=11, color='darkred')
#plt.legend(loc='upper right', fontsize=11.5)
#plt.tight_layout()
img_path = '‪P:/2020/Meyers Nave/GIS/Figure/DebrisThreshold_Template_withThresholds.jpg'
plt.savefig(img_path.strip('\u202a'))  


###############################################################################
# Template + 5min data
###############################################################################
fig=plt.figure(1)
fig.set_figheight(7.5)
fig.set_figwidth(12)
plt.xlim([10**-1*0.6,10**0*1.1])
plt.ylim([0.00,4.25])
#plt.ylim([10**-1*0.6,10**0*1.1])
RainDuration = np.array([0.06, 1.1]) 
LightRain_hline = np.array([0.1,0.1])    
ModerateRain_hline = np.array([0.3,0.3])
plt.plot(RainDuration,LightRain_hline, '-', color='lightgreen')
plt.plot(RainDuration,ModerateRain_hline, '-', color='yellow')
plt.plot(DurationAr[0:46], RainRateArFlat[0:46], 'o', label = 'Maximum 5-minute rainfall intensity', color='royalblue'  ) #upstream from the inundated area
plt.axhspan(0.0, 0.1, color='lightgreen', alpha=0.2)
plt.axhspan(0.1, 0.3, color='yellow', alpha=0.2)
plt.axhspan(0.3, 4.25, color='red', alpha=0.2)


plt.xlabel('Rainfall Duration (hr)', fontweight = 'bold', fontsize=12)
plt.ylabel('Rainfall Intensity (in/hr)', fontweight = 'bold', fontsize=12)

plt.text(duration[0]/60, 4.3, "5 min", ha='center', fontsize=11)
plt.text(duration[1]/60, 4.3, "10 min", ha='center', fontsize=11)
plt.text(duration[2]/60, 4.3, "15 min", ha='center', fontsize=11)
plt.text(duration[3]/60, 4.3, "30 min", ha='center', fontsize=11)
plt.text(duration[4]/60, 4.3, "60 min", ha='center', fontsize=11)

plt.text(duration[0]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[1]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[2]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[3]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[4]/60, 4.25,"-", rotation=90, ha='center')

#plt.text(1.15, 3,"(in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=11)
plt.text(1.165, 1.29,"Rainfall Intensity (in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=12)
plt.text(1.1,0.0,"- 0.0", verticalalignment='center', fontsize=11)
plt.text(1.1,0.5,"- 0.5", verticalalignment='center', fontsize=11)
plt.text(1.1,1,"- 1.0", verticalalignment='center', fontsize=11)
plt.text(1.1,1.5,"- 1.5", verticalalignment='center', fontsize=11)
plt.text(1.1, 2,"- 2.0", verticalalignment='center', fontsize=11)
plt.text(1.1,2.5,"- 2.5", verticalalignment='center', fontsize=11)
plt.text(1.1,3,"- 3.0", verticalalignment='center', fontsize=11)
plt.text(1.1,3.5,"- 3.5", verticalalignment='center', fontsize=11)
plt.text(1.1,4,"- 4.0", verticalalignment='center', fontsize=11)

plt.text(0.77, 0.056,"Light Rain", verticalalignment='center', fontsize=11, color='darkgreen')
plt.text(0.77,0.2,"Moderate Rain", verticalalignment='center', fontsize=11, color='goldenrod')
plt.text(0.77,0.4,"Heavy Rain", verticalalignment='center', fontsize=11, color='darkred')

#plt.legend(loc='lower left', bbox_to_anchor=(-0.02,-.2), fontsize=11.5)
plt.legend(loc='upper right', fontsize=11.5)
#plt.tight_layout()
img_path = '‪P:/2020/Meyers Nave/GIS/Figure/DebrisThreshold_Template_5minMaxdata.jpg'
plt.savefig(img_path.strip('\u202a'))  

###############################################################################
# Template + all data no threshold
###############################################################################
fig=plt.figure(1)
fig.set_figheight(7.5)
fig.set_figwidth(12)
plt.xlim([10**-1*0.6,10**0*1.1])
plt.ylim([0.00,4.25])
#plt.ylim([10**-1*0.6,10**0*1.1])
RainDuration = np.array([0.06, 1.1]) 
LightRain_hline = np.array([0.1,0.1])    
ModerateRain_hline = np.array([0.3,0.3])
plt.plot(RainDuration,LightRain_hline, '-', color='lightgreen')
plt.plot(RainDuration,ModerateRain_hline, '-', color='yellow')
plt.plot(DurationAr, RainRateArFlat, 'o', label = 'Maximum rainfall intensity', color='royalblue'  ) #upstream from the inundated area
plt.axhspan(0.0, 0.1, color='lightgreen', alpha=0.2)
plt.axhspan(0.1, 0.3, color='yellow', alpha=0.2)
plt.axhspan(0.3, 4.25, color='red', alpha=0.2)


plt.xlabel('Rainfall Duration (hr)', fontweight = 'bold', fontsize=12)
plt.ylabel('Rainfall Intensity (in/hr)', fontweight = 'bold', fontsize=12)

plt.text(duration[0]/60, 4.3, "5 min", ha='center', fontsize=11)
plt.text(duration[1]/60, 4.3, "10 min", ha='center', fontsize=11)
plt.text(duration[2]/60, 4.3, "15 min", ha='center', fontsize=11)
plt.text(duration[3]/60, 4.3, "30 min", ha='center', fontsize=11)
plt.text(duration[4]/60, 4.3, "60 min", ha='center', fontsize=11)

plt.text(duration[0]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[1]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[2]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[3]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[4]/60, 4.25,"-", rotation=90, ha='center')

#plt.text(1.15, 3,"(in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=11)
plt.text(1.165, 1.29,"Rainfall Intensity (in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=12)
plt.text(1.1,0.0,"- 0.0", verticalalignment='center', fontsize=11)
plt.text(1.1,0.5,"- 0.5", verticalalignment='center', fontsize=11)
plt.text(1.1,1,"- 1.0", verticalalignment='center', fontsize=11)
plt.text(1.1,1.5,"- 1.5", verticalalignment='center', fontsize=11)
plt.text(1.1, 2,"- 2.0", verticalalignment='center', fontsize=11)
plt.text(1.1,2.5,"- 2.5", verticalalignment='center', fontsize=11)
plt.text(1.1,3,"- 3.0", verticalalignment='center', fontsize=11)
plt.text(1.1,3.5,"- 3.5", verticalalignment='center', fontsize=11)
plt.text(1.1,4,"- 4.0", verticalalignment='center', fontsize=11)

plt.text(0.77, 0.056,"Light Rain", verticalalignment='center', fontsize=11, color='darkgreen')
plt.text(0.77,0.2,"Moderate Rain", verticalalignment='center', fontsize=11, color='goldenrod')
plt.text(0.77,0.4,"Heavy Rain", verticalalignment='center', fontsize=11, color='darkred')

#plt.legend(loc='lower left', bbox_to_anchor=(-0.02,-.2), fontsize=11.5)
plt.legend(loc='upper right', fontsize=11.5)
#plt.tight_layout()
img_path = '‪P:/2020/Meyers Nave/GIS/Figure/DebrisThreshold_Template_allMaxdata.jpg'
plt.savefig(img_path.strip('\u202a'))  


###############################################################################
# Template + all data no threshold+Upper Threshold
###############################################################################
fig=plt.figure(1)
fig.set_figheight(7.5)
fig.set_figwidth(12)
plt.xlim([10**-1*0.6,10**0*1.1])
plt.ylim([0.00,4.25])
#plt.ylim([10**-1*0.6,10**0*1.1])
RainDuration = np.array([0.06, 1.1]) 
LightRain_hline = np.array([0.1,0.1])    
ModerateRain_hline = np.array([0.3,0.3])
plt.plot(RainDuration,LightRain_hline, '-', color='lightgreen')
plt.plot(RainDuration,ModerateRain_hline, '-', color='yellow')
plt.plot(DurationAr, RainRateArFlat, 'o', label = 'Maximum rainfall intensity', color='royalblue'  ) #upstream from the inundated area
plt.plot(x,y_upper, '--')#, label = 'Debris flow upper bound threshold$^{1}$')  #: I = 0.46 D$^{-0.7}$
#plt.plot(x,y_lower, '--',  label = 'Lower-bound threshold')  #: I = 0.26 D$^{-0.7}$
plt.axhspan(0.0, 0.1, color='lightgreen', alpha=0.2)
plt.axhspan(0.1, 0.3, color='yellow', alpha=0.2)
plt.axhspan(0.3, 4.25, color='red', alpha=0.2)


plt.xlabel('Rainfall Duration (hr)', fontweight = 'bold', fontsize=12)
plt.ylabel('Rainfall Intensity (in/hr)', fontweight = 'bold', fontsize=12)

plt.text(duration[0]/60, 4.3, "5 min", ha='center', fontsize=11)
plt.text(duration[1]/60, 4.3, "10 min", ha='center', fontsize=11)
plt.text(duration[2]/60, 4.3, "15 min", ha='center', fontsize=11)
plt.text(duration[3]/60, 4.3, "30 min", ha='center', fontsize=11)
plt.text(duration[4]/60, 4.3, "60 min", ha='center', fontsize=11)

plt.text(duration[0]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[1]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[2]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[3]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[4]/60, 4.25,"-", rotation=90, ha='center')

#plt.text(1.15, 3,"(in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=11)
plt.text(1.165, 1.29,"Rainfall Intensity (in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=12)
plt.text(1.1,0.0,"- 0.0", verticalalignment='center', fontsize=11)
plt.text(1.1,0.5,"- 0.5", verticalalignment='center', fontsize=11)
plt.text(1.1,1,"- 1.0", verticalalignment='center', fontsize=11)
plt.text(1.1,1.5,"- 1.5", verticalalignment='center', fontsize=11)
plt.text(1.1, 2,"- 2.0", verticalalignment='center', fontsize=11)
plt.text(1.1,2.5,"- 2.5", verticalalignment='center', fontsize=11)
plt.text(1.1,3,"- 3.0", verticalalignment='center', fontsize=11)
plt.text(1.1,3.5,"- 3.5", verticalalignment='center', fontsize=11)
plt.text(1.1,4,"- 4.0", verticalalignment='center', fontsize=11)

plt.text(0.77, 0.056,"Light Rain", verticalalignment='center', fontsize=11, color='darkgreen')
plt.text(0.77,0.2,"Moderate Rain", verticalalignment='center', fontsize=11, color='goldenrod')
plt.text(0.77,0.4,"Heavy Rain", verticalalignment='center', fontsize=11, color='darkred')
plt.legend(loc='upper right', fontsize=11.5)
#plt.show()

#plt.tight_layout()
#plt.show()
img_path = '‪P:/2020/Meyers Nave/GIS/Figure/DebrisThreshold_Template_allMaxdata_upper.jpg'
plt.savefig(img_path.strip('\u202a'))  







##############################################################################
# final plot + NOAA atlas return Period, lower part of Montecito, for lat: 34.427 lon: -119.64
##############################################################################
RP2in = np.array([0.199,0.285,0.345,0.536,0.803,1.18])
RP5in = np.array([0.253, 0.363,0.439, 0.681,1.02,1.5])
RP10in = np.array([0.296, 0.425, 0.514, 0.798, 1.2,1.75])
RP25in = np.array([0.354, 0.508, 0.614, 0.954, 1.43,2.09])
RP50in = np.array([0.398, 0.57, 0.69, 1.07, 1.61, 2.34])
RP100in = np.array([0.442, 0.633, 0.766, 1.19, 1.78,2.59])

inCONinPhr = np.array([12,6,4,2,1,0.5])
durationHr = np.array([5/60, 10/60, 15/60, 30/60, 60/60,120/60])

RP2inPhr = RP2in*inCONinPhr
RP5inPhr = RP5in*inCONinPhr
RP10inPhr = RP10in*inCONinPhr
RP25inPhr = RP25in*inCONinPhr
RP50inPhr = RP50in*inCONinPhr
RP100inPhr = RP100in*inCONinPhr

durationHr_new = np.linspace(durationHr.min(), durationHr.max(),500)

f2 = interp1d(durationHr, RP2inPhr, kind='quadratic')
RP2inPhr_smooth=f2(durationHr_new)


fig=plt.figure(1)
fig.set_figheight(7.5)
fig.set_figwidth(12)
plt.xlim([10**-1*0.6,10**0*1.1])
plt.ylim([0.00,4.25])
#plt.ylim([10**-1*0.6,10**0*1.1])
RainDuration = np.array([0.06, 1.1]) 
LightRain_hline = np.array([0.1,0.1])    
ModerateRain_hline = np.array([0.3,0.3])
plt.plot(RainDuration,LightRain_hline, '-', color='lightgreen')
plt.plot(RainDuration,ModerateRain_hline, '-', color='yellow')
plt.plot(DurationAr, RainRateArFlat, 'o', label = 'Maximum rainfall intensity', color='royalblue'  ) #upstream from the inundated area
plt.plot(x,y_upper, '--', label = 'Debris flow upper-bound threshold$^{1}$')  #: I = 0.46 D$^{-0.7}$
plt.plot(x,y_lower, '--',  label = 'Debris flow lower-bound threshold$^{1}$')  #: I = 0.26 D$^{-0.7}$
plt.plot(durationHr,RP2inPhr, linestyle='--', marker='o', color='gray', markerfacecolor='yellow',  label = '2 year return period$^{2}$') 
plt.plot(durationHr,RP5inPhr,linestyle='--', marker='o', color='gray', markerfacecolor='greenyellow', label = '5 year return period$^{2}$') 
plt.plot(durationHr,RP10inPhr,linestyle='--', marker='o', color='gray', markerfacecolor='yellowgreen',  label = '10 year return period$^{2}$') 
plt.plot(durationHr,RP25inPhr,linestyle='--', marker='o', color='gray', markerfacecolor='peachpuff',  label = '25 year return period$^{2}$') 
plt.plot(durationHr,RP50inPhr, linestyle='--', marker='o', color='gray', markerfacecolor='lightsalmon',  label = '50 year return period$^{2}$') 
plt.plot(durationHr,RP100inPhr, linestyle='--', marker='o', color='gray', markerfacecolor='tomato',  label = '100 year return period$^{2}$') 
plt.axhspan(0.0, 0.1, color='lightgreen', alpha=0.2)
plt.axhspan(0.1, 0.3, color='yellow', alpha=0.2)
plt.axhspan(0.3, 4.25, color='red', alpha=0.2)


plt.xlabel('Rainfall Duration (hr)', fontweight = 'bold', fontsize=12)
plt.ylabel('Rainfall Intensity (in/hr)', fontweight = 'bold', fontsize=12)

plt.text(duration[0]/60, 4.3, "5 min", ha='center', fontsize=11)
plt.text(duration[1]/60, 4.3, "10 min", ha='center', fontsize=11)
plt.text(duration[2]/60, 4.3, "15 min", ha='center', fontsize=11)
plt.text(duration[3]/60, 4.3, "30 min", ha='center', fontsize=11)
plt.text(duration[4]/60, 4.3, "60 min", ha='center', fontsize=11)

plt.text(duration[0]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[1]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[2]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[3]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[4]/60, 4.25,"-", rotation=90, ha='center')

plt.text(1.165, 1.29,"Rainfall Intensity (in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=12)
plt.text(1.1,0.0,"- 0.0", verticalalignment='center', fontsize=11)
plt.text(1.1,0.5,"- 0.5", verticalalignment='center', fontsize=11)
plt.text(1.1,1,"- 1.0", verticalalignment='center', fontsize=11)
plt.text(1.1,1.5,"- 1.5", verticalalignment='center', fontsize=11)
plt.text(1.1, 2,"- 2.0", verticalalignment='center', fontsize=11)
plt.text(1.1,2.5,"- 2.5", verticalalignment='center', fontsize=11)
plt.text(1.1,3,"- 3.0", verticalalignment='center', fontsize=11)
plt.text(1.1,3.5,"- 3.5", verticalalignment='center', fontsize=11)
plt.text(1.1,4,"- 4.0", verticalalignment='center', fontsize=11)

plt.text(0.77, 0.056,"Light Rain", verticalalignment='center', fontsize=11, color='darkgreen')
plt.text(0.77,0.2,"Moderate Rain", verticalalignment='center', fontsize=11, color='goldenrod')
plt.text(0.77,0.4,"Heavy Rain", verticalalignment='center', fontsize=11, color='darkred')

plt.legend(loc='upper right', fontsize=10.5)    #, bbox_to_anchor=(-0.02,-.34)
#plt.tight_layout()
#plt.show()
img_path = '‪P:/2020/Meyers Nave/GIS/Figure/DebrisThreshold_all_returnPeriod_lowerpart.jpg'
plt.savefig(img_path.strip('\u202a'))    



##############################################################################
# final plot + NOAA atlas return Period, Upper part of Montecito, lat:34:4897 lon:-119.6653
##############################################################################
RP2in = np.array([0.266,0.381,0.461,0.687,1.09, 1.68])
RP5in = np.array([0.340, 0.487,0.589, 0.88,1.4, 2.14])
RP10in = np.array([0.399, 0.572, 0.692, 1.03, 1.64,2.49])
RP25in = np.array([0.477, 0.684, 0.827, 1.24, 1.96, 2.96])
RP50in = np.array([0.536, 0.768, 0.929, 1.39, 2.2, 3.3])
RP100in = np.array([0.594, 0.851, 1.03, 1.54, 2.44, 3.64])

inCONinPhr = np.array([12,6,4,2,1,0.5])
durationHr = np.array([5/60, 10/60, 15/60, 30/60, 60/60, 120/60])

RP2inPhr = RP2in*inCONinPhr
RP5inPhr = RP5in*inCONinPhr
RP10inPhr = RP10in*inCONinPhr
RP25inPhr = RP25in*inCONinPhr
RP50inPhr = RP50in*inCONinPhr
RP100inPhr = RP100in*inCONinPhr

durationHr_new = np.linspace(durationHr.min(), durationHr.max(),500)

f2 = interp1d(durationHr, RP2inPhr, kind='quadratic')
RP2inPhr_smooth=f2(durationHr_new)

f10 = interp1d(durationHr, RP10inPhr, kind='quadratic')
RP10inPhr_smooth=f10(durationHr_new)

f100 = interp1d(durationHr, RP100inPhr, kind='quadratic')
RP100inPhr_smooth=f100(durationHr_new)


fig=plt.figure(1)
fig.set_figheight(7.5)
fig.set_figwidth(12)
plt.xlim([10**-1*0.6,10**0*1.1])
plt.ylim([0.00,4.25])
#plt.ylim([10**-1*0.6,10**0*1.1])
RainDuration = np.array([0.06, 1.1]) 
LightRain_hline = np.array([0.1,0.1])    
ModerateRain_hline = np.array([0.3,0.3])
plt.plot(RainDuration,LightRain_hline, '-', color='lightgreen')
plt.plot(RainDuration,ModerateRain_hline, '-', color='yellow')
plt.plot(DurationAr, RainRateArFlat, 'o', label = 'Maximum rainfall intensity', color='royalblue'  ) #upstream from the inundated area
plt.plot(x,y_upper, '--') #, label = 'Debris flow upper-bound threshold$^{1}$')  #: I = 0.46 D$^{-0.7}$
plt.plot(x,y_lower, '--') #,  label = 'Debris flow lower-bound threshold$^{1}$')  #: I = 0.26 D$^{-0.7}$
plt.plot(durationHr_new,RP2inPhr_smooth, '-', color='black',  label = 'Return period$^{*}$')  
plt.plot(durationHr_new,RP10inPhr_smooth,'-', color='black') 
plt.plot(durationHr_new,RP100inPhr_smooth, '-', color='black') 
plt.axhspan(0.0, 0.1, color='lightgreen', alpha=0.2)
plt.axhspan(0.1, 0.3, color='yellow', alpha=0.2)
plt.axhspan(0.3, 4.25, color='red', alpha=0.2)


plt.xlabel('Rainfall Duration (hr)', fontweight = 'bold', fontsize=12)
plt.ylabel('Rainfall Intensity (in/hr)', fontweight = 'bold', fontsize=12)

plt.text(duration[0]/60, 4.3, "5 min", ha='center', fontsize=11)
plt.text(duration[1]/60, 4.3, "10 min", ha='center', fontsize=11)
plt.text(duration[2]/60, 4.3, "15 min", ha='center', fontsize=11)
plt.text(duration[3]/60, 4.3, "30 min", ha='center', fontsize=11)
plt.text(duration[4]/60, 4.3, "60 min", ha='center', fontsize=11)

plt.text(duration[0]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[1]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[2]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[3]/60, 4.25,"-", rotation=90, ha='center')
plt.text(duration[4]/60, 4.25,"-", rotation=90, ha='center')

plt.text(1.165, 1.29,"Rainfall Intensity (in/hr)", rotation=90, ha='center', fontweight = 'bold', fontsize=12)
plt.text(1.1,0.0,"- 0.0", verticalalignment='center', fontsize=11)
plt.text(1.1,0.5,"- 0.5", verticalalignment='center', fontsize=11)
plt.text(1.1,1,"- 1.0", verticalalignment='center', fontsize=11)
plt.text(1.1,1.5,"- 1.5", verticalalignment='center', fontsize=11)
plt.text(1.1, 2,"- 2.0", verticalalignment='center', fontsize=11)
plt.text(1.1,2.5,"- 2.5", verticalalignment='center', fontsize=11)
plt.text(1.1,3,"- 3.0", verticalalignment='center', fontsize=11)
plt.text(1.1,3.5,"- 3.5", verticalalignment='center', fontsize=11)
plt.text(1.1,4,"- 4.0", verticalalignment='center', fontsize=11)

plt.text(0.77, 0.056,"Light Rain", verticalalignment='center', fontsize=11, color='darkgreen')
plt.text(0.77,0.2,"Moderate Rain", verticalalignment='center', fontsize=11, color='goldenrod')
plt.text(0.77,0.4,"Heavy Rain", verticalalignment='center', fontsize=11, color='darkred')

plt.legend(loc='upper right', fontsize=10.5)    #, bbox_to_anchor=(-0.02,-.34)
#plt.tight_layout()
#plt.show()
img_path = '‪P:/2020/Meyers Nave/GIS/Figure/DebrisThreshold_all_returnPeriod_Mountainpart.jpg'
plt.savefig(img_path.strip('\u202a'))    