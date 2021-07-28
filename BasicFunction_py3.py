# -*- coding: utf-8 -*-
"""
NEW FUNCTIONS (8/21/2019):
1) InverseD_Inter
2) asc2dssGrid
3) TiftoDss
4) ReadPRISM
5) CheckStationarity
6) CreateMapSacCounty
7) CreateMask
8) CreateMatrixFileFloat
9) GetAORC
10) GetNLDASSec_py3
11) GribBandtoNParray
12) InverseD_Inter
13) PlotLinearRelationship
14) dss2ascGrid
15) ncdump
16) dss2csv  (for point dss timeseries)
17) RasterMap: Create map of raster file
 
OLDER FUNCTIONS (before 8/21/2019):
1) CreateMatrixFileFloat
    
All Functions:
CheckStationarity
CreateMapSacCounty
CreateMask
CreateMatrixFileFloat
GetAORC
GetNLDASSec_py3
GribBandtoNParray
InverseD_
PlotLinearRelationship
ReadPRISM
TiftoDss
asc2dssGrid
dss2ascGrid
ncdump 
idw               # the sub function creates a wight matrix (it will be used in radar_adj_idw sub function to adjust radar rainfall based on gauges data)
radar_adj_idw       # the sub function output is adjusted radar raster file utilizing gauge data and Inverse Distance Weighting method
"""
   
######################################
#Test
######################################
def test():
    print('Test importing module from github')
    
###############################################################################
# InverseD_Inter
###############################################################################
def InverseD_Inter(smoothing,power,Infolder, Outfolder, Filename, BoundingBox,CellSizeX,CellSizeY,XField,YField,ZField): 
    """This Function creates continuous rainfall data from point rain gauge data using Inverse Distance Technique
    #### Input:
    1. Smoothing: Smoothing parameter (default 0.0)
    2. power: Inverse Distance Weighting power (default 2.0)
    3. Infolder: directory path containing input csv file
    4. Outfolder: path for saving the output of the function
    5. Filename: CSV file name, containing the Lon, Lat and rainfall/spatial variable data
    6. BoundingBox: Lat&Long of area of desire, the order should be the following: [MinLon, MaxLon, MinLat, MaxLat ]
    7. CellSizeX: cell size in X direction
    8. CellSizeY: cell size in Y direction
    9. XField: Column name for Lon
    10. YField: Column name for Lat
    11. ZField: Column name for Spatial Variable
    #### Output:
    1. tiff file containing spatial rainfall calculated by Inverse Distance method"""

    import os
    import subprocess
    GridSizeX = round(abs(BoundingBox[2]-BoundingBox[3])/CellSizeX)
    GridSizeY = round(abs(BoundingBox[0]-BoundingBox[1])/CellSizeY)
          
    if not os.path.exists(Infolder):
        os.mkdir(Infolder) 
    BatchFileName=Outfolder+'/BatchFile.bat' 
    CSVinput=Infolder+'/'+Filename
    VRTfileNAME=Outfolder+'/dem.vrt'   
    Outputfile=Outfolder+'/'+Filename.replace('csv','tif')
    
    #create .vrt file
    myfilem = open(VRTfileNAME, 'w')
    
    myfilem.write("<OGRVRTDataSource>")
    myfilem.write("\n")
    myfilem.write('    <OGRVRTLayer name='+'"'+Filename.replace('.csv','')+'"'+'>')
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
    strdata='C:/"Program Files"/GDAL/gdal_grid -a_srs EPSG:4269 -a invdist:smoothing:' + str(smoothing) + ':power=' + str(power)+  ':max_points=12 -txe'+' '+str(BoundingBox[0])+' '+str(BoundingBox[1])+ " -tye "+str(BoundingBox[2])+' '+str(BoundingBox[3])+  " -outsize " +str(GridSizeX) +' ' + str(GridSizeY)+ ' -of GTiff -ot Float64 -l '+Filename.replace('.csv','')+' ' +VRTfileNAME+' '+ Outputfile
#    print (strdata)
    myfilem.write(strdata)    
    myfilem.close()    
    subprocess.run(BatchFileName)

###############################################################################
# asc2dssGrid
###############################################################################


def asc2dssGrid(Infile,DssFILE,Variable,StartTime,EndTime, Dunits, Dtype,PartB, PartF):
    """
    This Function gets and asc file and converts it to dss format
    #### Input:
    1. Infile: Path of asc file
    2. DssFile: Path of DSS file
    3. Variable: could be rainfall, stream flow , ...
    4. StartTime: Start time of asc file
    5. EndTime: End time of asc file   !!! NOTE: DSS end time don't accept 00:00 as a time, it should be 24:00!
    6. Dunits: it could be In, mm, degF (Fahrenhit), ....
    7. Dtype: 0(PER-AVER), 1(PER-CUM) or 2(INST-VAL)
    8. PartB
    9. PartF
    #### Output:
    1. DSS file generated from asc file
    """
    import subprocess
    BatchFileName='//westfolsom/Office/Python/DSS_Utility_exe_for_Python_Functions/Ascii2grid2.bat'
    asc2dssGridExe='//westfolsom/Office/Python/DSS_Utility_exe_for_Python_Functions/asc2dssGrid.exe'
    myfilem = open(BatchFileName, 'w')         
    if(Dtype==1): strcom=asc2dssGridExe+' in='+ Infile+' dss='+DssFILE+' path=/SHG/'+PartB+'/'+Variable+'/'+StartTime+'/'+EndTime+'/'+PartF+'/ GRIDTYPE=SHG DUNITS='+Dunits+' DTYPE='+str(Dtype)
    if(Dtype==2): strcom=asc2dssGridExe+' in='+ Infile+' dss='+DssFILE+' path=/SHG/'+PartB+'/'+Variable+'/'+StartTime+'//'+PartF+'/ GRIDTYPE=SHG DUNITS='+Dunits+' DTYPE='+str(Dtype)
    
    
    myfilem.write(strcom)    
    myfilem.close()    
    flag=subprocess.run(BatchFileName, shell=True)
    if(flag==1): 
        print (" Error calling subprocess")
    
##############################################################################
# TiftoDss
##############################################################################
def TiftoDss(Outtif2, dat_beg, MissingValue, DssFILE, Variable,timeDelta, Dunits, Dtype, PartB, PartF):
    """
    This Function gets a tiff file, converts it into an asc format and then into a dss format
    #### Sub Function:
    1. asc2dssGrid
    #### Input:
    1. Outtif2: path to the reprojected tiff file
    2. dat_beg: begining of time  in string - example: '19960226_000000'
    3. MissingValue: the way we want to write Missing value, based on the later use it could be different
    4. DssFILE: Path of DSS file
    5. Variable: Part C in DSS
    6. timeDelta: delta in hours - resolution of the dataset
    7. Dunits: it could be In, mm, degF (Fahrenhit), ....
    8. Dtype: 1(PER-CUM), 2(INST-VAL), 0(PER-AVG)
    9. PartB
    10. PartF
    
    #### Output:
    1. DSS file
    """
#From the new file I need to get ncol, nrows, xllcorner, yllcorner, cellsize
    import numpy as np
    from osgeo import gdal
    from gdal import GA_ReadOnly
    from datetime import timedelta, datetime
    import sys
    from os import path
    flag=1
    
    try: 
        dataset = gdal.Open(Outtif2, GA_ReadOnly)   
        ncolZ = dataset.RasterXSize            
        nrowZ = dataset.RasterYSize
        gfZ = dataset.GetGeoTransform()           
        rb = dataset.GetRasterBand(1)
        aa = rb.ReadAsArray().astype(np.float)                
        cellsize = gfZ[1]
        xllcorner = int(round(gfZ[0]))        
        yllcorner = int(round(gfZ[3]+gfZ[5]*(nrowZ)))
        dataset = None

        aa[np.isnan(aa)] = MissingValue  
        if((Variable=="PRECIP") | (Variable=="precip") | (Variable=="SWE")): aa[aa<0] = MissingValue     
        #######################################################################
        # Given the Reprojected Hourly tiff convert to ASCI
        #######################################################################
        
        header=[]
    
        header.append("ncols "+str(aa.shape[1]))
        header.append("nrows "+str(aa.shape[0]))
        header.append("xllcorner "+str(xllcorner))    
        header.append("yllcorner " +str(yllcorner))
        header.append("cellsize "+str(gfZ[1]))
        header.append("NODATA_value " + str(MissingValue))
        AscFilePrism=Outtif2[0:Outtif2.rfind('/')+1]+dat_beg+'Reproj'+'.asc'
        with open(AscFilePrism, "w") as f:
            for n in range(0,len(header)):
                
                f.write(header[n])
                f.write('\n')
                
            np.savetxt(f, aa, fmt="%1.3f")  
        dat_beg1 = datetime.strptime(dat_beg, '%Y%m%d_%H%M%S')
        PrismdayStart=(dat_beg1).strftime("%d%b%Y:%H%M")
        PrismdayEnd=(dat_beg1 + timedelta(hours=timeDelta)).strftime("%d%b%Y:%H%M") 
