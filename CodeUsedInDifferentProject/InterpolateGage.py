# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 14:18:43 2017

@author: lcunha
"""

import jdcal
from ftplib import FTP
import os, sys
import datetime
import bz2
import sys
from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
from datetime import timedelta as td
sys.path.append("C:/Users/lcunha/Documents/PRISM");
import gdal
sys.path.append("//WESTFOLSOM/Office/Python/West_Python_Functions");
import numpy as np
import BasicFunction as BF   
import West_Functions as WF
import os
import subprocess
import calendar
from os import system
import matplotlib.pyplot as plt

def asc2dssGrid(Infile,DssFILE,Variable,StartTime,EndTime):

    BatchFileName='P:\\2015\\USACE\\HHT\\Garrison\\Data\\DSS\\Ascii2grid7.bat'
    asc2dssGridExe='P:/2015/USACE/HHT/Garrison/Data/DSS/asc2dssGrid.exe'
    myfilem = open(BatchFileName, 'w') 
    
    if(Variable=='prec'):          
        myfilem.write(asc2dssGridExe+' in='+ Infile+' dss='+DssFILE+' path=/SHG/GARRISON/'+Variable+'/'+StartTime+'/'+EndTime+'/Livneh/ GRIDTYPE=SHG DUNITS=mm DTYPE=1')    
    else:        
        myfilem.write(asc2dssGridExe+' in='+ Infile+' dss='+DssFILE+' path=/SHG/GARRISON/'+Variable+'/'+StartTime+'/'+EndTime+'/Livneh/ GRIDTYPE=SHG DUNITS=Deg C DTYPE=2')    

    myfilem.close()    
    subprocess.call(BatchFileName, shell=True)
        
def GDAL_Grid(Infolder, Outfolder, Filename, BoundingBos,CellSizeX,CellSizeY,XField,YField,ZField,Outputfile):

    GridSizeX=round(abs(BoundingBos[2]-BoundingBos[3])/CellSizeX)
    GridSizeY=round(abs(BoundingBos[0]-BoundingBos[1])/CellSizeY)
    
      
    if not os.path.exists(Infolder):
        os.mkdir(Infolder) 
    BatchFileName=Outfolder+'/BatchFile.bat' 
    CSVinput=Infolder+'\\'+Filename+'.csv'
    VRTfileNAME=Outfolder+'\\dem.vrt'   
#    Outputfile=Outfolder+'\\'+Filename+'.tif'
    
    #create .vrt file
    myfilem = open(VRTfileNAME, 'w')
    
    myfilem.write("<OGRVRTDataSource>")
    myfilem.write("\n")
    myfilem.write('    <OGRVRTLayer name='+'"'+Filename+'"'+'>')
    myfilem.write("\n")
    myfilem.write("        <SrcDataSource>")
    myfilem.write(CSVinput)
    myfilem.write("</SrcDataSource>")
    myfilem.write("\n")
    myfilem.write('        <GeometryType>wkbPoint</GeometryType>')
    myfilem.write("\n")
    myfilem.write("        <GeometryField encoding="+'"'+"PointFromColumns"+'"'+" x=")
    myfilem.write('"'+XField+'"')
    myfilem.write(" y=")
    myfilem.write('"'+YField+'"')
    myfilem.write(" z=")
    myfilem.write('"'+ZField+'"')
    myfilem.write("/>")
    myfilem.write("\n")
    myfilem.write("    </OGRVRTLayer>")
    myfilem.write("\n")
    myfilem.write("</OGRVRTDataSource>")
    
    myfilem.close()
    
    #CreateBatch
    myfilem = open(BatchFileName, 'w')
    
    myfilem.write('C:/"Program Files"/GDAL/gdal_grid -a_srs EPSG:4269 -a invdist:power=2.0:smoothing=0:max_points=12 -txe'+' '+str(BoundingBos[2])+' '+str(BoundingBos[3])+ " -tye " +str(BoundingBos[0])+' '+str(BoundingBos[1])+ " -outsize " +str(GridSizeX) +' ' + str(GridSizeY)+ ' -of GTiff -ot Float64 -l '+Filename+' ' +VRTfileNAME+' '+ Outputfile )
#    myfilem.write('C:/"Program Files"/GDAL/gdal_grid -a_srs EPSG:4269 -a invdist:power=2.0:smoothing=0:max_points=12 -txe'+' '+str(BoundingBos[2])+' '+str(BoundingBos[3])+ " -tye " +str(BoundingBos[0])+' '+str(BoundingBos[1])+ " -outsize " +str(GridSizeX) +' ' + str(GridSizeY)+ ' -of GTiff -ot Float64 -l '+Filename+' '+ Outputfile )
#    print 'C:/"Program Files"/GDAL/gdal_grid -a_srs EPSG:4269 -a invdist:power=2.0:smoothing=0:max_points=12 -txe'+' '+str(BoundingBos[2])+' '+str(BoundingBos[3])+ " -tye " +str(BoundingBos[0])+' '+str(BoundingBos[1])+ " -outsize " +str(GridSizeX) +' ' + str(GridSizeY)+ ' -of GTiff -ot Float64 -l '+Filename+' '+ Outputfile
    myfilem.close()
    
    subprocess.call(BatchFileName)
    
import glob
Files=glob.glob("P:/2019/UmpquaRiver/Precipitation-Temperature/*.csv")




