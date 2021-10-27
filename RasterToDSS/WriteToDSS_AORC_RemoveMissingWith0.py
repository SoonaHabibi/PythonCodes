# -*- coding: utf-8 -*-
"""
The code read AORC gridded data in NetCDF format and convert it into a dss version 6.
Due to no coverage over golf all missing value were replaced with 0 to increase processing time.

NOTE: AORC and StageIV are hourly precip data in mm

Created on Wed Sep  1 00:06:01 2021

@author: sardekani
"""

import pandas as pd
import numpy as np
import sys
sys.path.append("//WESTFOLSOM/Office/Python/WEST_Python_FunctionAug2019/");
import BasicFunction_py3 as BF
from osgeo import gdal
from datetime import datetime, timedelta
from netCDF4 import Dataset 
import os 
import gzip
import zlib
import shutil
import subprocess


StageIIIDir='D:/WESTDataCode/Rainfall_StageIII_Texas/asc/'  
AORCInDir='D:/WESTDataCode/Rainfall_MPE_AORC/'    
StageIVDir='F:/StageIV/' 

# Get Start and end of each event
EventIn='P:/2020/LCRA/Stats_Thr-10_98_1_Linear_NLDAS_Aug2/10003_-10/10003_RunoffEvents_top20.csv'
df_event=pd.read_csv(EventIn, date_parser=['RainsStartDateAr1', 'FlowEndDateAr1'])
beg=df_event['RainsStartDateAr1']
end=df_event['FlowEndDateAr1']


# AORC, StageIII and StageIV base file paths
AORCFileBase = AORCInDir+"WGRFC/Unzip/AORC_APCP_WGRFC_1980010101.nc4"
StageIIIFileBase=StageIIIDir+'stageIII_01Apr2007_1000.asc'


# generate empty dictionaries
ncol={}
nrow={}
proj={}
gt={}
xllcorner={}
yllcorner={}
xurcorner={}
yurcorner={}
col1={}
col2={}
row1={}
row2={}

Flag='AORC'
#proj[Flag]='EPSG:4269'
proj[Flag]='GEOGCS["NAD83",DATUM["North_American_Datum_1983",SPHEROID["GRS 1980",6378137,298.2572221010042,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6269"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4269"]]'   
nc_fidproj = Dataset(AORCFileBase, 'r')  
nc_attrs, nc_dims, nc_vars = BF.ncdump(nc_fidproj)
lon_AORC=nc_fidproj.variables['longitude'][:]
lat_AORC=nc_fidproj.variables['latitude'][:]
lon={'AORC':[]}
lat={'AORC':[]}
lon['AORC'].append(nc_fidproj.variables['longitude'][:])
lat['AORC'].append(nc_fidproj.variables['latitude'][:]) 
resdegr=lon_AORC[1]-lon_AORC[0]

# Bounding box is defined based on the StageIII dataset boundary, [yllcorner,yurcorner,xllcorner,xurcorner]
BB1=[23.18338,39.22302,-111.36656,-90.2261]                      # based on degree
BB2=[yllcorner['StageIII'],yurcorner['StageIII'],xllcorner['StageIII'],xurcorner['StageIII']]         #Metric