# To Change 00:00 to 24:00, DSS don't understand 00:00 for the end of period!
        if PrismdayEnd[-4:] == '0000': 
            list1 = list(PrismdayEnd)
            list1[-4:] = '2400'
            list1[0:5] = PrismdayStart[0:5]
            PrismdayEnd = ''.join(list1)
        if not path.exists(AscFilePrism): print ("Did not run1 "+Outtif2)
        asc2dssGrid(AscFilePrism,DssFILE,Variable,PrismdayStart,PrismdayEnd, Dunits, Dtype, PartB, PartF)
    except:
        print ("Did not run3 "+Outtif2)
        sys.exit()
        flag=-1
    return flag

##############################################################################
# ReadPRISM
##############################################################################
def ReadPRISM(dat,Var,Res):
    """
    This Function gets a PRISM file in bil format, and opens the file and save it in 'img'
    #### Input:
    1. dat: date of the bil file
    2. Var: this could be ppt (precipitation), tmax, tmin or tmean
    3. Res: resolution of PRISM data
    #### Output:
    1. img: this function returns 'img' variable
    """
    from osgeo import gdal
    import os
    datet=(dat).strftime("%Y%m%d")
    yearstr=(dat).strftime("%Y")
    
    
    DataFolder='O:/PRISM/' 
    DataFolder='D:/WESTDataCode/PRISM/'                 
    if(Var=='ppt'):
    
        ZIPFile = DataFolder+'ppt/' + yearstr + '/PRISM_ppt_stable_' +Res+ 'D2_' +datet+ '_bil.zip'
        Filename = DataFolder+'ppt/' + yearstr + '/PRISM_ppt_stable_' +Res+ 'D2_' +datet+ '_bil.zip/PRISM_ppt_stable_' +Res+ 'D2_' + datet +'_bil.bil'
        if not os.path.isfile(ZIPFile):
            ZIPFile = DataFolder+'ppt/' + yearstr + '/PRISM_ppt_early_' +Res+ 'D2_' +datet+ '_bil.zip'
            Filename = DataFolder+'ppt/' + yearstr + '/PRISM_ppt_early_' +Res+ 'D2_' +datet+ '_bil.zip/PRISM_ppt_early_' +Res+ 'D2_' + datet +'_bil.bil'
        if not os.path.isfile(ZIPFile): 
            ZIPFile = DataFolder+'ppt/' + yearstr + '/PRISM_ppt_provisional_' +Res+ 'D2_' +datet+ '_bil.zip'
            Filename = DataFolder+'ppt/' + yearstr + '/PRISM_ppt_provisional_' +Res+ 'D2_' +datet+ '_bil.zip/PRISM_ppt_provisional_' +Res+ 'D2_' + datet +'_bil.bil'
    
        bil = r'/vsizip/' + Filename
        img = gdal.Open(bil)
    
    if(Var=='tmax'):        
        
        ZIPFile = DataFolder+'Temp_4km/tmax/' + yearstr + '/PRISM_tmax_stable_' +Res+ 'D1_' +datet+ '_bil.zip'
        Filename = DataFolder+'Temp_4km/tmax/' + yearstr + '/PRISM_tmax_stable_' +Res+ 'D1_' +datet+ '_bil.zip/PRISM_tmax_stable_' +Res+ 'D1_' + datet +'_bil.bil'
        if not os.path.isfile(ZIPFile): 
            ZIPFile = DataFolder+'Temp_4km/tmax/' + yearstr + '/PRISM_tmax_early_' +Res+ 'D1_' +datet+ '_bil.zip'
            Filename = DataFolder+'Temp_4km/tmax/' + yearstr + '/PRISM_tmax_early_' +Res+ 'D1_' +datet+ '_bil.zip/PRISM_tmax_early_' +Res+ 'D1_' + datet +'_bil.bil'
        if not os.path.isfile(ZIPFile): 
            ZIPFile = DataFolder+'Temp_4km/tmax/' + yearstr + '/PRISM_tmax_provisional_' +Res+ 'D1_' +datet+ '_bil.zip'
            Filename = DataFolder+'Temp_4km/tmax/' + yearstr + '/PRISM_tmax_provisional_' +Res+ 'D1_' +datet+ '_bil.zip/PRISM_tmax_provisional_' +Res+ 'D1_' + datet +'_bil.bil'

        bil = r'/vsizip/' + Filename
        img = gdal.Open(bil)

    
    if(Var=='tmin'):        
        
        ZIPFile = DataFolder+'Temp_4km/tmin/' + yearstr + '/PRISM_tmin_stable_' +Res+ 'D1_' +datet+ '_bil.zip'
        Filename = DataFolder+'Temp_4km/tmin/' + yearstr + '/PRISM_tmin_stable_' +Res+ 'D1_' +datet+ '_bil.zip/PRISM_tmin_stable_' +Res+ 'D1_' + datet +'_bil.bil'
        if not os.path.isfile(ZIPFile): 
            ZIPFile = DataFolder+'Temp_4km/tmin/' + yearstr + '/PRISM_tmin_early_' +Res+ 'D1_' +datet+ '_bil.zip'
            Filename = DataFolder+'Temp_4km/tmin/' + yearstr + '/PRISM_tmin_early_' +Res+ 'D1_' +datet+ '_bil.zip/PRISM_tmin_early_' +Res+ 'D1_' + datet +'_bil.bil'
        if not os.path.isfile(ZIPFile): 
            ZIPFile = DataFolder+'Temp_4km/tmin/' + yearstr + '/PRISM_tmin_provisional_' +Res+ 'D1_' +datet+ '_bil.zip'
            Filename = DataFolder+'Temp_4km/tmin/' + yearstr + '/PRISM_tmin_provisional_' +Res+ 'D1_' +datet+ '_bil.zip/PRISM_tmin_provisional_' +Res+ 'D1_' + datet +'_bil.bil'

        bil = r'/vsizip/' + Filename
        img = gdal.Open(bil)


    if(Var=='tmean'): 
        #Filename = 'C:/Users/lcunha/Documents/PRISM/'+Res+'/daily/tmean/' + yearstr + '/PRISM_tmean_stable_' +Res+ 'D1_' +datet+ '_bil.zip/PRISM_tmean_stable_' +Res+ 'D1_' + datet +'_bil.bil'
        ZIPFile = DataFolder+'Temp_4km/tmean/' + yearstr + '/PRISM_tmean_stable_' +Res+ 'D1_' +datet+ '_bil.zip'
        Filename = DataFolder+'Temp_4km/tmean/' + yearstr + '/PRISM_tmean_stable_' +Res+ 'D1_' +datet+ '_bil.zip/PRISM_tmean_stable_' +Res+ 'D1_' + datet +'_bil.bil'
        if not os.path.isfile(ZIPFile): 
            ZIPFile = DataFolder+'Temp_4km/tmean/' + yearstr + '/PRISM_tmean_early_' +Res+ 'D1_' +datet+ '_bil.zip'
            Filename = DataFolder+'Temp_4km/tmean/' + yearstr + '/PRISM_tmean_early_' +Res+ 'D1_' +datet+ '_bil.zip/PRISM_tmean_early_' +Res+ 'D1_' + datet +'_bil.bil'
        if not os.path.isfile(ZIPFile): 
            ZIPFile = DataFolder+'Temp_4km/tmean/' + yearstr + '/PRISM_tmean_provisional_' +Res+ 'D1_' +datet+ '_bil.zip'
            Filename = DataFolder+'Temp_4km/tmean/' + yearstr + '/PRISM_tmean_provisional_' +Res+ 'D1_' +datet+ '_bil.zip/PRISM_tmean_provisional_' +Res+ 'D1_' + datet +'_bil.bil'

        bil = r'/vsizip/' + Filename
        img = gdal.Open(bil)
#        plt.imshow(img)
    return img 


