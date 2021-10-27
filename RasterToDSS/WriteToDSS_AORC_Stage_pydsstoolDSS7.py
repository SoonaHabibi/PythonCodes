# -*- coding: utf-8 -*-
"""
The code read AORC gridded data in NetCDF format and StageIV (Grib) and convert them into dss version 7 using pydsstools library.


Created on Mon Aug 30 09:38:45 2021

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
from affine import Affine
import numpy as np
import numpy.ma as ma
from affine import Affine
from pydsstools.heclib.dss.HecDss import Open
from pydsstools.heclib.utils import gridInfo
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
StageIVFileBase=StageIVDir+'ST4.2002010100.01h'

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

# Read base file for each dataset, and save geotransform, projection, ... 
Flag='StageIII'
dataset = gdal.Open(StageIIIFileBase) 
gdal.Warp('C:/Users/SARDEKANI/Documents/StageIIIReproj2.asc',StageIIIFileBase,dstSRS='EPSG:5070')
# StageIIIFileBaseReproj='C:/Users/SARDEKANI/Documents/StageIIIReproj'
ncol[Flag]=dataset.RasterXSize 
nrow[Flag]=dataset.RasterYSize
proj[Flag]=dataset.GetProjection()
gt[Flag] = dataset.GetGeoTransform()
xllcorner[Flag]=gt[Flag][0]
yllcorner[Flag]=gt[Flag][3]+nrow[Flag]*gt[Flag][5]
xurcorner[Flag]=gt[Flag][0]+ncol[Flag]*gt[Flag][1]
yurcorner[Flag]=gt[Flag][3]
    
Flag='StageIV'
dataset = gdal.Open(StageIVFileBase) 
ncol[Flag]=dataset.RasterXSize 
nrow[Flag]=dataset.RasterYSize
proj[Flag]=dataset.GetProjection()
gt[Flag] = dataset.GetGeoTransform()
xllcorner[Flag]=gt[Flag][0]
yllcorner[Flag]=gt[Flag][3]+nrow[Flag]*gt[Flag][5]
    
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

# Get the new row and column for StageIV and AORC

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
    


DssFILE='P:/2019/NASA_UTA/Data/DSS_events/Grid_Prec_Events.dss'
Dtype=1   #PER-CUM
Dunits='mm'
Variable='Precip'

# StageIII
# errorasc=[]
# Flag='StageIII'
# PartB='StageIII'
# Dunits='mm'
# for i in range(4,len(beg)):
#     date_range=pd.date_range(beg[i],end[i],freq='1H')
#     PartF='Event'+str(i+1)
#     if date_range[0].year>2003:
#         for j, dateI in enumerate(date_range):
#             print(dateI)
#             StartTime = dateI.strftime("%d%b%Y:%H%M")
#             EndTime = (dateI + timedelta(hours=1)).strftime("%d%b%Y:%H%M")
#             # To Change 00:00 to 24:00, DSS don't understand 00:00 for the end of period!
#             if EndTime[-4:] == '0000': 
#                 list1 = list(EndTime)
#                 list1[-4:] = '2400'
#                 list1[0:5] = StartTime[0:5]
#                 EndTime = ''.join(list1)
    
#             Flag='StageIII'
#              #StageIII is available from 2004
#             Datestr=dateI.strftime('%d%b%Y_%H%M')
#             Infile=StageIIIDir+'stageIII_'+Datestr+'.asc'
#             if os.path.exists(Infile):
#                 BF.asc2dssGrid(Infile,DssFILE,Variable,StartTime,EndTime, Dunits, Dtype,PartB, PartF)
#             else: 
#                 print('Not Available: ', Infile)
#                 errorasc.append(dateI)

    
Errors=[]    
# AORC 
Flag='AORC'
BatchFileName='//westfolsom/Office/Python/DSS_Utility_exe_for_Python_Functions/Ascii2gridAORC.bat'
asc2dssGridExe='//westfolsom/Office/Python/DSS_Utility_exe_for_Python_Functions/asc2dssGridAORC.exe'
DssFILE='P:/2019/NASA_UTA/Data/DSS_events/AORC_Prec_Events_pydsstool.dss'
Dtype=1
Variable='Precip'
#for i in range(0,15):
for i in range(7,len(beg)):
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
                        rainf[(rainf<0.1)&(rainf>0)]=0                   # put small values to zero
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
                
                # Create grid of zero for missing period! 0 could be replaced with NA value
                else:
                    print ("Error " + Filename)
                    Errors.append(Filename)
                    rainf=np.zeros((nrow[Flag],ncol[Flag]))
                    BF.CreateMatrixFileFloat(tifName,rainf,len(rainf[0]), len(rainf),gt[Flag],proj[Flag])
                    #subprocess.call('gdalwarp -overwrite -s_srs EPSG:4269 -t_srs EPSG:5070 -srcnodata ' + str(MissingValue) + ' -dstnodata ' + str(MissingValue) + ' -tr 500 500 -of GTiff ' + TiffFile +' ' +TiffFile2 ,shell=True
                    # gdal.Warp(TifReproj,tifName,dstSRS='EPSG:5070', xRes=2000,yRes=2000,srcNodata =-901,dstNodata = -901,outputType=gdal.GDT_Int16)
                    # gdal.Warp(TifReproj,tifName,dstSRS='EPSG:5070', xRes=2000,yRes=2000,srcNodata =-901,dstNodata = -901)
                    gdal.Warp(AscReproj,tifName,dstSRS='EPSG:5070', xRes=2000,yRes=2000,srcNodata =-901,dstNodata = -901)
                
            
            EndTime = dateI.strftime("%d%b%Y:%H%M")
            StartTime = (dateI - timedelta(hours=1)).strftime("%d%b%Y:%H%M")
            # To Change 00:00 to 24:00, DSS don't understand 00:00 for the end of period!
            if EndTime[-4:] == '0000': 
                list1 = list(EndTime)
                list1[-4:] = '2400'
                list1[0:5] = StartTime[0:5]
                EndTime = ''.join(list1)

            dataset = gdal.Open(AscReproj)   
            ncolZ = dataset.RasterXSize            
            nrowZ = dataset.RasterYSize
            gfZ = dataset.GetGeoTransform()           
            rb = dataset.GetRasterBand(1)
            aa = rb.ReadAsArray().astype(np.float)                
            cellsize = gfZ[1]
            xllcorner = int(round(gfZ[0]))        
            yllcorner = int(round(gfZ[3]+gfZ[5]*(nrowZ)))
            dataset = None
            aa[aa<0] = -901
            
            EndTime = dateI.strftime("%d%b%Y:%H%M")
            StartTime = (dateI - timedelta(hours=1)).strftime("%d%b%Y:%H%M")
            # To Change 00:00 to 24:00, DSS don't understand 00:00 for the end of period!
            if EndTime[-4:] == '0000': 
                list1 = list(EndTime)
                list1[-4:] = '2400'
                list1[0:5] = StartTime[0:5]
                EndTime = ''.join(list1)
            
            
            pathname_out1 = "/SHG/AORC/PRECIP/"+StartTime+"/"+EndTime+"/"+PartF+"/"
            with Open(DssFILE) as fid:
            # np.nan is considered as nodata
                data = aa
                data[data<0] = np.nan # assign nodata to negative Value
                grid_info = gridInfo()
                cellsize = gfZ[1] # feet
                xmin,ymax = (gfZ[0],gfZ[3]) # grid top-left corner coordinates
                affine_transform = Affine(cellsize,0,xmin,0,-cellsize,ymax)
                grid_info.update([('grid_type','specified'),
                                  ('grid_crs','unknown'),
                                  ('grid_transform',affine_transform),
                                  ('data_type','per-cum'),
                                  ('data_units','mm'),
                                  ('opt_time_stamped',False)])
                fid.put_grid(pathname_out1,data,grid_info)
                
                                
df_error=pd.DataFrame(Errors,columns=['MissingDate'])
df_error.to_csv('P:/2019/NASA_UTA/Data/AORC/Errors.csv')
        

ErrorsStageIV=[]    
# StageIV
Flag='StageIV'
MissingValue=-901
DssFILE='P:/2019/NASA_UTA/Data/DSS_events/StageIV_Prec_Events_dss7.dss'
ErrorsStageIV=[]
PartB='StageIV'
Dunits='mm'
for i in range(len(beg)):
    date_range=pd.date_range(beg[i],end[i],freq='1H')
    PartF='Event'+str(i+1)
    
    if date_range[i].year>=2002:
        AscDir='P:/2019/NASA_UTA/Data/StageIV/'+date_range[0].strftime('%b%Y')+'/'
        if not os.path.exists(AscDir): os.mkdir(AscDir)
        
        for j, dateI in enumerate(date_range):    
            print(dateI)
            dateStr=dateI.strftime('%Y%m%d%H')
            
            # Naming of StageIV files is not consistent! Therefore all the 5 following format should be checked
            # Naming formats after 2020 are different and needs to be added in here.
            fname=StageIVDir+'st4.'+dateStr+'.01h.gz'
            fname1=StageIVDir+'st4_pr.'+dateStr+'.01h.gz'
            fname2=StageIVDir+'ST4.'+dateStr+'.01h.gz'
            fname3=StageIVDir+'ST4.'+dateStr+'.01h.z'
            fname4=StageIVDir+'st4.'+dateStr+'.01h.z'
            try:
                if os.path.exists(fname):
                    print(fname)
                    if not os.path.exists(fname[:-3]):
                        with gzip.open(fname, 'rb') as f_in:
                            with open(fname[:-3], 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                    img = gdal.Open(fname[:-3])
                    band = img.GetRasterBand(1)                
                    rain = band.ReadAsArray()
                    
                elif os.path.exists(fname1): 
                    print(fname1)
                    if not os.path.exists(fname1[:-3]):
                        with gzip.open(fname1, 'rb') as f_in:
                            with open(fname1[:-3], 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                    img = gdal.Open(fname1[:-3])
                    band = img.GetRasterBand(1)                
                    rain = band.ReadAsArray()
                    
                elif os.path.exists(fname2): 
                    print(fname2)
                    if not os.path.exists(fname2[:-3]):
                        with gzip.open(fname2, 'rb') as f_in:
                            with open(fname2[:-3], 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                    img = gdal.Open(fname2[:-3])
                    band = img.GetRasterBand(1)                
                    rain = band.ReadAsArray()
                    
                elif os.path.exists(fname3)|os.path.exists(fname3[:-2]):
                    if not os.path.exists(fname3[:-2]):
                        out="F:/StageIV/"
                        unzip_cmd_str = 'C:/"Program Files"/WinRAR/WinRAR.exe' + " x " + fname3 + " *.* " + out
                        subprocess.call(unzip_cmd_str,shell=True)
                        os.remove(fname3)
                        print ('Unzip: ',fname3)
    
                    img = gdal.Open(fname3[:-2])
                    band = img.GetRasterBand(1)                
                    rain = band.ReadAsArray()
                elif os.path.exists(fname4)|os.path.exists(fname4[:-2]): 
                    if not os.path.exists(fname4[:-2]):
                        out="F:/StageIV/"
                        unzip_cmd_str = 'C:/"Program Files"/WinRAR/WinRAR.exe' + " x " + fname4 + " *.* " + out
                        subprocess.call(unzip_cmd_str,shell=True)
                        os.remove(fname4)
                        print ('Unzip: ',fname4)
                        
                    img = gdal.Open(fname4[:-2])
                    band = img.GetRasterBand(1)                
                    rain = band.ReadAsArray()
                    
                else:                # create a grid of NA (-901) for periods with missing data
                    print ("Not Available ", dateStr)
                    ErrorsStageIV.append(dateStr)
                    rain=np.zeros((nrow[Flag],ncol[Flag]))
                    rain=rain-901

                rain[rain<0]=-901
                rain[rain>999]=-901
                tifName=AscDir+'AORC_'+Datestr+'.tif'
                BF.CreateMatrixFileFloat(tifName,rain,len(rain[0]), len(rain),gt[Flag],proj[Flag])
                # reproject the total map
                AscReproj=AscDir+'StageIV_'+Datestr+'_reproj.asc'
                warp = gdal.Warp(AscReproj,tifName,dstSRS='EPSG:5070', xRes=2000,yRes=2000,srcNodata =-901,dstNodata = -901, outputBounds=[BB2[2], BB2[0], BB2[3], BB2[1]])

                EndTime = dateI.strftime("%d%b%Y:%H%M")
                StartTime = (dateI - timedelta(hours=1)).strftime("%d%b%Y:%H%M")
                # To Change 00:00 to 24:00, DSS don't understand 00:00 for the end of period!
                if EndTime[-4:] == '0000': 
                    list1 = list(EndTime)
                    list1[-4:] = '2400'
                    list1[0:5] = StartTime[0:5]
                    EndTime = ''.join(list1)

                pathname_out1 = "/SHG/AORC/PRECIP/"+StartTime+"/"+EndTime+"/"+PartF+"/"
                
                with Open(DssFILE) as fid:
                # np.nan is considered as nodata
                    data = aa
                    data[data<0] = np.nan # assign nodata to negative value
                    grid_info = gridInfo()
                    cellsize = gfZ[1] # feet
                    xmin,ymax = (gfZ[0],gfZ[3]) # grid top-left corner coordinates
                    affine_transform = Affine(cellsize,0,xmin,0,-cellsize,ymax)
                    grid_info.update([('grid_type','specified'),
                                      ('grid_crs','unknown'),
                                      ('grid_transform',affine_transform),
                                      ('data_type','per-cum'),
                                      ('data_units','mm'),
                                      ('opt_time_stamped',False)])
                    fid.put_grid(pathname_out1,data,grid_info)
                    
                    
            except:
                print('error:', EndTime)
                ErrorsStageIV.append(EndTime)
                
                
                            
df_error=pd.DataFrame(ErrorsStageIV,columns=['MissingDate'])
df_error.to_csv('P:/2019/NASA_UTA/Data/AORC/Errors.csv')