# Get the new row and column for AORC
Flag='AORC'                  #finding the col and row of the boundry
LonDomain=lon_AORC[(lon_AORC>=BB1[2]) & (lon_AORC<=BB1[3])]
col1[Flag]=int((min(LonDomain)-min(lon_AORC))/resdegr)
col2[Flag]=int((max(LonDomain)-min(lon_AORC))/resdegr)
ncol[Flag]=col2[Flag]-col1[Flag]+1
LatDomain=lat_AORC[(lat_AORC>=BB1[0]) & (lat_AORC<=BB1[1])]
row1[Flag]=int((min(LatDomain)-min(lat_AORC))/resdegr)
row2[Flag]=int((max(LatDomain)-min(lat_AORC))/resdegr)
nrow[Flag]=row2[Flag]-row1[Flag]+1
gt[Flag]=(min(lon_AORC)-resdegr/2,resdegr,0.0,max(lat_AORC)+resdegr/2,0.0,-resdegr)
    


                
Errors=[]    
# AORC 
Flag='AORC'
BatchFileName='//westfolsom/Office/Python/DSS_Utility_exe_for_Python_Functions/Ascii2gridAORC.bat'
asc2dssGridExe='//westfolsom/Office/Python/DSS_Utility_exe_for_Python_Functions/asc2dssGridAORC.exe'
DssFILE='P:/2019/NASA_UTA/Data/DSS_events/AORC_Prec_Events_NoMiss.dss'
Dtype=1
Variable='Precip'
MissingValue=-901
PartB='AORC'
Dunits='mm'
#for i in range(0,15):
for i in range(2,len(beg)):
    date_range=pd.date_range(beg[i],end[i],freq='1H')
    PartF='Event'+str(i+1)
    
    if date_range[i].year>=1979:
        AORCDir='P:/2019/NASA_UTA/Data/AORC/'+date_range[0].strftime('%b%Y')+'_v2/'
        if not os.path.exists(AORCDir): os.mkdir(AORCDir)
        
        for j, dateI in enumerate(date_range):    
            print(dateI)
            Datestr=dateI.strftime('%Y%m%d%H')
            Filename=AORCInDir+"WGRFC/Unzip/AORC_APCP_WGRFC_"+Datestr+".nc4"
            
            tifName=AORCDir+'AORC_'+Datestr+'.tif'
            AscReproj=AORCDir+'AORC_'+Datestr+'_reproj_resample.asc'
            TifReproj=AORCDir+'AORC_'+Datestr+'_reproj_resample.tif'
            if not os.path.exists(AscReproj):
                if os.path.exists(Filename):
                    try:                    
                        nc_fidproj = Dataset(Filename, 'r')  
                        #rain=nc_fidproj.variables['APCP_surface'][:][:].data[0]
                        rain=nc_fidproj.variables['APCP_surface'][:][:].data[0][row1[Flag]:row2[Flag]+1,col1[Flag]:col2[Flag]+1]
                        rainf=np.flipud(rain)
                        rainf=rainf.round(decimals=2)
                        rainf[rainf>300]=-901
                        rainf[(rainf<0.1)&(rainf>0)]=0
                        rainf[rainf<0]=-901
                        rainf[np.isnan(rainf)]=-901
                        BF.CreateMatrixFileFloat(tifName,rainf,len(rainf[0]), len(rainf),gt[Flag],proj[Flag])
                        #subprocess.call('gdalwarp -overwrite -s_srs EPSG:4269 -t_srs EPSG:5070 -srcnodata ' + str(MissingValue) + ' -dstnodata ' + str(MissingValue) + ' -tr 500 500 -of GTiff ' + TiffFile +' ' +TiffFile2 ,shell=True
                        # gdal.Warp(TifReproj,tifName,dstSRS='EPSG:5070', xRes=2000,yRes=2000,srcNodata =-901,dstNodata = -901)
                        gdal.Warp(AscReproj,tifName,dstSRS='EPSG:5070', xRes=2000,yRes=2000,srcNodata =-901,dstNodata = -901)
         
                    except:
                        print ("Error " + Filename)
                        Errors.append(Filename)
                        rainf=np.zeros((nrow[Flag],ncol[Flag]))
                        BF.CreateMatrixFileFloat(tifName,rainf,len(rainf[0]), len(rainf),gt[Flag],proj[Flag])
                        #subprocess.call('gdalwarp -overwrite -s_srs EPSG:4269 -t_srs EPSG:5070 -srcnodata ' + str(MissingValue) + ' -dstnodata ' + str(MissingValue) + ' -tr 500 500 -of GTiff ' + TiffFile +' ' +TiffFile2 ,shell=True
                        # gdal.Warp(TifReproj,tifName,dstSRS='EPSG:5070', xRes=2000,yRes=2000,srcNodata =-901,dstNodata = -901)
                        gdal.Warp(AscReproj,tifName,dstSRS='EPSG:5070', xRes=2000,yRes=2000,srcNodata =-901,dstNodata = -901)
                
                else:
                    print ("Error " + Filename)
                    Errors.append(Filename)
                    rainf=np.zeros((nrow[Flag],ncol[Flag]))
                    BF.CreateMatrixFileFloat(tifName,rainf,len(rainf[0]), len(rainf),gt[Flag],proj[Flag])
                    #subprocess.call('gdalwarp -overwrite -s_srs EPSG:4269 -t_srs EPSG:5070 -srcnodata ' + str(MissingValue) + ' -dstnodata ' + str(MissingValue) + ' -tr 500 500 -of GTiff ' + TiffFile +' ' +TiffFile2 ,shell=True
                    # gdal.Warp(TifReproj,tifName,dstSRS='EPSG:5070', xRes=2000,yRes=2000,srcNodata =-901,dstNodata = -901)
                    gdal.Warp(AscReproj,tifName,dstSRS='EPSG:5070', xRes=2000,yRes=2000,srcNodata =-901,dstNodata = -901)
                
            
            #####
            # This part has been added instead of simply importing BF.TiftoDss subfunction since we needed to 
            # replace all -901 to 0 due to slow processing (There are no Coverage over golf for AORC)
            # for other datasets you can simply use either BF.asc2dssGrid or BF.TiftoDss subfunctions
            ####
            dataset = gdal.Open(TifReproj)
            ncolZ = dataset.RasterXSize            
            nrowZ = dataset.RasterYSize
            gfZ = dataset.GetGeoTransform()           
            rb = dataset.GetRasterBand(1)
            aa = rb.ReadAsArray().astype(np.float)                
            cellsize = gfZ[1]
            xllcorner = int(round(gfZ[0]))        
            yllcorner = int(round(gfZ[3]+gfZ[5]*(nrowZ)))
            dataset = None
    
            aa[np.isnan(aa)] = 0
            aa[aa<0]=0
            header=[]
        
            header.append("ncols "+str(aa.shape[1]))
            header.append("nrows "+str(aa.shape[0]))
            header.append("xllcorner "+str(xllcorner))    
            header.append("yllcorner " +str(yllcorner))
            header.append("cellsize "+str(gfZ[1]))
            header.append("NODATA_value " + str(MissingValue))
            AscReproj=TifReproj[0:TifReproj.rfind('/')+1]+Datestr+'Reproj.asc'
            with open(AscReproj, "w") as f:
                for n in range(0,len(header)):
                    
                    f.write(header[n])
                    f.write('\n')
                    
                np.savetxt(f, aa, fmt="%1.1f")  
                            
            
            EndTime = dateI.strftime("%d%b%Y:%H%M")
            StartTime = (dateI - timedelta(hours=1)).strftime("%d%b%Y:%H%M")
            # To Change 00:00 to 24:00, DSS don't understand 00:00 for the end of period!
            if EndTime[-4:] == '0000': 
                list1 = list(EndTime)
                list1[-4:] = '2400'
                list1[0:5] = StartTime[0:5]
                EndTime = ''.join(list1)

            if os.path.exists(AscReproj):
                myfilem = open(BatchFileName, 'w')         
                if(Dtype==1): strcom=asc2dssGridExe+' in='+ AscReproj+' dss='+DssFILE+' path=/SHG/'+PartB+'/'+Variable+'/'+StartTime+'/'+EndTime+'/'+PartF+'/ GRIDTYPE=SHG DUNITS='+Dunits+' DTYPE='+str(Dtype)
                if(Dtype==2): strcom=asc2dssGridExe+' in='+ AscReproj+' dss='+DssFILE+' path=/SHG/'+PartB+'/'+Variable+'/'+StartTime+'//'+PartF+'/ GRIDTYPE=SHG DUNITS='+Dunits+' DTYPE='+str(Dtype)
                
                myfilem.write(strcom)    
                myfilem.close()    
                flag=subprocess.run(BatchFileName, shell=True)
            # BF.asc2dssGrid(AscReproj,DssFILE,Variable,StartTime,EndTime, Dunits, Dtype,PartB, PartF)

df_error=pd.DataFrame(Errors,columns=['MissingDate'])
df_error.to_csv('P:/2019/NASA_UTA/Data/AORC/Errors.csv')