##############################################################################
# ReadPRISMMonth
##############################################################################        
def ReadPRISMMonth(iy,im,Var,Res):
    """
    This Function gets a PRISM file in bil format, and opens the file and save it in 'img'
    #### Input:
    1. iy: year of the bil file
    2. im: month of the bil file
    2. Var: this could be ppt (precipitation), tmax, tmin or tmean
    3. Res: resolution of PRISM data ('4km')
    #### Output:
    1. img: this function returns 'img' variable
    """
    from osgeo import gdal
    import os
    datet=str(iy)+'{0:02d}'.format(im)
    yearstr=str(iy)
    
    
    DataFolder='O:/PRISM/monthly/'  
                
    ZIPFile = DataFolder+Var+'/' + yearstr + '/PRISM_'+Var+'_stable_' +Res+ 'M2_' +yearstr+ '_all_bil.zip'
    Filename = ZIPFile+'/PRISM_'+Var+'_stable_' +Res+ 'M2_' + datet +'_bil.bil'
    if not os.path.isfile(ZIPFile): 
        ZIPFile = DataFolder+Var+'/' + yearstr + '/PRISM_'+Var+'_stable_' +Res+ 'M3_' +yearstr+ '_all_bil.zip'
        Filename = ZIPFile+'/PRISM_'+Var+'_stable_' +Res+ 'M3_' + datet +'_bil.bil'
    if not os.path.isfile(ZIPFile): 
        ZIPFile = DataFolder+Var+'/' + yearstr + '/PRISM_'+Var+'_provisional_' +Res+ 'M3_' +datet+ '_bil.zip'
        Filename = ZIPFile+'/PRISM_'+Var+'_provisional_' +Res+ 'M3_' + datet +'_bil.bil'
    if not os.path.isfile(ZIPFile): 
        ZIPFile = DataFolder+Var+'/' + yearstr + '/PRISM_'+Var+'_stable_' +Res+ 'M1_' +datet+ '_bil.zip'
        Filename = ZIPFile+'/PRISM_'+Var+'_stable_' +Res+ 'M1_' + datet +'_bil.bil'
    if not os.path.isfile(ZIPFile): 
        ZIPFile = DataFolder+Var+'/' + yearstr + '/PRISM_'+Var+'_stable_' +Res+ 'M3_' +datet+ '_bil.zip'
        Filename = ZIPFile+'/PRISM_'+Var+'_stable_' +Res+ 'M3_' + datet +'_bil.bil'
    if not os.path.isfile(ZIPFile): 
        ZIPFile = DataFolder+Var+'/' + yearstr + '/PRISM_'+Var+'_stable_' +Res+ 'M2_' +datet+ '_bil.zip'
        Filename = ZIPFile+'/PRISM_'+Var+'_stable_' +Res+ 'M2_' + datet +'_bil.bil'
    if not os.path.isfile(ZIPFile): 
        ZIPFile = DataFolder+Var+'/' + yearstr + '/PRISM_'+Var+'_provisional_' +Res+ 'M2_' +datet+ '_bil.zip'
        Filename = ZIPFile+'/PRISM_'+Var+'_provisional_' +Res+ 'M2_' + datet +'_bil.bil'
        
        
    bil = r'/vsizip/' + Filename
    img = gdal.Open(bil)

    return img     

##############################################################################
# ReadPRISMMonth
##############################################################################        
def ReadPRISMYear(iy,Var,Res):
    """
    This Function gets a PRISM file in bil format, and opens the file and save it in 'img'
    #### Input:
    1. dat: date of the bil file
    2. Var: this could be ppt (precipitation), tmax, tmin or tmean
    3. Res: resolution of PRISM data
    #### Output:
    1. img: this function returns 'img' variable
    """
    from osgeo import gdal
    import os
    yearstr=str(iy)
    
    
    DataFolder='O:/PRISM/monthly/'                  
    if(Var=='ppt'):
        
        ZIPFile = DataFolder+'ppt/' + yearstr + '/PRISM_ppt_stable_' +Res+ 'M2_' +yearstr+ '_all_bil.zip'
        Filename = ZIPFile+'/PRISM_ppt_stable_' +Res+ 'M2_' + yearstr +'_bil.bil'
        if not os.path.isfile(ZIPFile): 
            ZIPFile = DataFolder+'ppt/' + yearstr + '/PRISM_ppt_stable_' +Res+ 'M3_' +yearstr+ '_all_bil.zip'
            Filename = ZIPFile+'/PRISM_ppt_stable_' +Res+ 'M3_' + yearstr +'_bil.bil'
        if not os.path.isfile(ZIPFile): 
            ZIPFile = DataFolder+'ppt/' + yearstr + '/PRISM_ppt_provisional_' +Res+ 'M3_' +yearstr+ '_bil.zip'
            Filename = ZIPFile+'/PRISM_ppt_provisional_' +Res+ 'M3_' + yearstr +'_bil.bil'
    
        bil = r'/vsizip/' + Filename
        img = gdal.Open(bil)
    else: "Please modify the code for the other variables"

    return img     
##############################################################################
# CreateMatrixFileFloat
##############################################################################       
def CreateMatrixFileFloat(FileName,matrixBasin,ncol, nrow,geotransform,ProjSys):
    from osgeo import gdal
    import numpy as np
#    import BasicFunction as BF  
    from osgeo import gdal, osr
    from osgeo import ogr              
        # Extract data block
    driver = gdal.GetDriverByName('GTiff')

    dst_ds = driver.Create( FileName, int(ncol), int(nrow), int(1), gdal.GDT_Float64 )    
    #print (geotransform)
    dst_ds.SetGeoTransform( geotransform )  
    # if(len(ProjSys)>1):  
    dst_ds.SetProjection( ProjSys )
    # else:
    #     srs = osr.SpatialReference()
    #     srs.SetWellKnownGeogCS( 'NAD83' )
    #     dst_ds.SetProjection(srs)
    
    
    dst_ds.GetRasterBand(1).WriteArray( matrixBasin )

    dst_ds = None    

###############################################################################
# dss2ascGrid
###############################################################################

def dss2ascGrid(Infile, AscFILE, PartA, PartB, PartC, StartTime, EndTime, PartF, Units, Dtype):
    """
    This Function gets a DSS file and converts it to ASC format
    #### Input:
    1. Infile: Path of the DSS file
    2. AscFile: Path of the ASC file
    3. PartA: part A of the DSS file
    4. PartB: part B of the DSS file
    5. PartC: Part C of the DSS file
    6. StartTime: Start time of DSS file (format example: 01APR2019:0100)
    7. EndTime: End time of DSS file   !!! NOTE: DSS end time don't accept 00:00 as a time, it should be 24:00!
    8. PartF: part F of DSS file
    9. Units: DSS unit
    10. Dtype: 1(PER-CUM), 2(INST-VAL), 0(PER-AVG)
    #### Output:
    1. ASC file generated from DSS file
    """
    import subprocess
    import shutil
    BatchFileName='//westfolsom/Office/Python/WEST_Python_FunctionAug2019/dss2ascGrid.bat'
    dss2ascGridExe='//westfolsom/Office/Python/WEST_Python_FunctionAug2019/dss2ascGrid.exe'
    myfilem = open(BatchFileName, 'w')           
    myfilem.write(dss2ascGridExe+ ' DSS='+Infile+ ' PATH=/'+PartA+'/'+PartB+'/'+PartC+'/'+StartTime+'/'+EndTime+'/'+PartF+'/ OUTPUT='+AscFILE+' PREC='+ Dtype)    
    myfilem.close()    
    flag = subprocess.run(BatchFileName, shell=True)
    if (flag==4294967295):
        print("Error calling subprocess_dsstoasc")
        asc_na = '//westfolsom/projects/2019/UmpquaRiver/Newfolder/NA.asc'
        shutil.copy2(asc_na, AscFILE)
    
###############################################################################
# PlotLinearRelationship
###############################################################################    
def PlotLinearRelationship(x,y,labelx,labely,Outplot):
    import numpy as np
    import matplotlib.pyplot as plt 
    from scipy import stats    
    font = {'family' : 'normal','size'   : 12}

    plt.rc('font', **font)

    plt.plot(x,y,'o', alpha=0.5)

    LinearReg=stats.linregress(x,y)   

    Slope=LinearReg[0]
    Interc=LinearReg[1]
    rvalue=LinearReg[2]    
    pvalue=LinearReg[3]
    predict_y = Interc + Slope * np.array(x)
    
    plt.plot(x,predict_y,'-', lw=2, color='red')
    
    plt.xlabel(labelx)
    plt.ylabel(labely)
    
    strtitle='Correl=' + str(round(rvalue,2))+ '; pvalue=' + str(round(pvalue,2)) +'; Slope=' + str(round(Slope,3))
    plt.grid(True)
    plt.title(strtitle, fontsize=14)
    
    plt.savefig(Outplot)
    plt.close()
    
    
    return pvalue, Slope, Interc

###############################################################################
#PlotLinearRelationshipMR
###############################################################################
def PlotLinearRelationshipMR(x,y,labelx,labely,Outplot):
    import numpy as np
    import matplotlib.pyplot as plt 
    from scipy import stats
    font = {'family' : 'DejaVu Sans','size'   : 12}

    plt.rc('font', **font)

    plt.plot(x,y,'o', alpha=0.5)
    
    LinearReg=stats.linregress(x,y)   

    Slope=LinearReg[0]
    Interc=LinearReg[1]
    rvalue=LinearReg[2]    
    pvalue=LinearReg[3]
    predict_y = Interc + Slope * np.array(x)
    
    plt.plot(x,predict_y,'-', lw=2, color='red')
    
    plt.xlabel(labelx)
    plt.ylabel(labely)
       
    strtitle='Correl=' + str(round(rvalue,2))+ '; pvalue=' + str(round(pvalue,2)) +'; Slope=' + str(round(Slope,5))

    plt.title(strtitle, fontsize=14)
    
    plt.savefig(Outplot)
    plt.close()
    
    
    return pvalue, Slope, Interc
