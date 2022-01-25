# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 08:37:05 2020

@author: sardekani
"""

import glob
import gdal
import numpy as np
import sys 
sys.path.append("//westfolsom/Office/Python/WEST_Python_FunctionAug2019");
import BasicFunction_py3 as BF
Proj ='GEOGCS["WGS 84", DATUM["WGS_1984", SPHEROID["WGS 84",6378137,298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich",0], UNIT["degree",0.0174532925199433], AUTHORITY["EPSG","4326"]]' 
def CreateMatrixFileFloat(TiffFile,arr,ncol, nrow,gt,Proj):
    # Extract data block
    driver = gdal.GetDriverByName('GTiff')

    dst_ds = driver.Create( TiffFile, int(ncol), int(nrow), int(1), gdal.GDT_Float64 )    
    dst_ds.SetGeoTransform( gt )  
    dst_ds.SetProjection( Proj )
    dst_ds.GetRasterBand(1).WriteArray( arr )
    dst_ds = None

indir = 'P:/2020/Meyers Nave/AWA SPAS/SPAS Report/RawSPAS_Output/10min_ppt_spas1785/'
outdir = 'P:/2020/Meyers Nave/AWA SPAS/SPAS Report/RawSPAS_Output/10min_rainrate_inPERhr/'
tif10min = glob.glob(indir + '*.tif')
for i in range(len(tif10min)):
    Tiffpath= tif10min[i]
    dataset = gdal.Open(Tiffpath) 
    arr = dataset.ReadAsArray()
    arr = arr*6
    Proj='GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]'     
    gt = (-120.15, 0.009999999999999995, 0.0, 34.9, 0.0, -0.009999999999999964)
    ncol=dataset.RasterXSize 
    nrow=dataset.RasterYSize
    TiffFile = Tiffpath.replace('RawSPAS_Output', 'RawSPAS_Output')
    CreateMatrixFileFloat(TiffFile,arr,ncol, nrow,gt,Proj) 


import os

outdir = 'P:/2020/Meyers Nave/AWA SPAS/SPAS Report/RawSPAS_Output/5min_rainrate_inPERhr/'
tif10min = glob.glob(outdir + '*0*')
for i in range(1,len(tif10min)):
    path= tif10min[i]
    Oldname=path[path.find('\\')+2:]
    newname=path[:path.find('\\')+1]+'5min_spas_rainrate_inPERhr_2018'+Oldname
    os.rename(path, newname)
    