# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 21:54:43 2021

@author: sardekani

Reading AORC rainfall dataset and calculate 1 year, 5 year, 10 year total rainfall 
and generate map
"""
from mpl_toolkits.basemap import Basemap
import sys 
sys.path.append("//WESTFOLSOM/Office/Python/WEST_Python_FunctionAug2019/");
import BasicFunction_py3 as BF
import numpy as np
import os

import math as m
from scipy.linalg import logm, expm
from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
from osgeo import gdal
from osgeo import osr
from osgeo.gdalconst import GA_ReadOnly
from datetime import timedelta
import pandas as pd
from datetime import datetime, date, time
from scipy.interpolate import interp1d
from scipy.interpolate import interp2d 
import subprocess
import copy
import matplotlib.pyplot as plt 



Flag='AORC'          # flag can be defined as 'StageIII', 'Mesonet' and 'AORC'
ProjFlag=0          # index of desired project 0:'TexasStorm', 1:'ArizonaStorm'
RFCAr=['WGRFC','CBRFC']
ProjName=['TexasStorm', 'ArizonaStorm']
maxPrAr=[4,3]
maxPr5Ar=[5,5]
maxPr10Ar=[5,5]
minPr=1
Units="MM"
Len=[1,5,10]
BoundaryBox=[-9] 


d1 =datetime(1979, 3, 1, 0, 0, 0)                    #Start date
# d1 =datetime(2000, 1, 1, 0, 0, 0)                    #Start date
d2 =datetime(2020, 11,23, 22, 0, 0)                  #End date	
YrRange=range(d1.year,d2.year+1)
DateRange=pd.date_range(start=d1, end=d2, freq='H')

AORCInDir='D:/WESTDataCode/Rainfall_MPE_AORC/'       
FileBase = AORCInDir+RFCAr[ProjFlag]+"/Unzip/AORC_APCP_"+RFCAr[ProjFlag]+"_1980010101.nc4"

  
nc_fidproj = Dataset(FileBase, 'r')  
nc_attrs, nc_dims, nc_vars = BF.ncdump(nc_fidproj)

lon_AORC=nc_fidproj.variables['longitude'][:]
lat_AORC=nc_fidproj.variables['latitude'][:]

lon={'AORC':[]}
lat={'AORC':[]}
lon['AORC'].append(nc_fidproj.variables['longitude'][:])
lat['AORC'].append(nc_fidproj.variables['latitude'][:]) 

 
resdegr=lon_AORC[1]-lon_AORC[0]

if(len(BoundaryBox)>1):
    #AORC                         #finding the col and row of the boundry
    LonDomain=lon_AORC[(lon_AORC>=BoundaryBox[2]) & (lon_AORC<=BoundaryBox[3])]
    col1_AORC=int((min(LonDomain)-min(lon_AORC))/resdegr)
    col2_AORC=int((max(LonDomain)-min(lon_AORC))/resdegr)
    ncol_AORC=col2_AORC-col1_AORC+1
    LatDomain=lat_AORC[(lat_AORC>=BoundaryBox[0]) & (lat_AORC<=BoundaryBox[1])]
    row1_AORC=int((min(LatDomain)-min(lat_AORC))/resdegr)
    row2_AORC=int((max(LatDomain)-min(lat_AORC))/resdegr)
    nrow_AORC=row2_AORC-row1_AORC+1

else:
    #AORC
    LatDomain=np.copy(lat_AORC)
    LonDomain=np.copy(lon_AORC)
    row1_AORC=0
    row2_AORC=len(lat_AORC)
    nrow_AORC=len(lat_AORC)
    col1_AORC=0
    col2_AORC=len(lon_AORC)
    ncol_AORC=len(lon_AORC)

#nc_attrs, nc_dims, nc_vars = BF.ncdump(nc_fidproj)
ProjSys_AORC='GEOGCS["NAD83",DATUM["North_American_Datum_1983",SPHEROID["GRS 1980",6378137,298.2572221010042,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6269"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4269"]]'   
AORCgeotransform=(min(lon_AORC)-resdegr/2,resdegr,0.0,max(lat_AORC)+resdegr/2,0.0,-resdegr)
#ProjSys_AORC='EPSG:4269'


inidate=d1
inidate5=d1
inidate10=d1
Errors=[]


Tot1yr={'AORC':np.zeros((nrow_AORC,ncol_AORC))}
Tot1yrAr={'AORC':[]}
Tot5yr={'AORC':np.zeros((nrow_AORC,ncol_AORC))}
Tot10yr={'AORC':np.zeros((nrow_AORC,ncol_AORC))}
Tot={'AORC':np.zeros((nrow_AORC,ncol_AORC))}

if Flag=='AORC':
    OutputDir="P:/2021/"+ProjName[ProjFlag]+"/Data/AORC/"
    if not os.path.exists(OutputDir): os.mkdir(OutputDir)  
    
    for dt in DateRange:
        Datestr=date.strftime(dt, '%Y%m%d%H')
        Datestr2=date.strftime(dt, '%d%b%Y_%H%M')
        Filename=AORCInDir+RFCAr[ProjFlag]+"/Unzip/AORC_APCP_"+RFCAr[ProjFlag]+"_"+Datestr+".nc4"
        
        if os.path.exists(Filename):
            try:
                print(Filename)
                nc_fidproj = Dataset(Filename, 'r')  
                #rain=nc_fidproj.variables['APCP_surface'][:][:].data[0]
                rain=nc_fidproj.variables['APCP_surface'][:][:].data[0][row1_AORC:row2_AORC+1,col1_AORC:col2_AORC+1]
                rainf=np.flipud(rain)
                rainf[rainf<0]=0
                # rainf[np.isnan[rainf]]=0
            except:
                print ("Error " + Filename)
                Errors.append(Filename)
                
            if (inidate.year==dt.year):
                Tot1yr['AORC']=Tot1yr['AORC']+rainf
            else:
                FileName=OutputDir+"Tif/Tot1YrPr_"+str(inidate.year)+Units+"_F.tif"
                BF.CreateMatrixFileFloat(FileName,Tot1yr['AORC'],len(Tot1yr['AORC'][0]), len(Tot1yr['AORC']),AORCgeotransform,ProjSys_AORC)
                #
                #Generate Total Precipitation (MM) Plot
                #
                maxPr=maxPrAr[ProjFlag]
                title=str(inidate.year)+' Total Precip (mm)'
                ShapeFile='O:/GIS/usa/StateBoundaries/states_21basic/states'
                OutFilePath="P:/2021/"+ProjName[ProjFlag]+"/Data/AORC/Plot/1YrTot_"+str(inidate.year)+".jpg"
                BF.RasterMap(FileName, ShapeFile, OutFilePath, title, minPr, maxPr)
                
                # Start summing precipitation for next year
                Tot1yrAr['AORC'].append(Tot1yr['AORC'])
                Tot1yr['AORC']=rainf
                inidate=dt
    FileName=OutputDir+"Tif/Tot1YrPr_"+str(inidate.year)+Units+"_F.tif"
    BF.CreateMatrixFileFloat(FileName,Tot1yr['AORC'],len(Tot1yr['AORC'][0]), len(Tot1yr['AORC']),AORCgeotransform,ProjSys_AORC)
    #
    #Generate Total Precipitation (MM) Plot
    #
    minPr=0
    maxPr=maxPrAr[ProjFlag]
    title=str(inidate.year)+' Total Precip (mm)'
    ShapeFile='O:/GIS/usa/StateBoundaries/states_21basic/states'
    OutFilePath="P:/2021/"+ProjName[ProjFlag]+"/Data/AORC/Plot/1YrTot_"+str(inidate.year)+".jpg"
    BF.RasterMap(FileName, ShapeFile, OutFilePath, title, minPr, maxPr)
    

#
# Generate 5yr, 10yr and entire period rainfall
#
Tot5yr={'AORC':np.zeros((nrow_AORC,ncol_AORC))}
Tot10yr={'AORC':np.zeros((nrow_AORC,ncol_AORC))}
Tot={'AORC':np.zeros((nrow_AORC,ncol_AORC))}
counter5=0
counter10=0
ShapeFile='O:/GIS/usa/StateBoundaries/states_21basic/states'
OutputDir="P:/2021/"+ProjName[ProjFlag]+"/Data/AORC/"

for iAr in range(len(YrRange)):
    TifInp="P:/2021/"+ProjName[ProjFlag]+"/Data/AORC/Tif/Tot1YrPr_"+str(YrRange[iAr])+"MM_F.tif"
    gdata = gdal.Open(TifInp)
    geo = gdata.GetGeoTransform()
    Tot1yr['AORC']= gdata.ReadAsArray()
    Tot['AORC']=Tot1yr['AORC']+Tot['AORC']
    if counter5<5:
        Tot5yr['AORC']=Tot1yr['AORC']+Tot5yr['AORC']
        counter5=counter5+1
    else:
        FileName5=OutputDir+"Tif/5YrTotalPr_"+str(YrRange[iAr-5])+'_'+str(YrRange[iAr-1])+Units+"_F1.tif"
        BF.CreateMatrixFileFloat(FileName5,Tot5yr['AORC'],len(Tot5yr['AORC'][0]), len(Tot5yr['AORC']),AORCgeotransform,ProjSys_AORC)
        OutFilePath5="P:/2021/"+ProjName[ProjFlag]+"/Data/AORC/Plot/5YrTot_"+str(YrRange[iAr-5])+'_'+str(YrRange[iAr-1])+".jpg"
        title5=str(YrRange[iAr-5])+'_'+str(YrRange[iAr-1])+' Total Precip (mm)- 5 yr'
        BF.RasterMap(FileName5, ShapeFile, OutFilePath5, title5, minPr, maxPr5Ar[ProjFlag])
        counter5=1
        Tot5yr['AORC']=np.zeros((nrow_AORC,ncol_AORC))
    if counter10<10:
        Tot10yr['AORC']=Tot1yr['AORC']+Tot10yr['AORC']
        counter10=counter10+1
    else:
        FileName10=OutputDir+"Tif/10YrTotalPr_"+str(YrRange[iAr-10])+'_'+str(YrRange[iAr-1])+Units+"_F1.tif"
        BF.CreateMatrixFileFloat(FileName10,Tot10yr['AORC'],len(Tot10yr['AORC'][0]), len(Tot10yr['AORC']),AORCgeotransform,ProjSys_AORC)
        OutFilePath10="P:/2021/"+ProjName[ProjFlag]+"/Data/AORC/Plot/10YrTot_"+str(YrRange[iAr-10])+'_'+str(YrRange[iAr-1])+".jpg"
        title10=str(YrRange[iAr-10])+'_'+str(YrRange[iAr-1])+' Total Precip (mm)- 10 yr'
        BF.RasterMap(FileName10, ShapeFile, OutFilePath10, title10, minPr, maxPr10Ar[ProjFlag])
        counter10=1
        Tot10yr['AORC']=np.zeros((nrow_AORC,ncol_AORC))
    
FileName=OutputDir+"Tif/TotalPr_"+str(YrRange[0])+'_'+str(YrRange[-1])+Units+"_F1.tif"
BF.CreateMatrixFileFloat(FileName,Tot['AORC'],len(Tot['AORC'][0]), len(Tot['AORC']),AORCgeotransform,ProjSys_AORC)
ShapeFile='O:/GIS/usa/StateBoundaries/states_21basic/states'
OutFilePath="P:/2021/"+ProjName[ProjFlag]+"/Data/AORC/Plot/Tot_"+str(YrRange[0])+'_'+str(YrRange[iAr])+".jpg"
title=str(YrRange[0])+'_'+str(YrRange[iAr])+' Total Precip (mm)'
BF.RasterMap(FileName, ShapeFile, OutFilePath, title, np.log10(Tot['AORC'][Tot['AORC']>0].min()), np.log10(Tot['AORC'].max()))


# Generate plot - 1 year total
for yr in YrRange:
    TifInp="P:/2021/"+ProjName[ProjFlag]+"/Data/AORC/Tif/Tot1YrPr_"+str(yr)+"MM_F.tif"
    gdata = gdal.Open(TifInp)
    geo = gdata.GetGeoTransform()
    data = gdata.ReadAsArray()
    
    xres = geo[1]
    yres = geo[5]
    
    xmin = geo[0] + xres * 0.5
    xmax = geo[0] + (xres * gdata.RasterXSize) - xres * 0.5
    ymin = geo[3] + (yres * gdata.RasterYSize) + yres * 0.5
    ymax = geo[3] - yres * 0.5
    
    
    plt.figure(figsize=(30,15))
    plt.rcParams.update({'font.size': 22})
    # A good LCC projection for USA plots
    m = Basemap(llcrnrlon=xmin-2,llcrnrlat=ymin-2,urcrnrlon=xmax+2,urcrnrlat=ymax+2,
                projection='lcc',lat_1=33,lat_2=45,lon_0=-95)
    
    # This just plots the shapefile
    m.readshapefile('O:/GIS/usa/StateBoundaries/states_21basic/states','Counties',drawbounds=True, color='0.3')
    
    #This just plots the Nexrad Point shapefile 
    Radar=m.readshapefile('O:/GIS/usa/NEXRAD_Sites/nexrad sites','code')
    for point in m.code:
        m.plot(point[0], point[1], marker='+', color='r', markersize=8, markeredgewidth=4)


    # Add DEM contour to the plot
    DEMfile='‪P:/2021/ArizonaStorm/Data/GIS/1kmDEM_usa.tif'
    gdataDEM = gdal.Open(DEMfile.lstrip('\u202a'))
    geoDEM = gdataDEM.GetGeoTransform()
    dataDEM = gdataDEM.ReadAsArray()
    
    # create arrays with all lon/lat values from min to max and
    xresDEM = geoDEM[1]
    yresDEM = geoDEM[5]
    xminDEM = geoDEM[0] + xresDEM * 0.5
    xmaxDEM = geoDEM[0] + (xresDEM * gdataDEM.RasterXSize) - xresDEM * 0.5
    yminDEM = geoDEM[3] + (yresDEM * gdataDEM.RasterYSize) + yresDEM * 0.5
    ymaxDEM = geoDEM[3]

    xDEM,yDEM = np.mgrid[xminDEM:xmaxDEM+xresDEM:xresDEM, ymaxDEM+yresDEM:yminDEM:yresDEM]
    xDEM,yDEM = m(xDEM,yDEM)
    
    # Make contour plot
    cs = m.contour(xDEM, yDEM, dataDEM.T, 40, colors="k", lw=0.5, alpha=0.3)

    # m.etopo(scale=0.5, alpha=0.5)
    
    x,y = np.mgrid[xmin:xmax+xres:xres, ymax+yres:ymin:yres]
    x,y = m(x,y)
    
    cmap = plt.cm.gist_rainbow
    cmap.set_under ('1.0')
    cmap.set_bad('0.8')
    
    im = m.pcolormesh(x,y, np.log10(data.T), cmap=cmap, vmin=1, vmax=maxPrAr[ProjFlag])
    # im = m.pcolormesh(x,y, data.T, cmap=cmap, vmin=0, vmax=data.max())
    
    cb = plt.colorbar( orientation='vertical', fraction=0.10, shrink=0.7, label='Log10(rainfall[mm])')
    plt.title(str(yr)+' Total Precip (mm)')
    Outplot="P:/2021/"+ProjName[ProjFlag]+"/Data/AORC/Plot/1YrTot_"+str(yr)+".jpg"
    plt.legend()
    plt.savefig(Outplot,bbox_inches='tight',dpi=500)
    plt.close()