###############################################################################
# PlotLinearRelationshipMA
###############################################################################
def PlotLinearRelationshipMA(x,y,y2,y3,labelx,labely,Outplot):
    #.PlotLinearRelationshipMR(df['Date'], df['VALUE'], df['SWE_MA10'],df['SWE_MA30'],labelx,labely, legend1, legend2, legend3 ,Outplot)
    import numpy as np
    import matplotlib.pyplot as plt 
    from scipy import stats
    font = {'family' : 'DejaVu Sans','size'   : 12}

    plt.rc('font', **font)

    plt.plot(x,y,'o', color='blue', alpha=0.5)
    plt.plot(x,y2, '-', color='green')
    plt.plot(x,y3, '-', color='blue')

    LinearReg=stats.linregress(x,y)   

    Slope=LinearReg[0]
    Interc=LinearReg[1]
    rvalue=LinearReg[2]    
    pvalue=LinearReg[3]
    predict_y = Interc + Slope * np.array(x)
    
    plt.plot(x,predict_y,'-', lw=2, color='red')
    
    plt.legend(['SWE', 'SWE10', 'SWE30'])
    plt.xlabel(labelx)
    plt.ylabel(labely)
         
    strtitle='Correl=' + str(round(rvalue,2))+ '; pvalue=' + str(round(pvalue,2)) +'; Slope=' + str(round(Slope,5))

    plt.title(strtitle, fontsize=14)
    
    plt.savefig(Outplot)
    plt.close()
    
    return pvalue, Slope, Interc
###############################################################################
# PlotLinearRelationship
###############################################################################    
def PlotLinearRelationship_LO(x1,y1,x2,y2,x3,y3,labelx,labely,Outplot): #
    import numpy as np
    import matplotlib.pyplot as plt 
    from scipy import stats    
    import math
    font = {'family' : 'normal','size'   : 12}

    plt.rc('font', **font)

    plt.plot(x1,y1,'o', alpha=1, color='red')
    plt.plot(x2,y2,'o', alpha=1, color='yellow')
    plt.plot(x3,y3,'o', alpha=1, color='blue')

    LinearReg1=stats.linregress(x1,y1) 
    LinearReg2=stats.linregress(x2,y2)  
    LinearReg3=stats.linregress(x3,y3)  

    Slope1=LinearReg1[0]
    Interc1=LinearReg1[1]
    rvalue1=LinearReg1[2]    
    pvalue1=LinearReg1[3]
    predict_y1 = Interc1 + Slope1 * np.array(x1)
    
    Slope2=LinearReg2[0]
    Interc2=LinearReg2[1]
    rvalue2=LinearReg2[2]    
    pvalue2=LinearReg2[3]
    predict_y2 = Interc2 + Slope2 * np.array(x2)
    
    Slope3=LinearReg3[0]
    Interc3=LinearReg3[1]
    rvalue3=LinearReg3[2]    
    pvalue3=LinearReg3[3]
    predict_y3 = Interc3 + Slope3 * np.array(x3)
    
    # plt.plot(x1,predict_y1,'-', lw=2, color='red')
    # plt.plot(x2,predict_y2,'-', lw=2, color='yellow')
    plt.plot(x3,predict_y3,'-', lw=2, color='blue')
    
    plt.xlabel(labelx)
    plt.ylabel(labely)
    
    x_minimum = math.floor(min([x1.min(),x2.min(),x3.min()]))
    x_maximum = math.ceil(max([x1.max(),x2.max(),x3.max()]))
        
    if len(x1) >= 15 :
        plt.xticks(np.arange(5*math.floor(x_minimum/5), 5*math.ceil(x_maximum/5)+5, 5))
        plt.xlim(x_minimum-2, x_maximum+2)
    else :
        plt.xticks(np.arange(2*math.floor(x_minimum/2), 2*math.ceil(x_maximum/2), 2))
        plt.xlim(x_minimum-1, x_maximum+1)
    
    strtitle='Correl=' + str(round(rvalue3,2))+ '; pvalue=' + str(round(pvalue3,2)) +'; Slope=' + str(round(Slope3,3))

    plt.title(strtitle, fontsize=14)
    
    plt.savefig(Outplot)
    plt.close()
    
    return pvalue3, Slope3, Interc3
    # return pvalue1, Slope1, Interc1, pvalue2, Slope2, Interc2, pvalue3, Slope3, Interc3

###############################################################################
# PlotLinearRelationship
###############################################################################    
def PlotLinearRelationship_LO3(x1,y1,x2,y2,x3,y3,labelx,labely,ylimtop,c100,q100,Outplot): #
    import numpy as np
    import matplotlib.pyplot as plt 
    from scipy import stats    
    import math
    font = {'family' : 'normal','size'   : 12}

    plt.rc('font', **font)

    plt.plot(x1,y1,'o', alpha=1, color='red')
    plt.plot(x2,y2,'o', alpha=1, color='yellow')
    plt.plot(x3,y3,'o', alpha=1, color='blue')

    LinearReg3=stats.linregress(x3,y3)  

    Slope3=LinearReg3[0]
    Interc3=LinearReg3[1]
    pvalue3=LinearReg3[3]
    predict_y3 = Interc3 + Slope3 * np.array(x3)
    
    # plt.plot(x1,predict_y1,'-', lw=2, color='red')
    # plt.plot(x2,predict_y2,'-', lw=2, color='yellow')
    plt.plot(x3,predict_y3,'-', lw=1.5, color='blue')
    plt.plot([1988, 2021],[q100,q100],'-', lw=2, color='green')
    plt.plot([1988, 2021],[c100,c100],'-', lw=2, color='black')
    
    plt.xlabel(labelx)
    plt.ylabel(labely)
    
    # x_minimum = math.floor(min([x1.min(),x2.min(),x3.min()]))
    # x_maximum = math.ceil(max([x1.max(),x2.max(),x3.max()]))
        
    # if len(x1) >= 15 :
    #     plt.xticks(np.arange(5*math.floor(x_minimum/5), 5*math.ceil(x_maximum/5)+5, 5))
    #     plt.xlim(x_minimum-2, x_maximum+2)
    # else :
    #     plt.xticks(np.arange(2*math.floor(x_minimum/2), 2*math.ceil(x_maximum/2), 2))
    #     plt.xlim(x_minimum-1, x_maximum+1)
    
    plt.xticks(np.arange(5*math.floor(1988/5), 5*math.ceil(2021/5)+5, 5))
    plt.xlim(1988, 2021)
    plt.ylim(0-0.05*ylimtop, ylimtop+0.05*ylimtop)
    
    strtitle='County =' + str(round(c100,2))+ '; Ours =' + str(round(q100,2)) 

    plt.title(strtitle, fontsize=14)
    
    plt.savefig(Outplot)
    plt.close()
    
    return pvalue3, Slope3, Interc3
    # return pvalue1, Slope1, Interc1, pvalue2, Slope2, Interc2, pvalue3, Slope3, Interc3


###############################################################################
# PlotLinearRelationship
###############################################################################    
def PlotLinearRelationship_LO2(x1,y1,x2,y2,x3,y3,labelx,labely,ylimtop,Outplot): #
    import numpy as np
    import matplotlib.pyplot as plt 
    from scipy import stats    
    import math
    font = {'family' : 'normal','size'   : 12}

    plt.rc('font', **font)

    plt.plot(x1,y1,'o', alpha=1, color='red')
    plt.plot(x2,y2,'o', alpha=1, color='yellow')
    plt.plot(x3,y3,'o', alpha=1, color='blue')

    LinearReg3=stats.linregress(x3,y3)  

    Slope3=LinearReg3[0]
    Interc3=LinearReg3[1]
    rvalue3=LinearReg3[2]    
    pvalue3=LinearReg3[3]
    predict_y3 = Interc3 + Slope3 * np.array(x3)
    
    # plt.plot(x1,predict_y1,'-', lw=2, color='red')
    # plt.plot(x2,predict_y2,'-', lw=2, color='yellow')
    plt.plot(x3,predict_y3,'-', lw=2, color='blue')
    
    plt.xlabel(labelx)
    plt.ylabel(labely)
    
    # x_minimum = math.floor(min([x1.min(),x2.min(),x3.min()]))
    # x_maximum = math.ceil(max([x1.max(),x2.max(),x3.max()]))
        
    # if len(x1) >= 15 :
    #     plt.xticks(np.arange(5*math.floor(x_minimum/5), 5*math.ceil(x_maximum/5)+5, 5))
    #     plt.xlim(x_minimum-2, x_maximum+2)
    # else :
    #     plt.xticks(np.arange(2*math.floor(x_minimum/2), 2*math.ceil(x_maximum/2), 2))
    #     plt.xlim(x_minimum-1, x_maximum+1)
    
    plt.xticks(np.arange(5*math.floor(1988/5), 5*math.ceil(2021/5)+5, 5))
    plt.xlim(1988, 2021)
    plt.ylim(0-0.05*ylimtop, ylimtop+0.05*ylimtop)
        
    plt.savefig(Outplot)
    plt.close()
    
    return pvalue3, Slope3, Interc3
    # return pvalue1, Slope1, Interc1, pvalue2, Slope2, Interc2, pvalue3, Slope3, Interc3

