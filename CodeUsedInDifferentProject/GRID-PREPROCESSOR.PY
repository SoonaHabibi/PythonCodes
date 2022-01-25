#This script creates temperature, precipitation, and snow grids for the CWMS forecast run using input specified by
#the user in the extract GUI in CAVI. This user input is saved to a .fcst file, which is read by this script.
#Precipitation and temperature grids are created for the lookback period (start date - forecast date) using data 
#from real-time stations and gageInterp.

#Precipitation and temperature grids are then created for the forecast period (forecast date - end date) using
#QPS/QPF and QPT point forecast data from the NWRFC using gageInterp. 6-hr precipitation grids (inches) are then 
#processed to an hourly time step (and mm) using a uniform distribution. Min and max daily temperature grids are
#used to create hourly temperature grids (deg F) using the hyperbolic tangent method described in Schaub, Jr., 
#1991 (http://www.dtic.mil/dtic/tr/fulltext/u2/a240394.pdf).

#To create snow grids to initialize HMS, the user must create a local folder containing a SNODAS .tar file (for the
#start date). The script handles the remaining processing. The user should download the 'masked' SNODAS data, as 
#the script writes a Header.txt file specific to 'masked' SNODAS data. Data can be downloaded from the NSIDC ftp 
#site: ftp://sidads.colorado.edu/DATASETS/NOAA/G02158/.

#The script unzips the SNODAS.tar file, removes unwanted variables, creates headers for each file, renames each file, 
#converts each .dat file to tiff format, defines the projections of the grids to be WGS 1984, then reprojects the 
#grids to USGS Albers projection. After this, the script resamples the grids to 2000m, clips the grids down to the 
#SHG_grid shapefile, converts the SWE grids to Inches and the temperature grids to farenheight, converts the raster 
#to points, then spatially joins the points to the SHG_grid shapefile. After this, the script converts the spatially 
#joined SHG_grid shapefile to a raster, and then converts the rasters to asciis. This generates a SWE and cold content
#ATI grid.

#Finally, the script creates the remaining HMS initial snow grids: liquid water, cold content, and. melt rate ATI.
#The grids are then put into the forecast dss. 


#Created by: Danielle Perrot, RTI International
#Date: 12/14/2017
#Updated on 1/18/2018; no longer need to point to CWMS database. Forecast timeseries can be pulled into forecast dss via extract process, and then gageInterp can create grids using the timeseries stored in the forecast.dss.
#Updated on 2/25/2018; added error logging output. A file named error_grid-processor.log will be saved to the directory where this script is located when an error occurs, which will output details of the error (i.e. type and line #).

#%%
import sys
import os
from os import rename, listdir, chdir
from os.path import join
import gzip
import glob
import subprocess
from datetime import date, datetime, timedelta
import shutil
from shutil import copyfile
import tarfile
import io
import numpy as np
import fileinput
import xml.etree.ElementTree as etree
import time
from os.path import dirname, abspath
import logging

import arcpy
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

#Define function that will pre-pend lines to a text file
def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

#Define function to create Header.txt file for masked SNODAS data
def create_snodas_masked_header(targetfolder):
    f= open(os.path.join(targetfolder,'Header.txt'),"w+")
    f.write("nrows 3351\nncols 6935\nnbands 1\nnbits 16\npixeltype signedint\nbyteorder M\nlayout dat\nulxmap -124.729583333331703\nulymap 52.871249516804028\nxdim 0.00833333333\nydim 0.00833333333")
    f.close()      


########### USER INPUT AND DEFINING FOLDER LOCATIONS ##########
cavi_dir = os.getcwd() #Get current working directory
cwms_dir = os.path.dirname(cavi_dir)

script= os.path.abspath(__file__)
cwd = dirname(script) #This is the basin folder for CWMS CAVI, which is where this script is located.

log_file = os.path.join(cwd,'error_grid-processor.log')
logging.basicConfig(filename=log_file,level=logging.DEBUG)

print(str("Executing tool for project stored in: "+cwd))

