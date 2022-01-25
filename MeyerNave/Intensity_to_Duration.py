# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 15:15:03 2020

@author: sardekani
"""

import pandas as pd
import numpy as np
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
import sys 
sys.path.append("//westfolsom/Office/Python/WEST_Python_FunctionAug2019");
import BasicFunction_py3 as BF


freq = [1,2,5,10,25,50,100,200,500,1000]
rain_5min = [0.158, 0.199, 0.252, 0.294, 0.351, 0.394, 0.438, 0.481, 0.54, 0.584]
rain_10min = [0.226, 0.285, 0.361, 0.422, 0.504, 0.565, 0.627, 0.69, 0.773, 0.837]
rain_15min = [0.273, 0.345, 0.437, 0.51, 0.609, 0.684, 0.758, 0.834, 0.935, 1.01]
rain_30min = [0.426, 0.537, 0.681, 0.796, 0.95, 1.07, 1.18, 1.3, 1.46, 1.58]
rain_60min = [0.638, 0.805, 1.02, 1.19, 1.42,1.6, 1.77, 1.95, 2.19, 2.37]
intensityAr = [rain_5min, rain_10min, rain_15min, rain_30min, rain_60min]
duration = [5, 10, 15, 30, 60]
dur_1yr_lr_band = [0.135, 0.194, 0.234, .365, .547]
dur_1000yr_upper_band = [0.871, 1.25, 1.51, 2.35, 3.53]

indir = 'P:/2020/Meyers Nave/AWA SPAS/SPAS Report/RawSPAS_Output/Data/'
outdir = 'P:/2020/Meyers Nave/PixelFrequency/'

for i in range(len(duration)):
    TiffFile = indir + 'spas1721_Max_' + str(duration[i]) +'.tif'
    dataset = gdal.Open(TiffFile, GA_ReadOnly) 
    rb = dataset.GetRasterBand(1)
    RainRate = rb.ReadAsArray()
    freqAr = np.zeros(RainRate.shape)
    intensity = intensityAr [i]
    for j in range(len(freq)-1):
        slope = (freq[j+1]-freq[j])/(intensity[j+1]-intensity[j])
        freqAr[(RainRate>=intensity[j]) & (RainRate<=intensity[j+1])] = freq[j] + (RainRate[(RainRate>=intensity[j]) \
             & (RainRate<=intensity[j+1])]-intensity[j])*slope
    freqAr[RainRate>dur_1000yr_upper_band[i]] = 10000          # 10000 means freq>1000 yr, 0 means freq<1
    freqAr = freqAr.round(decimals=0)
    RainRate[RainRate<0] = 0 
    ncol = dataset.RasterXSize 
    nrow = dataset.RasterYSize
    Proj = dataset.GetProjection()               
    gt = dataset.GetGeoTransform()
    
    Tiffout = outdir + str(duration[i]) + 'minDuration_freq.tif'
    BF.CreateMatrixFileFloat(Tiffout, freqAr, ncol, nrow, gt, Proj) 