###############################################################################
# PlotLinearRelationship
###############################################################################    
def PlotLinearRelationship_LO(x1,y1,x2,y2,x3,y3,labelx,labely,Outplot): #
    import numpy as np
    import matplotlib.pyplot as plt 
    from scipy import stats    
    import math
    font = {'family' : 'normal','size'   : 12}

    plt.rc('font', **font)

    plt.plot(x1,y1,'o', alpha=1, color='red')
    plt.plot(x2,y2,'o', alpha=1, color='yellow')
    plt.plot(x3,y3,'o', alpha=1, color='blue')

    LinearReg1=stats.linregress(x1,y1) 
    LinearReg2=stats.linregress(x2,y2)  
    LinearReg3=stats.linregress(x3,y3)  

    Slope1=LinearReg1[0]
    Interc1=LinearReg1[1]
    rvalue1=LinearReg1[2]    
    pvalue1=LinearReg1[3]
    predict_y1 = Interc1 + Slope1 * np.array(x1)
    
    Slope2=LinearReg2[0]
    Interc2=LinearReg2[1]
    rvalue2=LinearReg2[2]    
    pvalue2=LinearReg2[3]
    predict_y2 = Interc2 + Slope2 * np.array(x2)
    
    Slope3=LinearReg3[0]
    Interc3=LinearReg3[1]
    rvalue3=LinearReg3[2]    
    pvalue3=LinearReg3[3]
    predict_y3 = Interc3 + Slope3 * np.array(x3)
    
    # plt.plot(x1,predict_y1,'-', lw=2, color='red')
    # plt.plot(x2,predict_y2,'-', lw=2, color='yellow')
    plt.plot(x3,predict_y3,'-', lw=2, color='blue')
    
    plt.xlabel(labelx)
    plt.ylabel(labely)
    
    x_minimum = math.floor(min([x1.min(),x2.min(),x3.min()]))
    x_maximum = math.ceil(max([x1.max(),x2.max(),x3.max()]))
        
    if len(x1) >= 15 :
        plt.xticks(np.arange(5*math.floor(x_minimum/5), 5*math.ceil(x_maximum/5)+5, 5))
        plt.xlim(x_minimum-2, x_maximum+2)
    else :
        plt.xticks(np.arange(2*math.floor(x_minimum/2), 2*math.ceil(x_maximum/2), 2))
        plt.xlim(x_minimum-1, x_maximum+1)
    
    strtitle='Correl=' + str(round(rvalue3,2))+ '; pvalue=' + str(round(pvalue3,2)) +'; Slope=' + str(round(Slope3,3))

    plt.title(strtitle, fontsize=14)
    
    plt.savefig(Outplot)
    plt.close()
    
    return pvalue3, Slope3, Interc3
    # return pvalue1, Slope1, Interc1, pvalue2, Slope2, Interc2, pvalue3, Slope3, Interc3
###############################################################################
# Download data from ftp area
###############################################################################    

# overriding requests.Session.rebuild_auth to mantain headers when redirected
def GetNLDASSec_py3(FTPAddress,InDirectory,InFileName,OutputFileName): 
    import requests # get the requsts library from https://github.com/requests/requests
# overriding requests.Session.rebuild_auth to mantain headers when redirected
 
    class SessionWithHeaderRedirection(requests.Session):     
        AUTH_HOST = 'urs.earthdata.nasa.gov'     
        def __init__(self, username, password):     
            super().__init__()     
            self.auth = (username, password)
     
       # Overrides from the library to keep headers when redirected to or from     
       # the NASA auth host.
     
        def rebuild_auth(self, prepared_request, response):     
            headers = prepared_request.headers     
            url = prepared_request.url                
            if 'Authorization' in headers:
     
                original_parsed = requests.utils.urlparse(response.request.url)     
                redirect_parsed = requests.utils.urlparse(url)
     
                if (original_parsed.hostname != redirect_parsed.hostname) and (redirect_parsed.hostname != self.AUTH_HOST) and (original_parsed.hostname != self.AUTH_HOST):     
                    del headers['Authorization']
            return
          
    # create session with the user credentials that will be used to authenticate access to the data
     
    username='lcunha'
    password='Lkcunha6393*'
     
    session = SessionWithHeaderRedirection(username, password)
    # the url of the file we wish to retrieve     
    url=FTPAddress+InDirectory+InFileName 
    #url = "http://e4ftl01.cr.usgs.gov/MOLA/MYD17A3H.006/2009.01.01/MYD17A3H.A2009001.h12v05.006.2015198130546.hdf.xml"
    # extract the filename from the url to be used when saving the file

    try:     
        # submit the request using the session     
        response = session.get(url, stream=True)     
        #print(response.status_code)
        # raise an exception in case of http errors     
        response.raise_for_status()  
        # save the file

        with open(OutputFileName, "wb") as fd:
            for chunk in response.iter_content(chunk_size=1024*1024):     
                fd.write(chunk)            
     
    except requests.exceptions.HTTPError as e:     
        # handle any errors here     
        print(e)
        

def GetNLDASSec_py3_Aug172020(FTPAddress,InDirectory,InFileName,OutputFileName): 
    # Set the URL string to point to a specific data URL. Some generic examples are:
    #   https://servername/data/path/file
    #   https://servername/opendap/path/file[.format[?subset]]
    #   https://servername/daac-bin/OTF/HTTP_services.cgi?KEYWORD=value[&KEYWORD=value]
    #URL = 'https://hydro1.sci.gsfc.nasa.gov/data/NLDAS/NLDAS_NOAH0125_H.002/1991/335/'
    URL=FTPAddress+InDirectory+InFileName 
    # Set the FILENAME string to the data file name, the LABEL keyword value, or any customized name. 
    #FILENAME = InFileName
    
    import requests
    result = requests.get(URL)
    print (URL)
    try:
       result.raise_for_status()
       f = open(OutputFileName,'wb')
       f.write(result.content)
       f.close()
       print('contents of URL written to '+OutputFileName)
    except:
       print('requests.get() returned an error code '+str(result.status_code))
   
###############################################################################
# Download data from http area - AORC
###############################################################################    

def GetAORC(FTPAddress,InDirectory,InFileName,OutputFileName): 
    import requests # get the requsts library from https://github.com/requests/requests
# overriding requests.Session.rebuild_auth to mantain headers when redirected
 
    class SessionWithHeaderRedirection(requests.Session):     
        AUTH_HOST = 'hydrology.nws.noaa.gov'     
        def __init__(self, username, password):     
            super().__init__()     
            self.auth = (username, password)
     
       # Overrides from the library to keep headers when redirected to or from     
       # the NASA auth host.
     
        def rebuild_auth(self, prepared_request, response):     
            headers = prepared_request.headers     
            url = prepared_request.url                
            if 'Authorization' in headers:
     
                original_parsed = requests.utils.urlparse(response.request.url)     
                redirect_parsed = requests.utils.urlparse(url)
     
                if (original_parsed.hostname != redirect_parsed.hostname) and (redirect_parsed.hostname != self.AUTH_HOST) and (original_parsed.hostname != self.AUTH_HOST):     
                    del headers['Authorization']
            return
          
    # create session with the user credentials that will be used to authenticate access to the data
     
    username='anonymous'
    password='anonymous*'
     
    session = SessionWithHeaderRedirection(username, password)
    # the url of the file we wish to retrieve     
    url=FTPAddress+InDirectory+InFileName 
    #url = "http://e4ftl01.cr.usgs.gov/MOLA/MYD17A3H.006/2009.01.01/MYD17A3H.A2009001.h12v05.006.2015198130546.hdf.xml"
    # extract the filename from the url to be used when saving the file

    try:     
        # submit the request using the session     
        response = session.get(url, stream=True)     
        #print(response.status_code)
        # raise an exception in case of http errors     
        response.raise_for_status()  
        # save the file

        with open(OutputFileName, "wb") as fd:
            for chunk in response.iter_content(chunk_size=1024*1024):     
                fd.write(chunk)            
     
    except requests.exceptions.HTTPError as e:     
        # handle any errors here     
        print(e)