try:
    #Prompt user for input:
    while True:
        forecast = raw_input('Define folder name for forecast (i.e. 2015.02.08-1200): ')
        dir_forecast = os.path.join(cwd,'forecast',forecast,'NWP_Rogue')
        if not os.path.exists(dir_forecast):
            print('Sorry, invalid folder name or forecast does not exist in forecast folder. Please define folder name again.')
        else:
            break   
    forecast_precip_yn = raw_input('Create forecasted precipitation grids? (Y/N): ').upper()

    control = os.path.join(dir_forecast,forecast+'_GMT.frcst') #Define .fcst file
    if not os.path.exists(control):
        print("No .fcst file for specified forecast, ending tool...")
        time.sleep(5)
        sys.exit()
        
    dir_gageInterp_template_control = os.path.join(cwd,'gageInterp_templates')
    dir_grid_programs = os.path.join(cwms_dir,'common','grid')
    dir_constant = os.path.join(cwd,'constant_grids')
    grid_shp = os.path.join(dir_constant,"Rogue_SHG/grid.shp")

    #Copy executables to the forecast folder
    print("Copying gageInterp, dss2ascGrid, asc2dssGrid, and conus.nad to local forecast folder...")
    shutil.copy2(os.path.join(dir_grid_programs,'gageInterp.exe'),os.path.join(dir_forecast,'gageInterp.exe'))
    shutil.copy2(os.path.join(dir_grid_programs,'dss2ascGrid.exe'),os.path.join(dir_forecast,'dss2ascGrid.exe'))
    shutil.copy2(os.path.join(dir_grid_programs,'asc2dssGrid.exe'),os.path.join(dir_forecast,'asc2dssGrid.exe'))
    shutil.copy2(os.path.join(dir_grid_programs,'conus.nad'),os.path.join(dir_forecast,'conus.nad'))
    time.sleep(5)

    #Read xml .fcst file generated from user input in CAVI to extract the extract, start, forecast, and end dates. Dates are in GMT.
    control = etree.parse(control)
    root = control.getroot()
    for child in root:
        for element in child:
            if element.tag == 'Extract':
                extract = element.text
            if element.tag == 'Start':
                start = element.text
            if element.tag == 'Forecast':
                forecast = element.text
            if element.tag == 'End':
                end = element.text

    print(str("Extract: "+extract))
    print(str("Start: "+start))
    print(str("Forecast: "+forecast))
    print(str("End: "+end))
    time.sleep(5)

    #Create datetime objects from .fcst file
    extract_date = datetime.datetime.strptime(extract,'%d%b%Y %H%M')
    start_date = datetime.datetime.strptime(start,'%d%b%Y %H%M')
    forecast_date = datetime.datetime.strptime(forecast,'%d%b%Y %H%M')
    end_date = datetime.datetime.strptime(end,'%d%b%Y %H%M')

    #Prompt user for input regarding snowmelt modeling
    snowmelt_modeling_yn = raw_input('Create initial condition snow grids? Only needed if snowmelt modeling being performed in HMS. (Y/N): ').upper()
    if snowmelt_modeling_yn == 'Y':
        while True:
            snow_dir = raw_input('Enter filepath to where masked SNODAS tar file is located (i.e. C:/Projects/Rogue/SNOW_GRIDS): ')
            if not os.path.exists(snow_dir):
                print("Folder does not exist, please re-enter (using '/' to separate folders.")
            else:
                break
        spring_melt = raw_input('Calculate antecedent temperature index based on observed air temperature data above the base temperature? If spring snowmelt conditions, enter Y; otherwise, enter N: ').upper()
        #(According to 3.1.38_Snowmelt_for_Corps_Water_Management_Systems_2018.dox,"Once the spring melt period begins, the antecedent temperature index should be calculated based on observed air temperature data above the base temperature since the onset of melt.") 
        #Calculate additional grids for lookback period and pre-lookback period (extract date up until forecast date) if spring melt conditions prevail
        if extract_date==start_date and spring_melt=='Y':
            print("WARNING: Start date and extract date are the same. Melt rate ATI grid will therefore NOT be calculated using accumulated degree days (and will be set to 0 instead).")
            time.sleep(2)
            continue_script = raw_input('Continue? (Y/N): ').upper()
            if continue_script == 'Y':
                print("Continuing, and will set melt rate ATI grid to 0.")
                time.sleep(5)
            if continue_script == 'N':
                print("Exiting script...please re-run extract process with the extract date set earlier than the start date to calculate melt rate ATI grid with accumulated degree days.")
                time.sleep(10)
                sys.exit()

    #Determine PRISM bias grid to use from forecast date
    forecast_date_month = forecast_date.month #get month from forecast date
    if (4<=forecast_date_month<=10): #If the month for the lookback end date (i.e. forecast date) is sometime between April and October, use the summer bias grid. Otherwise, use winter bias grid.
        bias = "SUMMER"
    else:
        bias = "WINTER"
    print(str("Month of forecast date = "+str(forecast_date_month)+",therefore using "+bias+" bias grid for gageInterp."))
    time.sleep(5)

    #### CREATE GRIDS FOR LOOKBACK PERIOD (start date - forecast date)
    lookbacktimestart_new = start_date.strftime('%d%b%Y, %H%M')
    lookbacktimeend_new = forecast_date.strftime('%d%b%Y, %H%M')

    #Update template deckfile for precip for lookback period
    template_gageInterp_control_precip = os.path.join(dir_gageInterp_template_control,'MakePrecipGrids_Rogue_template.ginterp')
    gageInterp_control_precip_lookback = os.path.join(dir_forecast,'MakePrecipGrids_Rogue_lookback.ginterp')
    shutil.copy2(template_gageInterp_control_precip,gageInterp_control_precip_lookback)
    with open(gageInterp_control_precip_lookback) as s: #Look for lines to update in gageInterp precip lookback control file
        for line in s:
            if line.startswith("TimeStart:"):
                timestart = line
                timestart_new = line.replace("TIMESTART",lookbacktimestart_new)
            if line.startswith("TimeEnd:"):
                timeend = line
                timeend_new = line.replace("TIMEEND",lookbacktimeend_new)
            if line.startswith("OutFile:"):
                outfile = line
                outfile_new = line.replace("DIR_FORECAST",dir_forecast)
                outfile_new = outfile_new.replace("/",'\\')
            if line.startswith("AdjustGridFile:"):
                biasgrid = line
                biasgrid_new = line.replace("DIR_CONSTANT",dir_constant)
                biasgrid_new = biasgrid_new.replace("/",'\\')
            if line.startswith("AdjustGridPath:"):
                biaspath = line
                biaspath_new = line.replace("[SEASON]",bias)
            if line.startswith("DSSFile:"):
                dssfile = line
                dssfile_new = line.replace("DIR_FORECAST",dir_forecast)
                dssfile_new = dssfile_new.replace("/",'\\')
                              
    with open(gageInterp_control_precip_lookback,'r') as file: #Open and update start time and end time in gageInterp precip lookback control file
        s=file.read()
    print("Updating precipitation gageInterp control file for lookback period")
    time.sleep(2)
    s = s.replace(timestart,timestart_new)
    s = s.replace(timeend,timeend_new)
    s = s.replace(outfile,outfile_new)
    s = s.replace(biasgrid,biasgrid_new)
    s = s.replace(biaspath,biaspath_new)
    s = s.replace(dssfile,dssfile_new)                                             
    with open(gageInterp_control_precip_lookback,'w') as file:
        file.write(s)
        file.close()

    #Run GageInterp for lookback period for precip
    os.chdir(dir_forecast) #Change directory to gageInterp directory; gageInterp will not run if given filepaths, must be run from directory where gageInterp.exe is located.
    print("Run gageInterp to create precipitation grids for lookback period for forecast.dss")
    time.sleep(5)
    while True:
        try:
            subprocess.check_call(["gageInterp.exe","CONTROL=MakePrecipGrids_Rogue_lookback.ginterp"])
        except subprocess.CalledProcessError:
            retry = raw_input('GageInterp crashed. Re-run gageInterp (Y/N)?: ').upper()
            if retry == "Y":
                print("Reattempting............")
                time.sleep(2)
                continue          
            if retry == "N":
                print("Exiting tool...........")
                sys.exit()
        else:
            break
    os.chdir(cwd)


    #If snowmelt modeling: update template deckfile for temp for lookback period (or, if spring melt conditions, for extract period+lookback period)
    if snowmelt_modeling_yn == 'Y':
        lookbacktimestart_new = (start_date-timedelta(hours=1)).strftime('%d%b%Y, %H%M')
        lookbacktimeend_new = forecast_date.strftime('%d%b%Y, %H%M')
        if spring_melt == 'Y':               
            lookbacktimestart_new = (extract_date-timedelta(hours=1)).strftime('%d%b%Y, %H%M')
           
        template_gageInterp_control_temp = os.path.join(dir_gageInterp_template_control,'MakeTempGrids_Rogue_template.ginterp')
        gageInterp_control_temp_lookback = os.path.join(dir_forecast,'MakeTempGrids_Rogue_lookback.ginterp')
        shutil.copy2(template_gageInterp_control_temp,gageInterp_control_temp_lookback)
        with open(gageInterp_control_temp_lookback) as s: #Look for lines to update in gageInterp precip lookback control file
            for line in s:
                if line.startswith("TimeStart:"):
                    timestart = line
                    timestart_new = line.replace("TIMESTART",lookbacktimestart_new)
                if line.startswith("TimeEnd:"):
                    timeend = line
                    timeend_new = line.replace("TIMEEND",lookbacktimeend_new)
                if line.startswith("OutFile:"):
                    outfile = line
                    outfile_new = line.replace("DIR_FORECAST",dir_forecast)
                    outfile_new = outfile_new.replace("/",'\\')
                if line.startswith("AdjustGridFile:"):
                    biasgrid = line
                    biasgrid_new = line.replace("DIR_CONSTANT",dir_constant)
                    biasgrid_new = biasgrid_new.replace("/","\\")
                if line.startswith("DSSFile:"):
                    dssfile = line
                    dssfile_new = line.replace("DIR_FORECAST",dir_forecast)
                    dssfile_new = dssfile_new.replace("/","\\")
        with open(gageInterp_control_temp_lookback,'r') as file: #Open and update start time and end time in gageInterp precip lookback control file
            s=file.read()
        print("Updating temperature gageInterp control file for lookback period")
        time.sleep(2)
        s = s.replace(timestart,timestart_new)
        s = s.replace(timeend,timeend_new)
        s = s.replace(outfile,outfile_new)
        s = s.replace(biasgrid,biasgrid_new)
        s = s.replace(dssfile,dssfile_new)                                             
        with open(gageInterp_control_temp_lookback,'w') as file:
            file.write(s)
            file.close()

        #Run GageInterp for lookback period for temp
        os.chdir(dir_forecast) 
        print("Run gageInterp to create temperature grids for lookback period for forecast.dss")
        time.sleep(5)
        while True:
            try:
                subprocess.check_call(["gageInterp.exe","CONTROL=MakeTempGrids_Rogue_lookback.ginterp"])
            except subprocess.CalledProcessError:
                retry = raw_input('GageInterp crashed. Re-run gageInterp (Y/N)?: ').upper()
                if retry == "Y":
                    print("Reattempting............")
                    time.sleep(2)
                    continue
                if retry == "N":
                    print("Exiting tool...........")
                    sys.exit()
            else:
                break
        os.chdir(cwd)


    #### CREATE GRIDS FOR FORECAST PERIOD (forecast date - end date)

    ## FORECASTED PRECIP ##
    forecasttimestart_new = forecast_date.strftime('%d%b%Y, %H%M')
    forecasttimeend_new = end_date.strftime('%d%b%Y, %H%M')

    if forecast_precip_yn == 'Y':
        #Update template deckfile for precip for forecast period
        template_gageInterp_control_precip = os.path.join(dir_gageInterp_template_control,'MakePrecipGrids_Fcst_Rogue_template.ginterp')
        gageInterp_control_precip_fcst = os.path.join(dir_forecast,'MakePrecipGrids_Rogue_fcst.ginterp')
        shutil.copy2(template_gageInterp_control_precip,gageInterp_control_precip_fcst)
        with open(gageInterp_control_precip_fcst) as s: #Look for lines to update in gageInterp precip fcst control file
            for line in s:
                if line.startswith("TimeStart:"):
                    timestart = line
                    timestart_new = line.replace("FORECAST_TIMESTART",forecasttimestart_new)
                if line.startswith("TimeEnd:"):
                    timeend = line
                    timeend_new = line.replace("FORECAST_TIMEEND",forecasttimeend_new)
                if line.startswith("OutFile:"):
                    outfile = line
                    outfile_new = line.replace("DIR_FORECAST",dir_forecast)
                    outfile_new = outfile_new.replace("/",'\\')
                if line.startswith("AdjustGridFile:"):
                    biasgrid = line
                    biasgrid_new = line.replace("DIR_CONSTANT",dir_constant)
                    biasgrid_new = biasgrid_new.replace("/",'\\')
                if line.startswith("AdjustGridPath:"):
                    biaspath = line
                    biaspath_new = line.replace("[SEASON]",bias)
                if line.startswith("DSSFile:"):
                    dssfile = line
                    dssfile_new = line.replace("DIR_FORECAST",dir_forecast)
                    dssfile_new = dssfile_new.replace("/",'\\')
                                  
        with open(gageInterp_control_precip_fcst,'r') as file: #Open and update start time and end time in gageInterp precip fcst control file
            s=file.read()
        print("Updating precipitation gageInterp control file for forecast period")
        time.sleep(5)
        s = s.replace(timestart,timestart_new)
        s = s.replace(timeend,timeend_new)
        s = s.replace(outfile,outfile_new)
        s = s.replace(biasgrid,biasgrid_new)
        s = s.replace(biaspath,biaspath_new)
        s = s.replace(dssfile,dssfile_new)                                             
        with open(gageInterp_control_precip_fcst,'w') as file:
            file.write(s)
            file.close()

        #Run GageInterp for 6 hr precip for forecast period     
        os.chdir(dir_forecast)
        print("Run gageInterp to create 6hr precipitation grids (mm) from RFC QPS/QPF data (in) for forecast period for forecast.dss")
        time.sleep(5)
        while True:
            try:
                subprocess.check_call(["gageInterp.exe","CONTROL=MakePrecipGrids_Rogue_fcst.ginterp"])
            except subprocess.CalledProcessError:
                retry = raw_input('GageInterp crashed. Re-run gageInterp (Y/N)?: ').upper()
                if retry == "Y":
                    print("Reattempting............")
                    time.sleep(2)
                    continue
                if retry == "N":
                    print("Exiting tool...........")
                    sys.exit()
            else:
                break
        os.chdir(cwd)

        #Extract 6 hr forecasted precip grids from dss
        print("Create asc of 6hr precipitation grids (mm) from forecast.dss")
        time.sleep(5)
        precip_fcst_6hr_asc_folder = os.path.join(dir_forecast,"precip_fcst_6hr_asc")
        if not os.path.exists(precip_fcst_6hr_asc_folder):
            os.mkdir(precip_fcst_6hr_asc_folder)
        else:
            shutil.rmtree(precip_fcst_6hr_asc_folder)
            os.mkdir(precip_fcst_6hr_asc_folder)

        precip_fcst_1hr_asc_folder = os.path.join(dir_forecast,"precip_fcst_1hr_asc")
        if not os.path.exists(precip_fcst_1hr_asc_folder):
            os.mkdir(precip_fcst_1hr_asc_folder)
        else:
            shutil.rmtree(precip_fcst_1hr_asc_folder)
            os.mkdir(precip_fcst_1hr_asc_folder)

        time1 = forecast_date
        time2 = end_date - timedelta(hours=6)
        dif = int((time2-time1).total_seconds()/21600) # number of 6 hr time periods between time 1 and time 2
        datetime_list = [(time1 + timedelta(hours=6*x)).strftime("%d%b%Y:%H%M") for x in range(0, dif+1)] #Make list of datetimes between time1 and time2 every 6 hours
        datetime_str_list =[str(x).upper() for x in datetime_list] #Convert list of datetimes to proper format for dss
        datetime_str_next_list = [(datetime.datetime.strptime(x,"%d%b%Y:%H%M")+timedelta(hours=6)).strftime("%d%b%Y:%H%M") for x in datetime_str_list]
        datetime_str_next_list = [(datetime.datetime.strptime(x,"%d%b%Y:%H%M")-timedelta(days=1)).strftime("%d%b%Y:%H%M").replace('0000','2400') if '0000' in str(x) else x for x in datetime_str_next_list]
        datetime_str_next_list = [x.upper() for x in datetime_str_next_list]
        
        os.chdir(dir_forecast)
        for i,dt in enumerate(datetime_str_list):
            dt_next = datetime_str_next_list[i]
            path=str('/SHG/ROGUE/PRECIP/'+dt+'/'+dt_next+'/GINTERP-FCST-6HR/')
            asc_name = str('precip6hr_'+dt.replace(":","")+'.asc')
            command_output=str('OUTPUT='+os.path.basename(precip_fcst_6hr_asc_folder)+'\\'+asc_name)
            command_dss = str('dss=forecast.dss')
            command_path=str('path='+path)
            print(path)
            subprocess.call(["dss2ascGrid.exe",command_output,command_dss,command_path])
        os.chdir(cwd)

        #Create header to use for estimated hourly files
        example_precip_asc = glob.glob(os.path.join(precip_fcst_6hr_asc_folder,'*.asc'))[0]
        with open(example_precip_asc) as myfile:
            head= [next(myfile) for x in xrange(6)]
        header = ''.join(head)

        #Create forecasted hourly grids (mm) from forecasted 6 hr (mm) precip grids
        print("Making hourly grids (mm) from forecasted 6hr grid (in)")
        time.sleep(5)
        for i,dt in enumerate(datetime_str_list):
            file = os.path.join(precip_fcst_6hr_asc_folder,str('precip6hr_'+dt.replace(":","")+'.asc'))
            precip_6hr_in = np.loadtxt(file,skiprows=6) #Load 6hr grids (mm)
            precip_1hr_mm = precip_6hr_in/6 #Convert to 1 hr grid (mm)

            t1 = datetime.datetime.strptime(dt,"%d%b%Y:%H%M")
            if '2400' in datetime_str_next_list[i]:
                t2 = datetime.datetime.strptime(datetime_str_next_list[i].replace('2400','0000'),"%d%b%Y:%H%M")+timedelta(days=1)-timedelta(hours=1)
            else:
                t2 = datetime.datetime.strptime(datetime_str_next_list[i],"%d%b%Y:%H%M")-timedelta(hours=1)
            dif_hr = int((t2-t1).total_seconds()/3600)
            datetime_hr_list = [(t1 + timedelta(hours=x)).strftime("%d%b%Y:%H%M") for x in range(0, dif_hr+1)]
            datetime_next_hr_list = [(datetime.datetime.strptime(x,"%d%b%Y:%H%M")+timedelta(hours=1)).strftime("%d%b%Y:%H%M") for x in datetime_hr_list]
            for i,x in enumerate(datetime_hr_list):
                x = x.upper()
                x_next = datetime_next_hr_list[i].upper()
                name= str('precip1hr_'+x.replace(":","")+'.asc')
                #Save hourly asc to folder
                np.savetxt(os.path.join(precip_fcst_1hr_asc_folder,name),precip_1hr_mm,delimiter=" ",fmt='%1.4f')
                line_prepender(os.path.join(precip_fcst_1hr_asc_folder,name),header)


        #Write new estimated hourly forecasted precip grids back to the forecast.dss
        est_hourly_fcst_precip_files = sorted(glob.glob(os.path.join(precip_fcst_1hr_asc_folder,'precip1hr_*.asc')))

        command_dssfile='DSSFILE=forecast.dss'
        command_dtype = 'DTYPE=PER-INC'
        command_gridtype = 'GRIDTYPE=SHG'
        command_dunits = 'DUNITS=MM'

        print("Putting estimated hourly forecasted precip grids in forecast.dss")
        time.sleep(5)

        for file in est_hourly_fcst_precip_files:
            input_file = os.path.basename(file)
            shutil.copy2(file,os.path.join(dir_forecast,input_file)) #Copy grid to forecast directory; asc2dssGrid.exe must run in same directory as file and the target dss.

            date_x = input_file[10:19]
            time_x = input_file[19:23]
            datetime_x = str(date_x+":"+time_x)
            datetime_x_next = datetime.datetime.strptime(datetime_x,"%d%b%Y:%H%M")+timedelta(hours=1)
            datetime_x_next = datetime_x_next.strftime("%d%b%Y:%H%M").upper()

            #Handle any issues with converting from python datetime to datetime in python (dss uses 24:00, not 00:00)
            if datetime_x_next[10:12]=="00":
                date_x_next = (datetime.datetime.strptime(datetime_x_next,"%d%b%Y:%H%M")-timedelta(days=1)).strftime("%d%b%Y").upper()
                time_x_next = "2400"
                datetime_x_next = str(date_x_next+":"+time_x_next)

            #Write to dss  
            pathname=str('/SHG/ROGUE/PRECIP/'+datetime_x+'/'+datetime_x_next+'/GINTERP/')
            command_input = str('INPUT='+input_file)
            command_pathname = str('PATHNAME='+pathname)
            os.chdir(dir_forecast)
            subprocess.call(["asc2dssGrid.exe",command_input,command_dssfile,command_pathname,command_gridtype,command_dtype,command_dunits])
            os.remove(os.path.join(dir_forecast,input_file))
            os.chdir(cwd)


    ## FORECASTED TEMP ##
    forecastdatestart_new_prevday = (forecast_date-timedelta(days=1)).strftime('%d%b%Y') #Needed for forecasted temperature grid calc by gageInterp (to get grid for time x, input start date of time x-1).
    forecastdateend_new = (end_date+timedelta(days=1)).strftime('%d%b%Y') #One extra day needed to generate grids through the end of the forecast period (hourly grids are not generated for the last day)
            
    if snowmelt_modeling_yn == 'Y':
        #Update template deckfile for temp for forecast period
        min_max_list = ['MAX','MIN']
        for m in min_max_list:
            #Make control file and and run gageInterp for forecasted daily min/max temp:
            template_gageInterp_control_temp = os.path.join(dir_gageInterp_template_control,'MakeTempGrids_Fcst_Rogue_template.ginterp')
            gageInterp_control_temp_fcst = os.path.join(dir_forecast,'MakeTempGrids_Rogue_fcst_'+m+'.ginterp')
            shutil.copy2(template_gageInterp_control_temp,gageInterp_control_temp_fcst)
            with open(gageInterp_control_temp_fcst) as s: #Look for lines to update in gageInterp precip lookback control file
                for line in s:
                    if line.startswith("TimeStart:"):
                        timestart = line
                        timestart_new = line.replace("FORECAST_TIMESTART",forecastdatestart_new_prevday)
                    if line.startswith("TimeEnd:"):
                        timeend = line
                        timeend_new = line.replace("FORECAST_TIMEEND",forecastdateend_new)
                    if line.startswith("OutFile:"):
                        outfile = line
                        outfile_new = line.replace("DIR_FORECAST",dir_forecast)
                        outfile_new = outfile_new.replace("/",'\\')
                    if line.startswith("AdjustGridFile:"):
                        biasgrid = line
                        biasgrid_new = line.replace("DIR_CONSTANT",dir_constant)
                        biasgrid_new = biasgrid_new.replace("/","\\")
                    if line.startswith("DSSFile:"):
                        dssfile = line
                        dssfile_new = line.replace("DIR_FORECAST",dir_forecast)
                        dssfile_new = dssfile_new.replace("/","\\")
            with open(gageInterp_control_temp_fcst,'r') as file: #Open and update start time and end time in gageInterp precip lookback control file
                s=file.read()
            print(str("Updating temperature gageInterp control file for forecast period for: "+m))
            time.sleep(5)
            s = s.replace(timestart,timestart_new)
            s = s.replace(timeend,timeend_new)
            s = s.replace(outfile,outfile_new)
            s = s.replace(biasgrid,biasgrid_new)
            s = s.replace(dssfile,dssfile_new)                                             
            with open(gageInterp_control_temp_fcst,'w') as file:
                file.write(s)
                file.close()

            f = open(gageInterp_control_temp_fcst,'r')
            filedata = f.read()
            f.close()

            newdata = filedata.replace("[MIN/MAX]",m)

            f = open(gageInterp_control_temp_fcst,'w')
            f.write(newdata)
            f.close()

            os.chdir(dir_forecast)
            print(str("Run gageInterp to create daily "+m+" temperature grids from RFC QTF data for forecast period for forecast.dss"))
            time.sleep(5)

            while True:
                try:
                    if m=='MAX':
                        subprocess.check_call(["gageInterp.exe","CONTROL=MakeTempGrids_Rogue_fcst_MAX.ginterp"])
                    if m=='MIN':
                        subprocess.check_call(["gageInterp.exe","CONTROL=MakeTempGrids_Rogue_fcst_MIN.ginterp"])
                except subprocess.CalledProcessError:
                    retry = raw_input('GageInterp crashed. Re-run gageInterp (Y/N)?: ').upper()
                    if retry == "Y":
                        print("Reattempting............")
                        time.sleep(2)
                        continue
                    if retry == "N":
                        print("Exiting tool...........")
                        sys.exit()
                else:
                    break

            os.chdir(cwd)
            
        #Convert dss2asc for forecasted min and max daily temps
        time1 = forecast_date #first temp grid in dss
        time2 = end_date+timedelta(days=1) #last temp grid in dss
        dif = int((time2-time1).total_seconds()/86400) # number of 1 day time periods between time 1 and time 2
        datetime_list = [(time1 + timedelta(days=x)).strftime("%d%b%Y") for x in range(0, dif+1)]
        datetime_str_list =[str(x).upper() for x in datetime_list] 

        min_temp_asc_folder = os.path.join(dir_forecast,'MIN_temp_asc')
        if not os.path.exists(min_temp_asc_folder):
            os.mkdir(min_temp_asc_folder)
        else:
            shutil.rmtree(min_temp_asc_folder)
            os.mkdir(min_temp_asc_folder)
            
        max_temp_asc_folder = os.path.join(dir_forecast,'MAX_temp_asc')
        if not os.path.exists(max_temp_asc_folder):
            os.mkdir(max_temp_asc_folder)
        else:
            shutil.rmtree(max_temp_asc_folder)
            os.mkdir(max_temp_asc_folder)
            

        print("Making asciis from forecast.dss for min and max temperature grids during forecast period...")
        time.sleep(5)
        for m in min_max_list:
            os.chdir(dir_forecast)
            for date in datetime_str_list:
                    path=str('/SHG/ROGUE/TEMP-AIR-'+m+'/'+date+':2400//GINTERP-FCST-1D-'+m+'/') #Daily RFC forecasted grids are at timestamp 24:00 (midnight)
                    asc_name = str(m+'_temp_'+date.replace(':','')+'.asc')
                    command_output=str('OUTPUT='+m+'_temp_asc\\'+asc_name)
                    command_dss = str('dss=forecast.dss')
                    command_path=str('path='+path)
                    subprocess.call(["dss2ascGrid.exe",command_output,command_dss,command_path])
            os.chdir(cwd)

        #Create header to use for estimated hourly files
        example_temp_asc = glob.glob(os.path.join(max_temp_asc_folder,'*.asc'))[0]
        with open(example_temp_asc) as myfile:
            head= [next(myfile) for x in xrange(6)]
        header = ''.join(head)

        #Make output folder for hourly grid estimation
        est_hourly_temp_folder = os.path.join(dir_forecast,"temp_fcst_1hr_asc")
        if not os.path.exists(est_hourly_temp_folder):
            os.mkdir(est_hourly_temp_folder)
        else:
            shutil.rmtree(est_hourly_temp_folder)
            os.mkdir(est_hourly_temp_folder)

        #Begin making hourly grids from daily min and max grids using hyperbolic tangent method described in Schaub, Jr. (1991): http://www.dtic.mil/dtic/tr/fulltext/u2/a240394.pdf
        for i,date in enumerate(datetime_str_list):
            try:
                day1 = date
                day2 = datetime_str_list[i+1]
                print(str("Creating hourly temp grids from min and max temp grids of "+day1[:9]+" and the min temp grid of "+day2[:9]))
                time.sleep(2)
                stack=[]
                asc_list = glob.glob(os.path.join(dir_forecast,'*/*'+day1+'*.asc'))
                for m in ['MIN','MAX']:
                    for asc in asc_list:
                        if m in asc:
                            array = np.loadtxt(asc,skiprows=6)
                            stack.append(array)
                array_day2_min = np.loadtxt(os.path.join(min_temp_asc_folder,'MIN_temp_'+day2+'.asc'),skiprows=6)
                stack.append(array_day2_min)
                stack=np.array(stack)
                min1_time = 0
                max1_time = 9
                min2_time = 23
                hours_morning = range(min1_time,max1_time+1)
                hours_evening = range(max1_time+1,min2_time+1)
                basename = os.path.splitext(os.path.basename(asc_list[0]))[0].replace("MAX_temp","temp_1hr")

                for hr in hours_morning:
                    grid_temp_hourly = (((np.subtract(stack[1],stack[0]))/2)*np.tanh((hr-4.5)/2.5))+((np.add(stack[1],stack[0]))/2)
                    local_hr = hr+5
                    if local_hr<10:
                        name = str(basename+str("0"+str(local_hr)+"00")+'.asc')
                    else:
                        name = str(basename+str(str(local_hr)+"00")+'.asc')
                    dt_grid = datetime.datetime.strptime(str(day1+', '+str(local_hr)+"00"),"%d%b%Y, %H%M") #datetime stamp of grid
                    if dt_grid>forecast_date: #If the datetime stamp of the grid is after the forecast date, save the grid
                        np.savetxt(os.path.join(est_hourly_temp_folder,name),grid_temp_hourly,delimiter=" ",fmt='%1.2f')
                        line_prepender(os.path.join(est_hourly_temp_folder,name),header)
                for hr in hours_evening:
                    grid_temp_hourly = (-1*(((np.subtract(stack[1],stack[2]))/2)*np.tanh((hr-16.5)/3.5)))+((np.add(stack[1],stack[2]))/2)
                    local_hr = hr+5
                    if local_hr<24:
                        name = str(basename+str(str(local_hr)+"00")+'.asc')
                        dt_grid = datetime.datetime.strptime(str(day1+', '+str(local_hr)+"00"),"%d%b%Y, %H%M") #datetime stamp of grid 
                    if local_hr==24:
                        name = str(basename+str(str(local_hr)+"00")+'.asc')
                        dt_grid = datetime.datetime.strptime(str(day2+', '+"0000"),"%d%b%Y, %H%M") #datetime stamp of grid 
                    if local_hr>24:
                        local_hr=local_hr-24
                        name = str(basename+str("0"+str(local_hr)+"00")+'.asc').replace(day1,day2)
                        dt_grid = datetime.datetime.strptime(str(day2+', '+str(local_hr)+"00"),"%d%b%Y, %H%M")
                    if dt_grid>forecast_date: #If the datetime stamp of the grid is after the forecast date, save the grid
                        np.savetxt(os.path.join(est_hourly_temp_folder,name),grid_temp_hourly,delimiter=" ",fmt='%1.2f')
                        line_prepender(os.path.join(est_hourly_temp_folder,name),header)
                
            except:
                print(str("No hourly temp grids created for "+day1[:9]+" since it is the last day in the list."))
                time.sleep(3)


        #Write new estimated hourly forecasted temperature grids back to the forecast.dss
        est_hourly_fcst_temp_files = sorted(glob.glob(os.path.join(est_hourly_temp_folder,'temp_1hr*.asc')))

        command_dssfile='DSSFILE=forecast.dss'
        command_dtype = 'DTYPE=INST-VAL'
        command_gridtype = 'GRIDTYPE=SHG'
        command_dunits = 'DUNITS=DEG F'

        print("Putting estimated hourly forecasted temperature grids in forecast.dss")
        time.sleep(5)

        for file in est_hourly_fcst_temp_files:
            input_file = os.path.basename(file)
            shutil.copy2(file,os.path.join(dir_forecast,input_file)) #Copy grid to forecast directory; asc2dssGrid.exe must run in same directory as file and the target dss.
            date_x = input_file[9:18]
            time_x = input_file[18:22]
            datetime_x = str(date_x+":"+time_x)
            pathname=str('/SHG/ROGUE/TEMP/'+datetime_x+'//GINTERP/')
            command_input = str('INPUT='+input_file)
            command_pathname = str('PATHNAME='+pathname)
            os.chdir(dir_forecast)
            subprocess.call(["asc2dssGrid.exe",command_input,command_dssfile,command_pathname,command_gridtype,command_dtype,command_dunits])
            os.remove(os.path.join(dir_forecast,input_file))
            os.chdir(cwd)

        ########### PROCESS SNODAS AND MAKE INITIAL SNOW GRIDS ##########
        #Define directory of snow grids(will need to figure out how to change this to pull the SNODAS grids from the forecast.dss eventually)
        print("MAKE INITIAL SNOW GRIDS FOR HMS")

        create_snodas_masked_header(snow_dir)
        snodas_folder = os.path.join(snow_dir,"SNODAS_PROCESSING")
        snodas_orig_files_dir = os.path.join(snodas_folder,"1_Original_Files")
        snodas_renamed_files_dir = os.path.join(snodas_folder,"2_Original_Files_Delete_Rename")
        header_file = os.path.join(snow_dir,"Header.txt")
        processing_dir = os.path.join(snodas_folder,"3_Raster_Processing")
        final_asc_dir = os.path.join(snodas_folder,"4_Final_ASCII")
        SNOW_GRIDS_FOR_CWMS = os.path.join(snow_dir,"SNOW_GRIDS_FOR_CWMS")
        snow_archive_folder = os.path.join(snow_dir,"archive")


        if not os.path.exists(snodas_folder):
            os.mkdir(snodas_folder)
            os.mkdir(snodas_orig_files_dir)
            os.mkdir(snodas_renamed_files_dir)
            os.mkdir(processing_dir)
            os.mkdir(final_asc_dir)
        else:
            shutil.rmtree(snodas_folder)
            os.mkdir(snodas_folder)
            os.mkdir(snodas_orig_files_dir)
            os.mkdir(snodas_renamed_files_dir)
            os.mkdir(processing_dir)
            os.mkdir(final_asc_dir)
            
        if not os.path.exists(SNOW_GRIDS_FOR_CWMS):
            os.mkdir(SNOW_GRIDS_FOR_CWMS)
        else:
            shutil.rmtree(SNOW_GRIDS_FOR_CWMS)
            os.mkdir(SNOW_GRIDS_FOR_CWMS)

        if not os.path.exists(snow_archive_folder):
            os.mkdir(snow_archive_folder)

        snodas_file = os.path.join(snow_dir,'SNODAS_'+start_date.strftime("%Y%m%d")+'.tar') #get all tar files in original files directory

        if not os.path.exists(snodas_file):
            print(str("No SNODAS tar file to process for the user defined 'start' date:"+start_date.strftime("%Y%m%d")))
            print("Ending tool. Please add a SNODAS tar file to process to the SNOW_GRIDS directory.")
            time.sleep(15)
            sys.exit()

        shutil.copy2(snodas_file,os.path.join(snow_archive_folder,os.path.basename(snodas_file)))        
        os.rename(snodas_file,os.path.join(snodas_orig_files_dir,os.path.basename(snodas_file)))

        arcpy.env.workspace = snodas_renamed_files_dir
        sr = arcpy.SpatialReference("WGS 1984")
        sr2 = arcpy.SpatialReference("USA Contiguous Albers Equal Area Conic USGS")

        #Add all values and variables that you wish to delete in the list below.
        #For this study,we are only concerned about SWE(1034) and Temp(1038) so all other variables can be removed.
        file = os.path.join(snodas_orig_files_dir,'SNODAS_'+start_date.strftime("%Y%m%d")+'.tar')
        list_to_rm = ['1025', '1036', '1039', '1044', '1050', '.Hdr'];

        print(str("Extracting and processing data from SNODAS file: "+file))
        time.sleep(5)
        tar = tarfile.open(file,'r') #unzip the tar file
        tar.extractall(snodas_orig_files_dir)

        for file in glob.glob(os.path.join(snodas_orig_files_dir,'*.gz')): #Each tar file unzips to many .gz files; unzip the gzfiles
            base = os.path.basename(file)
            dest_name = os.path.join(snodas_renamed_files_dir, base[:-3]) #Put unzipped gz files into the re-named snodas directory
            with gzip.open(file,'rb') as infile:
                with open(dest_name,'wb') as outfile:
                    for line in infile:
                        outfile.write(line)

        all_snodas_variable_grids=os.listdir(snodas_renamed_files_dir)

        for item in all_snodas_variable_grids: #remove any files associated with variables we don't want (stored in "list_to_rm")
            for txt in list_to_rm:
                if txt in item:
                    os.remove(join(snodas_renamed_files_dir, item))
                    break
                
        for file in all_snodas_variable_grids: #Convert .dat files to .hdr files
            if file.endswith('.dat'):
                new_file = file[:-4]
                new_text_path = new_file + '.hdr'
                exp1= os.path.join(snodas_renamed_files_dir, new_text_path)
                shutil.copy(header_file, exp1) #copy the header file

        snodas_grids=os.listdir(snodas_renamed_files_dir) #swe and snow temp grids

        for item in snodas_grids:    #not sure if this is needed, but if there are any files left for variables we don't care about, then remove them.
            for txt in list_to_rm:
                if txt in item:
                    os.remove(join(snodas_renamed_files_dir, item))
                    break             

        os.chdir(snodas_renamed_files_dir)  
        fnames = listdir('.')
        for fname in fnames:
            if '11034' in fname:
                rename(fname, fname.replace('us_ssmv11034tS__T0001TTNATS', '', 1).replace('05HP001', '_SWE', 1))
            else:
                rename(fname, fname.replace('us_ssmv11034tS__T0001TTNATS', '', 1).replace('05HP001', '_SWE', 1))

        fnames2 = listdir('.')
        for fname in fnames2:
            if '11038' in fname:
                rename(fname, fname.replace('us_ssmv11038wS__A0024TTNATS', '', 1).replace('05DP001', '_Temp', 1))
            else:
                rename(fname, fname.replace('us_ssmv11038wS__A0024TTNATS', '', 1).replace('05DP001', '_Temp', 1))

        rasters = arcpy.ListRasters("", "DAT")
        for raster in rasters:
            arcpy.DefineProjection_management(raster, sr)
            new_raster = raster[:-4]
            new_raster_name = new_raster + '.tif'
            outname = os.path.join(processing_dir, new_raster_name)
            arcpy.CopyRaster_management(raster, outname ,"DEFAULTS","0","32767","","","32_BIT_FLOAT")

        arcpy.env.workspace = processing_dir
        rasters = arcpy.ListRasters("", "TIF")
        for raster in rasters:
            new_raster2 = raster[:-4]
            new_raster_name2 = new_raster2 + '_USGS' + '.tif'
            outname2 = os.path.join(processing_dir, new_raster_name2)
            arcpy.ProjectRaster_management(raster, outname2, sr2, "NEAREST", "2000 2000", "WGS_1984_(ITRF00)_To_NAD_1983", "", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
            new_raster_name3 = new_raster2 + '_USGS_Clip' + '.tif'
            outname3 = os.path.join(processing_dir, new_raster_name3)
            arcpy.Clip_management(outname2, "-2292000 2414000 -2088000 2532000", outname3, grid_shp, "-9999", "ClippingGeometry", "NO_MAINTAIN_EXTENT")

        arcpy.env.workspace = processing_dir
        rasters = arcpy.ListRasters("", "TIF")
        for raster in rasters:
            if raster.endswith('SWE_USGS_Clip.tif'):
                new_raster4 = raster[:-4]
                new_raster_name4 = new_raster4 + '_In' + '.tif'
                outname4 = os.path.join(processing_dir, new_raster_name4)
                invalue1= 1000
                invalue2 = 39.3701        
                outTimes = Raster(raster)/invalue1*invalue2
                outTimes.save(outname4)
                
                field = "VALUE"
                outpoint1 = outname4[:-4] + '_points.shp'
                arcpy.RasterToPoint_conversion(outname4, outpoint1, field)
                
                outzonal = outpoint1[:-4] + '_Join.shp'
                join_features = outpoint1
                arcpy.SpatialJoin_analysis(grid_shp, join_features, outzonal)
                
                outNewRaster = outzonal[:-4] + '_Raster.tif'
                arcpy.PolygonToRaster_conversion(outzonal, "GRID_CODE", outNewRaster, "CELL_CENTER", "NONE", "2000")

                ASCname = raster[:-4] + '_in_Grid.txt'
                outASC_SWE = os.path.join(final_asc_dir, ASCname)
                arcpy.RasterToASCII_conversion(outNewRaster, outASC_SWE)

        arcpy.env.workspace = processing_dir
        rasters = arcpy.ListRasters("", "TIF")
        for raster in rasters:
            if raster.endswith('Temp_USGS_Clip.tif'):
                new_raster5 = raster[:-4]
                new_raster_name5 = new_raster5 + '_F' + '.tif'
                outname5 = os.path.join(processing_dir, new_raster_name5)
                invalue1= 1.8
                invalue2 = 459.67
                outTimes = ((Raster(raster)*invalue1))-459.67
                outTimes.save(outname5)
                
                field = "VALUE"
                outpoint2 = outname5[:-4] + '_points.shp'
                arcpy.RasterToPoint_conversion(outname5, outpoint2, field)

                outzonal2 = outpoint2[:-4] + '_Join.shp'
                join_features = outpoint2
                arcpy.SpatialJoin_analysis(grid_shp, join_features, outzonal2)
                
                outNewRaster2 = outzonal2[:-4] + '_Raster.tif'
                arcpy.PolygonToRaster_conversion(outzonal2, "GRID_CODE", outNewRaster2, "CELL_CENTER", "NONE", "2000")

                ASCname = raster[:-4] + '_f_Grid.txt'
                outASC_CCATI = os.path.join(final_asc_dir, ASCname)
                arcpy.RasterToASCII_conversion(outNewRaster2, outASC_CCATI)

        print("Finished processing raw SNODAS data for SWE and CCATI (snow temperature) grids")
        time.sleep(5)

        ### Create snow grids for CWMS
        copyfile(outASC_SWE,os.path.join(SNOW_GRIDS_FOR_CWMS,os.path.basename(outASC_SWE)))
        copyfile(outASC_CCATI,os.path.join(SNOW_GRIDS_FOR_CWMS,os.path.basename(outASC_CCATI)))

        arcpy.env.workspace = SNOW_GRIDS_FOR_CWMS

        processed_files = glob.glob(os.path.join(SNOW_GRIDS_FOR_CWMS,'*USGS*.txt'))
        SNODAS_date = start_date.strftime("%Y%m%d")

        with open(processed_files[0]) as myfile:
            head= [next(myfile) for x in xrange(6)]
        header = ''.join(head)

        #Make liquid water grid
        print("Making liquid water grid...")
        time.sleep(5)

        lqw_grid_name = os.path.join(SNOW_GRIDS_FOR_CWMS,str(SNODAS_date+'_LQW_in.txt'))
        array = np.loadtxt(processed_files[0],skiprows=6)
        lqw_array = array*0.0 #Set liquid water array equal to 0
        np.savetxt(lqw_grid_name,lqw_array,delimiter=" ",fmt='%1.1f') #Save lqw grid
        line_prepender(lqw_grid_name,header)#Add header to top of grid txt file
        ##NOTE: According to documentation (3.1.38_Snowmelt_for_Corps_Water_Management_Systems_2018.docx): "If the simulation begins during the melt period, the error in setting the initial value to zero may cause a delay in melt runoff."

        #Make cold content grid
        print("Making cold content grid...")
        time.sleep(5)

        cc_grid_name=os.path.join(SNOW_GRIDS_FOR_CWMS,str(SNODAS_date+'_CC_in.txt'))
        swe_array_in = np.loadtxt(outASC_SWE,skiprows=6)
        temp_array_degF = np.loadtxt(outASC_CCATI,skiprows=6) #SNODAS temp grid in deg F
        temp_array_degC = (temp_array_degF-32.00)*(5.00/9.00)#convert temp grid to deg C
        tbase = 0 #Melting point of ice = 0 deg C
        Lf=334000 #Latent heat of fusion of water = 334,000 J/kg
        Cp=2100 #Specific heat of ice = 2100 J/kg-degC
        CC_array = (np.multiply((swe_array_in*float(Cp)),(temp_array_degC-float(tbase))))/float(Lf) #calculate cold content (in) = SWE(in) x Cp x (Tavg-Tbase)/Lf
        CC_array[CC_array==-0.]=0.00 #Set all -0 values to 0 in array
        np.savetxt(cc_grid_name,CC_array,delimiter=" ",fmt='%1.4f') #Save cold content grid
        line_prepender(cc_grid_name,header) #Add header to top of grid txt file

        #Make meltrate ATI (MRATI) grid
        mrati_grid_name = os.path.join(SNOW_GRIDS_FOR_CWMS,str(SNODAS_date+'_MRATI_degFdays.txt'))

        if spring_melt =='Y' and extract_date!=start_date:
            print("Making melt rate ATI grid: spring melt conditions; calculate accumulated degree days...")
            time.sleep(5)
            
            t1 = extract_date + timedelta(hours=1) #first temp grid in dss
            t2 = start_date #last temp grid in dss
            dif = int((t2-t1).total_seconds()/3600) ## time difference in hours

            datetime_list = [(t1 + timedelta(hours=x)).strftime("%d%b%Y:%H%M") for x in range(dif+1)]

           
            temp_asc_folder = os.path.join(dir_forecast,'temp_asc_pre-lookback')
            if not os.path.exists(temp_asc_folder):
                os.mkdir(temp_asc_folder)
            else:
                shutil.rmtree(temp_asc_folder)
                os.mkdir(temp_asc_folder)
                
            avg_daily_temp_folder = os.path.join(dir_forecast,'avg_daily_temp-prelookback')
            if not os.path.exists(avg_daily_temp_folder):
                os.mkdir(avg_daily_temp_folder)
            else:
                shutil.rmtree(avg_daily_temp_folder)
                os.mkdir(avg_daily_temp_folder)
            
            os.chdir(dir_forecast)
            print("Making asciis from forecast.dss for temperature grids during pre-lookback period...(i.e. extract start time through model start time)")    
            time.sleep(5)
            
            for date in datetime_list:
                date = str(date).upper()
                path=str('/SHG/ROGUE/TEMP/'+date+'//GINTERP/')
                asc_name = str('temp_'+date.replace(':','')+'.asc')
                command_output=str('OUTPUT='+os.path.basename(temp_asc_folder)+'\\'+asc_name)
                command_dss = str('dss=forecast.dss')
                command_path=str('path='+path)
                subprocess.call(["dss2ascGrid.exe",command_output,command_dss,command_path])
            os.chdir(cwd)

            asc_to_move = glob.glob(os.path.join(dir_forecast,'*.asc'))
            for asc in asc_to_move:
                os.rename(asc,os.path.join(temp_asc_folder,os.path.basename(asc)))

            #Calculate average daily temperature
            print("Calculating grids of average daily temperature")
            date_list = [(datetime.datetime.strptime(x,"%d%b%Y:%H%M")).strftime("%d%b%Y") for x in datetime_list]
            date_list = sorted(set(date_list))
            for date in date_list:
                date = str(date).upper()
                asc_list = glob.glob(os.path.join(temp_asc_folder,'*'+date+'*.asc'))
                stack=[]
                for asc in asc_list:
                    array = np.loadtxt(asc,skiprows=6) #load the temperature asc for the hour of the day selected
                    stack.append(array)
                stack=np.array(stack)
                stack_avg = np.average(stack,axis=0)
                np.savetxt(os.path.join(avg_daily_temp_folder,'avg_temp_'+date+'.asc'),stack_avg,delimiter=" ",fmt='%1.2f')
                line_prepender(os.path.join(avg_daily_temp_folder,'avg_temp_'+date+'.asc'),header)

            #Calculate total accumulated degree days for lookback period
            print("Calculating grid of total accumulated degree-days for pre-lookback period to create melt rate ATI grid")
            avg_daily_temp_grids = glob.glob(os.path.join(avg_daily_temp_folder,'*.asc'))
            stack_degdays = []
            for grid in avg_daily_temp_grids:
                array = np.loadtxt(grid,skiprows=6) #load the avg daily temp grid
                degdays = array-32 #calculate the difference between the temperature and freezing (32 deg F)
                degdays[degdays<0]=0 #set any negative values equal to 0
                stack_degdays.append(degdays)
            stack_degdays=np.array(stack_degdays)
            accum_degdays = np.sum(stack_degdays,axis=0)
            print("Making melt rate ATI grid...")
            time.sleep(5)
            
            np.savetxt(mrati_grid_name,accum_degdays,delimiter=" ",fmt='%1.2f')
            line_prepender(mrati_grid_name,header)
                             
        if (spring_melt =='Y' and extract_date == start_date) or (spring_melt == 'N'): #If not yet spring melt conditions, can set MRATI to 0.
            print("Making melt rate ATI grid (grid of 0s; conditions non-spring-melt...")
            time.sleep(5)
            
            array = np.loadtxt(processed_files[0],skiprows=6)
            mrati_array = array*0.0 #Set mrati array equal to 0
            np.savetxt(mrati_grid_name,mrati_array,delimiter=" ",fmt='%1.1f') #Save lqw grid
            line_prepender(mrati_grid_name,header)#Add header to top of grid txt file

        ##Add snow grids to forecast.dss
        snow_files = glob.glob(os.path.join(SNOW_GRIDS_FOR_CWMS,'*.txt'))
        for file in snow_files:
            shutil.copy2(file,os.path.join(dir_forecast,os.path.basename(file)))

        os.chdir(dir_forecast)

        snow_files_for_forecast = glob.glob(os.path.join(dir_forecast,'*.txt'))

        datetime_x = (start_date.strftime("%d%b%Y:%H%M")).upper()
        #datetime_x = str(datetime_x).upper()

        command_dssfile=str('DSSFILE=forecast.dss')
        command_dtype = 'DTYPE=INST-VAL'
        command_gridtype = 'GRIDTYPE=SHG'
        pathname = str('/SHG/ROGUE/PARAM_X/'+datetime_x+'//SNODAS/')

        for file in snow_files_for_forecast:
            input_file = os.path.basename(file)

            if 'CC' in input_file:
                param_x = 'COLD CONTENT'
                unit = 'IN'
            elif 'LQW' in input_file:
                param_x = 'LIQUID WATER'
                unit = 'IN'
            elif 'MRATI' in input_file:
                param_x = 'MELTRATE ATI'
                unit = 'DEGF-D'
            elif 'SWE' in input_file:
                param_x = 'SWE'
                unit = 'IN'
            elif 'Temp' in input_file:
                param_x = 'COLD CONTENT ATI'
                unit = 'DEG F'
            else:
                print(str(input_file+" does not have an associated snow grid parameter"))
                time.sleep(5)
                

            pathname_param = pathname.replace('PARAM_X',param_x)
            command_input = str('INPUT='+input_file)
            command_pathname = str('PATHNAME='+pathname_param)
            command_dunits = str('DUNITS='+unit)
            print(str("Putting "+input_file+" in forecast.dss as "+param_x))
            time.sleep(2)
            subprocess.call(["asc2dssGrid.exe",command_input,command_dssfile,command_pathname,command_gridtype,command_dtype,command_dunits])
            os.remove(file)

        os.chdir(cwd)

    print("FINISHED")
    time.sleep(2)
    exit_terminal = raw_input('Exit terminal window? (Y/N): ').upper()
    if exit_terminal == 'Y':
        print("Exiting terminal window..........")
        time.sleep(5)
        sys.exit()

except Exception as e:
    logging.exception("ERROR MESSAGE:")
finally:
    pass