###########################################################################################
## GribBandtoNParray
###########################################################################################         
#def GribBandtoNParray(GribFile,BoundingBos,OutFile,BAND,Conversion,ConversionAdd):
#    from osgeo import gdal
#    from osgeo import ogr
#    import numpy as np
#    import subprocess
##GribFile=OutputFileName
##OutFile=Tiffname
#
#    dataset = gdal.Open(GribFile) 
#    ncol=dataset.RasterXSize 
#    nrow=dataset.RasterYSize
#    Proj=dataset.GetProjection()
#    gf = dataset.GetGeoTransform()
#    leftx=gf[0]
#    uppery=gf[3]
#    resdegrx=gf[1]
#    resdegry=gf[5]
#    gt=dataset.GetGeoTransform()
#    
#    px = (np.array(BoundingBos[2] - gt[0]) / gt[1]).astype(int) #x pixel
#    py = (np.array(BoundingBos[0]  - gt[3]) / gt[5]).astype(int)  #y pixel
#    px2 = (np.array(BoundingBos[3] - gt[0]) / gt[1]).astype(int) #x pixel
#    py2 = (np.array(BoundingBos[1]  - gt[3]) / gt[5]).astype(int)  #y pixel
#    
#    band_metadata=[]
#    band_level=[]
#    band_variable=[]
#    band_comments=[]
#    
#    for id in range(1,dataset.RasterCount + 1):
#            j=id-1
#            band = dataset.GetRasterBand(id)
#            metadata = band.GetMetadata()
#            band_metadata.append(metadata)
#            band_comments.append(metadata['GRIB_COMMENT'])
#            band_level.append(metadata['GRIB_SHORT_NAME'])
#            band_variable.append(metadata['GRIB_ELEMENT'])
#    
#    rb=dataset.GetRasterBand(BAND)
#    aa=rb.ReadAsArray(int(px),int(py2),int(px2-px),int(py-py2)).astype(np.float)*Conversion+ConversionAdd
#    aa[aa>300]=0
#    BoundingBox=np.zeros(4)
#    BoundingBox[0]=BoundingBos[0]
#    BoundingBox[2]=gt[0]+px*gt[1]+gt[1]/2
#    BoundingBox[1]=gt[3]+py2*gt[5]+gt[5]/2
#    BoundingBox[3]=BoundingBos[3]
#    
#    gf=(BoundingBox[2],gf[1],gf[2],BoundingBox[1],gf[4],gf[5])   
#    CreateMatrixFileFloat(OutFile,aa,px2-px, py-py2,gf,Proj)
#    subprocess.call('gdalwarp -overwrite -t_srs EPSG:4269 -tr 0.041666667 0.041666667 -of GTiff ' + OutFile + ' ' +OutFile.replace('.tif','ReProj.tif'),shell=True)
#    
#    dataset=None
#    return aa


def CreateMaskFromShapefile(ShapeFile,RasterFile,geotransform,ProjSys,nrow,ncol,resdegr, leftx, uppery):
    from osgeo import gdal, osr
    from osgeo import ogr
    from osgeo import gdal
    import numpy as np
    #from osgeo import gdalconst
    #from osgeo import gdal, osr
    #from osgeo import ogr


    source_ds = ogr.Open(ShapeFile)
    source_layer = source_ds.GetLayer()

    driver = gdal.GetDriverByName('GTiff')
    
    target_ds = driver.Create(RasterFile, int(ncol), int(nrow), 1, gdal.GDT_Float32 )    
    target_ds.SetGeoTransform(geotransform)       
    srs = osr.SpatialReference()
    #srs.SetWellKnownGeogCS( 'NAD83' )
    target_ds.SetProjection( ProjSys.ExportToWkt() )
    
    #gdal.RasterizeLayer(target_ds, [1], source_layer, None, None, burn_values=[1], ['ALL_TOUCHED=TRUE'])
    gdal.RasterizeLayer(target_ds, [1], source_layer, None, None, [1], ['ALL_TOUCHED=TRUE'])
    target_ds = None
    return
    
def CreateMaskFromShapefileID(ShapeFile,feat_ID,RasterFile,geotransform,ProjSys,nrow,ncol,resdegr, leftx, uppery):
    from osgeo import gdal, osr
    from osgeo import ogr
    from osgeo import gdal
    import numpy as np
    #from osgeo import gdalconst
    #from osgeo import gdal, osr
    #from osgeo import ogr
    source_ds = ogr.Open(ShapeFile)
    source_layer = source_ds.GetLayer()

    driver = gdal.GetDriverByName('GTiff')
    
    target_ds = driver.Create(RasterFile, int(ncol), int(nrow), 1, gdal.GDT_Float32 )    
    target_ds.SetGeoTransform(geotransform)       
    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS( 'NAD83' )
    target_ds.SetProjection( ProjSys )
    
    #gdal.RasterizeLayer(target_ds, [1], source_layer, None, None, burn_values=[1], ['ALL_TOUCHED=TRUE'])
    gdal.RasterizeLayer(target_ds, [1], source_layer, None, None, [1], ['ALL_TOUCHED=TRUE'])
    target_ds = None
    return

##########################################################################################
# CreateMask
########################################################################################## 
def CreateMask(OriFile,nrow,ncol,resdegr, leftx, uppery):

    from osgeo import gdal
    import numpy as np
    import sys
    #sys.path.append("O:/Python/WEST_Python_FunctionAug2019/")
    #import BasicFunction_py3 as BF   

    #from osgeo import gdalconst
    #from osgeo import gdal, osr
    #from osgeo import ogr
    
    MatrixBA = gdal.Open(OriFile)
    ncolBa=MatrixBA.RasterXSize 
    nrowBa=MatrixBA.RasterYSize 
    #Proj=MatrixBA.GetProjection()
    geobasin = MatrixBA.GetGeoTransform()
    leftxBa=geobasin[0]
    upperyBa=geobasin[3]
    resdegrBa=geobasin[1]
    band = MatrixBA.GetRasterBand(1)
    DrainMatrix = band.ReadAsArray()
    matrixBasin=np.zeros((nrow,ncol), dtype=np.int)
    for ir in range(0,nrowBa):

        for ic in range(0,ncolBa):
            if(DrainMatrix[ir,ic]==1):
                LatP=upperyBa-(ir*resdegrBa)-resdegrBa/2
                LongP=leftxBa+(ic*resdegrBa)+resdegrBa/2
                row,col=map_to_pixel(LongP, LatP, resdegr, resdegr, leftx, uppery)
                matrixBasin[row,col]=matrixBasin[row,col]+1
    return matrixBasin   

def CreateMaskMatrix(DrainMatrix,geobasin,nrow,ncol,resdegr, leftx, uppery):

    from osgeo import gdal
    import numpy as np

    #from osgeo import gdalconst
    #from osgeo import gdal, osr
    #from osgeo import ogr
    
    #MatrixBA = gdal.Open(GOutfile)
    ncolBa=len(DrainMatrix[0])
    nrowBa=len(DrainMatrix)
    #Proj=MatrixBA.GetProjection()
    #geobasin = MatrixBA.GetGeoTransform()
    leftxBa=geobasin[0]
    upperyBa=geobasin[3]
    resdegrBa=geobasin[1]
    #band = MatrixBA.GetRasterBand(1)
    #DrainMatrix = band.ReadAsArray()
    matrixBasin=np.zeros((nrow,ncol), dtype=np.int)
    for ir in range(0,nrowBa):

        for ic in range(0,ncolBa):
            if(DrainMatrix[ir,ic]==1):
                LatP=upperyBa-(ir*resdegrBa)-resdegrBa/2
                LongP=leftxBa+(ic*resdegrBa)+resdegrBa/2
                row,col=map_to_pixel(LongP, LatP, resdegr, resdegr, leftx, uppery)
                matrixBasin[row,col]=matrixBasin[row,col]+1
    return matrixBasin           
    
##########################################################################################
# map_to_pixel
########################################################################################## 
def map_to_pixel(point_x, point_y, cellx, celly, xmin, ymax):
    col = int((point_x - xmin) / cellx)
    row = int((point_y - ymax) / -celly)
    return row,col


##########################################################################################
# ncdump
########################################################################################## 
def ncdump(nc_fid, verb=True):
    '''
    ncdump outputs dimensions, variables and their attribute information.
    The information is similar to that of NCAR's ncdump utility.
    ncdump requires a valid instance of Dataset.

    Parameters
    ----------
    nc_fid : netCDF4.Dataset
        A netCDF4 dateset object
    verb : Boolean
        whether or not nc_attrs, nc_dims, and nc_vars are printed

    Returns
    -------
    nc_attrs : list
        A Python list of the NetCDF file global attributes
    nc_dims : list
        A Python list of the NetCDF file dimensions
    nc_vars : list
        A Python list of the NetCDF file variables
    '''
    def print_ncattr(key):
        """
        Prints the NetCDF file attributes for a given key

        Parameters
        ----------
        key : unicode
            a valid netCDF4.Dataset.variables key
        """
        try:
            print ("\t\ttype:", repr(nc_fid.variables[key].dtype))
            for ncattr in nc_fid.variables[key].ncattrs():
                print ('\t\t%s:' % ncattr,\
                      repr(nc_fid.variables[key].getncattr(ncattr)))
        except KeyError:
            print ("\t\tWARNING: %s does not contain variable attributes" % key)

    # NetCDF global attributes
    nc_attrs = nc_fid.ncattrs()
    if verb:
        #print "NetCDF Global Attributes:"
        for nc_attr in nc_attrs:
            print ('\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr)))
    nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
    # Dimension shape information.
    if verb:
        #print "NetCDF dimension information:"
        for dim in nc_dims:
            #print "\tName:", dim 
            #print "\t\tsize:", len(nc_fid.dimensions[dim])
            print_ncattr(dim)
    # Variable information.
    nc_vars = [var for var in nc_fid.variables]  # list of nc variables
    if verb:
        #print "NetCDF variable information:"
        for var in nc_vars:
            if var not in nc_dims:
                print ('\tName:', var)
                print ("\t\tdimensions:", nc_fid.variables[var].dimensions)
                print ("\t\tsize:", nc_fid.variables[var].size)
                print_ncattr(var)
    return nc_attrs, nc_dims, nc_vars

##########################################################################################
# mk_test
########################################################################################## 
def mk_test(x, alpha = 0.05):
    import numpy as np
    from scipy.stats import norm
    """
    this perform the MK (Mann-Kendall) test to check if there is any trend present in 
    data or not
    
    Input:
        x:   a vector of data
        alpha: significance level
    
    Output:
        trend: tells the trend (increasing, decreasing or no trend)
        h: True (if trend is present) or False (if trend is absence)
        p: p value of the sifnificance test
        z: normalized test statistics 
        
    Examples
    --------
      >>> x = np.random.rand(100)
      >>> trend,h,p,z = mk_test(x,0.05) 
    """
    n = len(x)
    
    # calculate S 
    s = 0
    for k in range(n-1):
        for j in range(k+1,n):
            s += np.sign(x[j] - x[k])
    
    # calculate the unique data
    unique_x = np.unique(x)
    g = len(unique_x)
    
    # calculate the var(s)
    if n == g: # there is no tie
        var_s = (n*(n-1)*(2*n+5))/18
    else: # there are some ties in data
        tp = np.zeros(unique_x.shape)
        for i in range(len(unique_x)):
            tp[i] = sum(unique_x[i] == x)
        var_s = (n*(n-1)*(2*n+5) + np.sum(tp*(tp-1)*(2*tp+5)))/18
    
    if s>0:
        z = (s - 1)/np.sqrt(var_s)
    elif s == 0:
            z = 0
    elif s<0:
        z = (s + 1)/np.sqrt(var_s)
    
    # calculate the p_value
    p = 2*(1-norm.cdf(abs(z))) # two tail test
    h = abs(z) > norm.ppf(1-alpha/2) 
    
    if (z<0) and h:
        trend = 'decreasing'
    elif (z>0) and h:
        trend = 'increasing'
    else:
        trend = 'no trend'
        
    return trend, h, p, z
    
    
##########################################################################################
# CheckStationarity
########################################################################################## 
def CheckStationarity(SiteID,dfValid1,alpha):

    import numpy as np
    import pandas as pd
    from scipy import stats

# Test for independence of annual maxima datagenerate lag series   
    Values=dfValid1   
    LinearReg=stats.linregress(dfValid1.index.year,Values.values)

    Slope=LinearReg[0]
    Interc=LinearReg[1]
    rvalue=LinearReg[2]
    pvalue=LinearReg[3]
    if(pvalue>alpha): LRtrend='no trend'
    else:
        if(Slope>0): LRtrend='increasing'
        else: LRtrend='decreasing'
   
    trend,h,pmk,z =mk_test(Values.values,alpha)   
    
########## Levene test for variance
    if(len(dfValid1)>30):
        sample1=Values[0:int(len(Values)/3+3)]
        sample2=Values[int(len(Values)/3-3):int(2*len(Values)/3+3)]
        sample3=Values[int(2*len(Values)/3-3):int(len(Values))]
        Wv,pv=stats.levene(sample1,sample2,sample3,center='trimmed')

        # if p<0.05 there is a trend in variance
    else:
        Wv,pv=[-9,-9]
        
    NonStatTest=pd.DataFrame([[Slope,rvalue,pvalue,LRtrend,trend,h,pmk,z,Wv,pv]],index=[[SiteID]],columns=['LRSlope','LRrvalue','LRpvalue','LRtrend','MKtrend','MKh','MKpmk','MKz','LeWv','Lepv'])
    return NonStatTest

    
##########################################################################################
# CreateMapSacCounty
########################################################################################## 
def CreateMapSacCounty(lat,lon,Value,Label,BoundaryBox,outfile):
    from mpl_toolkits.basemap import Basemap
    import matplotlib.pyplot as plt
    import numpy as np
    # setup Lambert Conformal basemap.♣
    # set resolution=None to skip processing of boundary datasets.
    m = Basemap(projection='cea',
                resolution=None,llcrnrlat=BoundaryBox[0],urcrnrlat=BoundaryBox[1],urcrnrlon=BoundaryBox[2],llcrnrlon=BoundaryBox[3])
    # draw a land-sea mask for a map background.
    # lakes=True means plot inland lakes with ocean color.
    m.drawlsmask(land_color='white',ocean_color='aqua',lakes=True)
    m.readshapefile('O:/GIS/usa/census/Counties', 'Counties')
    x,y = m(lon.tolist(), lat.tolist())
    
    m.scatter(x,y, c=Value, s=12, cmap='coolwarm',vmin=-.05,vmax=0.05, alpha=0.8)
    #m.scatter(x,y, c=Value, latlon=True, s=8, cmap='coolwarm', alpha=0.5)
    plt.colorbar(label=Label)
    plt.savefig(outfile,bbox_inches='tight')  
    plt.close()     
    plt.show()
    
    
##########################################################################################
# all_indices
##########################################################################################    
def all_indices(value, qlist):
    import numpy as np
    indices = []
    idx = -1
    while True:
        try:
            idx = qlist.index(value, idx+1)
            indices.append(idx)
        except ValueError:
            break
    return indices

# -*- coding: utf-8 -*-
"""
Created on Wed May 10 13:36:58 2017

@author: lcunha
"""

##########################################################################################
# GetNLDASSec
##########################################################################################    
def GetNLDASSec(FTPAddress,InDirectory,InFileName,OutputFileName):
#Need to re-create the function, current function does not work
    
#https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+Python
#https://disc.gsfc.nasa.gov/data-access#python
#username = "lcunha"
#password= "Lkcunha6393*"    
    print("Use function BF.GetNLDASSec_py3(FTPAddress,InDirectory,InFileName,OutputFileName)")
    return
    
    
##########################################################################################
# GribBandtoNParray
##########################################################################################   
def GribBandtoNParray(GribFile,BoundingBos,OutFile,BAND,Conversion,ConversionAdd,flagWrite):
    from osgeo import gdal
    from osgeo import ogr
    import numpy as np
    import subprocess

    dataset = gdal.Open(GribFile) 
    ncol=dataset.RasterXSize 
    nrow=dataset.RasterYSize
    Proj=dataset.GetProjection()
    gf = dataset.GetGeoTransform()
    leftx=gf[0]
    uppery=gf[3]
    resdegrx=gf[1]
    resdegry=gf[5]
    gt=dataset.GetGeoTransform()
    rb=dataset.GetRasterBand(BAND)
    if(BoundingBos[0]==-9):
        aa=rb.ReadAsArray().astype(np.float)*Conversion+ConversionAdd
        px = 0
        py = nrow
        px2 = ncol
        py2 = 0
        gf=gt 
    else:
        #LargeBoundingBos=[lry,uly,lrx,ulx]
        #ds_new_Clip = gdal.Translate('', outRaster, format='MEM', projWin=[LargeBoundingBos[3], LargeBoundingBos[1], LargeBoundingBos[2], LargeBoundingBos[0]])
        px = (np.array(BoundingBos[2] - gt[0]) / gt[1]).astype(int) #x pixel
        py = (np.array(BoundingBos[0]  - gt[3]) / gt[5]).astype(int)  #y pixel
        px2 = (np.array(BoundingBos[3] - gt[0]) / gt[1]).astype(int) #x pixel
        py2 = (np.array(BoundingBos[1]  - gt[3]) / gt[5]).astype(int)  #y pixel            
        aa=rb.ReadAsArray(int(px+1),int(py2+1),int(px2-px),int(py-py2)).astype(np.float)*Conversion+ConversionAdd
        BoundingBox=np.zeros(4)
        BoundingBox[0]=BoundingBos[0]
        BoundingBox[2]=gt[0]+(px+1)*gt[1]
        BoundingBox[1]=gt[3]+(py2+1)*gt[5]
        BoundingBox[3]=BoundingBos[3]
        
        gf=(BoundingBox[2],gf[1],gf[2],BoundingBox[1],gf[4],gf[5]) 
        #print (gf)
    if(flagWrite>0): CreateMatrixFileFloat(OutFile,aa,int(px2-px), int(py-py2),gf,Proj)
    
    dataset=None
    return aa


##########################################################################################
# dss2csv
########################################################################################## 
def dss2csv(PartA, PartB, PartC, PartE, PartF, begDate, endDate, DssFile, csvOut):

    """
    begDate: the format should be like '01JAN1964 06:00:00'"""

    from pydsstools.heclib.dss import HecDss
    import numpy as np
    import pandas as pd
    
    pathname = '/'+PartA+'/'+PartB+'/'+PartC+'//PartE/PartF/'
    
    fid = HecDss.Open(DssFile)
    ts = fid.read_ts(pathname,window=(begDate,endDate),trim_missing=True)
    
    times = ts.pytimes
    values = ts.values
#        values[ts.nodata] = -9999
    fid.close()
    
    # Export timeseries to csv using pandas
    df = pd.DataFrame({"Time":times, "Value":values})
    df.to_csv(csvOut,
               sep = ',', 
               index = False)
    
    return df

def getBasins(HUCID1,HUC12All,ToHUC12All,AllSubbasins):
    import numpy as np
    ups=all_indices(HUCID1,ToHUC12All)
    #AllSubbasins.append(HUCID1)
    if(np.size(ups)==0):
        
        xxx=[]
        xxx.append(0)
        print ("get to the end of this node  " + str(HUCID1))
        return xxx
    else:
        if(np.size(all_indices(HUCID1,AllSubbasins))>0):
             print ("appending again link" + str(HUCID1))
        AllSubbasins.append(HUCID1)
        
        for i in range(0,np.size(ups)):
            #print str(i) + " " + str(HUCID1) + " upstream link " + str(HUC12All[int(ups[i])])
            xxx=[]
            xxx=getBasins(HUC12All[int(ups[i])],HUC12All,ToHUC12All,AllSubbasins)             
            if(xxx[0]!=0):
                AllSubbasins=xxx
            else:
                AllSubbasins.append(HUC12All[int(ups[i])])
                    
        return AllSubbasins    
    

def CreateShapefile(Watersheds,DamID,dataSource,inLayer,Alllinks):
    from osgeo import ogr
    import osgeo.osr as osr
    import os
    import numpy as np
    outShapefile = os.path.join( Watersheds, str(DamID)+".shp" )
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
     # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)
    print   (outShapefile  )
    outDataSource = outDriver.CreateDataSource(outShapefile)

    #out_lyr_name = os.path.splitext( os.path.split( outShapefile )[1] )[0]

    proj = osr.SpatialReference() 
    proj.SetWellKnownGeogCS( "NAD83" )  
    
    outLayer = outDataSource.CreateLayer('test',proj,geom_type=ogr.wkbPolygon)
    inLayerDefn = inLayer.GetLayerDefn()
    # CREATE aLL THE FIELDS 
    for ii in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(ii)
        #fieldName = fieldDefn.GetName()
        outLayer.CreateField(fieldDefn)
    
    outLayerDefn = outLayer.GetLayerDefn()
    # Add Features to the output layer
    for j in range(0,np.size(Alllinks)):
        print (Alllinks[j])
        layer2 = dataSource.GetLayer()
        strFilter="HUC12 =" + "'" + str(Alllinks[j]) +"'" +  ""
        #strFilter="HUC12 =" + "'" + str(120901060108) +"'" +  ""
        #strFilter="HUC12 =" + str(AllSubUnique[j]) +  ""
        layer2.SetAttributeFilter(strFilter)
#        for feature in layer2:
#            print feature.GetField("HUC12")
            
        for inFeature in layer2:
            #print inFeature.GetField("HUC12")
            outFeature = ogr.Feature(outLayerDefn)
            for iii in range(0, outLayerDefn.GetFieldCount()):
                fieldDefn = outLayerDefn.GetFieldDefn(iii)
                #fieldName = fieldDefn.GetName()
                outFeature.SetField(outLayerDefn.GetFieldDefn(iii).GetNameRef(),
                inFeature.GetField(iii))
                geom = inFeature.GetGeometryRef()
                outFeature.SetGeometry(geom.Clone())
        # Add new feature to output Layer
                outLayer.CreateFeature(outFeature)
    
    #inDataSource.Destroy()
    outDataSource.Destroy()
import math    
def distance_on_unit_sphere(lat1, long1, lat2, long2):
 
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
         
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
         
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
         
    # Compute spherical distance from spherical coordinates.
         
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
     
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
    km = 6371 * arc
    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return km    
    
##############################################################################    
# distance_matrix
##############################################################################
# The function gets the distance between two point
def distance_matrix(x0, y0, x1, y1):
    obs = np.vstack((x0, y0)).T
    interp = np.vstack((x1, y1)).T

    # Make a distance matrix between pairwise observations
    # Note: from <http://stackoverflow.com/questions/1871536>
    # (Yay for ufuncs!)
    d0 = np.subtract.outer(obs[:,0], interp[:,0])
    d1 = np.subtract.outer(obs[:,1], interp[:,1])

    return np.hypot(d0, d1)

##############################################################################    
# idw
##############################################################################
    """ Inverse distance weighting (x and y could be a list of points)
    #### Input:
    1. x: row index where gauges is located (list)
    2. y: column index where gauges is located (list)
    3. z: ratio of gauge/radar at gauges location (list)
    4. xi: row index of pixel the pixel we need to get the weight for
    5. yi: column index of the pixel we need to get the weight for
    6.power: power for IDW method (it is usually 1 or 2)
    #### Output:
    1. gauge/radar ratio at desired pixel"""
    
def idw(x, y, z, xi, yi, power):
    dist = distance_matrix(x,y, xi,yi)

    # In IDW, weights are 1 / distance
    weights = 1.0 / dist**power

    # Make weights sum to one
    weights /= weights.sum(axis=0)
    weights[np.isnan(weights)] = 1
    # Multiply the weights for each interpolated point by all observed Z-values
    zi = np.dot(weights.T, z)
    return zi
    
##############################################################################    
# radar_adj_idw
##############################################################################
    """ Inverse distance weighting (x and y could be a list of points)
    #### Input:
    1. FilePath: Tiff or Asc file path
    2. GageLat: list of gauges' lat
    3. GageLon: list of gauges' long
    4. GageName: list of Gauges' name
    5. Conv: ratio for converting the rain or rainfall data unit
    6. OutFilePath: Location and name were the adj rainfall should be saved
    #### Output:
    1.  tiff file containing spatial radar adjusted"""
    
def radar_adj_idw(FilePath, OutFilePath, GageLat, GageLon, GageName, conv):
    Rainfalldata = gdal.Open(Filename) 
    rb=Rainfalldata.GetRasterBand(1)
    Rain=rb.ReadAsArray()
    ncol=Rainfall.RasterXSize 
    nrow=Rainfall.RasterYSize
    Proj=Rainfall.GetProjection()               

    # Get the index of each gauge location
    ind1Gages=[]
    ind2Gages=[]
    ratiolist=[]
    for j in range(len(GageName)):
        ind1Gages.append(int((GageLat[j]-gt[3])/gt[5]))
        ind2Gages.append(int((GageLon[j]-gt[0])/gt[1]))
        RadarAtGage[GageName[j]].append(Rain[ind1Gages[j],ind2Gages[j]])
        ratio=Gage[j]/Rain[ind1Gages[j],ind2Gages[j]]
        ratiolist.append(ratio)
        
    W_mask=np.zeros((nrow,ncol)) 
    for xi in range(nrow):
        for yi in range(ncol):
            W_mask[xi,yi]=square_idw(ind1Gages[:-1], ind2Gages[:-1], ratiolist, xi, yi)
            
    BC_rain=np.multiply(Rain,W_mask)
    BC_rainrate=BC_rain*Conv
    
    BF.CreateMatrixFileFloat(OutFilePath,BC_rain,ncol, nrow,gt,Proj) 

    return BC_rain, W_mask      
    

#########################################################################
#RasterMap
##########################################################################
    """ Creat map for a raster file on a desired shapfile(ex: USA map)
    #### Input:
    1. RasterPath: Tiff or Asc file path
    2. ShapeFile: Shapefile
    3. title: plot title
    4. min value of color bar
    5. max value of color bar
    6. OutFilePath: Location and name were the jpg should be saved
    #### Output:
    1.  jpg"""
    
def RasterMap(RasterPath, ShapeFile, OutFilePath, title, minPr, maxPr):
    from mpl_toolkits.basemap import Basemap
    import numpy as np
    import gdal
    from osgeo import gdal
    from osgeo import osr
    from osgeo.gdalconst import GA_ReadOnly
    import matplotlib.pyplot as plt 
    from scipy.linalg import logm, expm
    
    gdata = gdal.Open(RasterPath)
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
    
    # This just plots the shapefile -- it has already been clipped
    m.readshapefile(ShapeFile,'Counties',drawbounds=True, color='0.3',linewidth=1.5)
    
    #This just plots the Nexrad Point shapefile 
    Radar=m.readshapefile('O:/GIS/usa/NEXRAD_Sites/nexrad sites','code')
    for point in m.code:
        m.plot(point[0], point[1], marker='+', color='r', markersize=8, markeredgewidth=4)
        
    # Add DEM contour to the plot
    DEMfile='O:/GIS/usa/1km_DEM/Elevation_GRID/1kmDEM_usa.tif'
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
    m.contour(xDEM, yDEM, dataDEM.T, 40, colors="k", lw=0.5, alpha=0.3)

    x,y = np.mgrid[xmin:xmax+xres:xres, ymax+yres:ymin:yres]
    x,y = m(x,y)
    
    cmap = plt.cm.gist_rainbow
    cmap.set_under ('1.0')
    cmap.set_bad('0.8')
    
    m.pcolormesh(x,y, np.log10(data.T), cmap=cmap, vmin=minPr, vmax=maxPr)
    
    plt.colorbar( orientation='vertical', fraction=0.10, shrink=0.7, label='Log10(rainfall[mm])')
    plt.title(title)
    plt.legend()
    plt.savefig(OutFilePath,bbox_inches='tight',dpi=500)
    plt.close()