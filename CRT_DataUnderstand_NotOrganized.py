# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 09:54:37 2021

NOTE: The code is not organized!!! :(

Some of the things the code do are:
    - Create a shapefile for the calibration sites that we couldn't connect to a dam.
    - Merge the dam shapefile and the above calibration sites and join the reach and\
        subbasin information into it.
    - check which one of the calibration sites are in dam shape file, flow file, ...
    - Compare PNW unimpaired with and with out Natural Lake by generating a 3x1 plots 
@author: sardekani
"""

import sys
import geopandas
import pandas as pd
import matplotlib.pyplot as plt
import re
from shapely.geometry import Point

direc='C:/Users/SARDEKANI/Documents/USACE_Seattle/'
reachSHP=direc+'GIS/Shapefile/crb_reaches_albers_nad83_m.shp'
subbasinSHP=direc+'GIS/Shapefile/crb_subbasins_shg.shp'
damSHP=direc+'GIS/Shapefile/Columbia_Basin_PNRS_Dams.shp'
DSS_partA=direc+'Data/DSS_flow_PartA.csv'
IncrInf=direc+'Data/PNW_unimpaired_flow_v1.1/incremental_inflow_v1.0.csv'
PNW_unim_with=direc+'Data/PNW_unimpaired_flow_v1.1/PNW_unimpaired_flow_naturallakes_v1.1.csv'
PNW_unim_without=direc+'Data/PNW_unimpaired_flow_v1.1/PNW_unimpaired_flow_without_naturallakes_v1.1.csv'
MOD=direc+'Data/2020MODFLOW_URC_MODELINPUT.csv'
precip='C:/Users/SARDEKANI/Documents/USACE_Seattle/Data/daily_precip_wc_2021_10_10.csv'
SWE='C:/Users/SARDEKANI/Documents/USACE_Seattle/Data/swe_day_snodas_2021_10_11_sqlcl.csv'
SnowD='C:/Users/SARDEKANI/Documents/USACE_Seattle/Data/snow_depth_day_snodas_2021_10_11_sqlcl.csv'


df_DSS_PartA=pd.read_csv(DSS_partA)
df_DSS_PartA['DSS_FLOW']=df_DSS_PartA['DSS_FLOW'].str.lower()
df_IncrInf=pd.read_csv(IncrInf,index_col=['Unnamed: 1'],parse_dates=True, header=6)
df_IncrInf.columns=pd.read_csv(IncrInf).columns[1:]
df_MOD=pd.read_csv(MOD,index_col=['Unnamed: 1'],parse_dates=True, header=6)
df_MOD.columns=pd.read_csv(MOD).columns[1:]
df_PNW_with=pd.read_csv(PNW_unim_with,index_col=['Unnamed: 1'],parse_dates=True, header=6)
df_PNW_out=pd.read_csv(PNW_unim_without,index_col=['Unnamed: 1'],parse_dates=True, header=6)
df_PNW_with.columns=pd.read_csv(PNW_unim_with).columns[1:]
df_PNW_out.columns=pd.read_csv(PNW_unim_without).columns[1:]
df_SWE=pd.read_csv(SWE)
df_SnowD=pd.read_csv(SnowD)
df_precip=pd.read_csv(precip)

# Calibration points in the proposal document
HMS_Mod=['mica', 'revelstoke','arrow','duncan', 'priest lake', 'boundary', 'noxon', 'grand coulee',\
         'chief joseph', 'rocky reach','wanapum', 'priest rapids', 'cle elum', 'keechelus', 'kachess',\
             'bumping lake','libby','kerr','coeur dalene','albeni falls', 'jackson lake','american falls',\
                 'brownlee', 'dworshak','lower granite', 'ice harbor', 'pelton', 'bonners ferry', 'columbia falls'\
                     ,'corra linn', 'spalding','kiona']
    
# HMS_Mod=['mica', 'revelstoke','arrow lakes','duncan', 'priest lake', 'boundary', 'noxon rapids', 'grand coulee',\
#          'chief joseph', 'rocky reach','wanapum', 'priest rapids', 'cle elum', 'keechelus', 'kachess',\
#              'bumping lake','libby','kerr','coeur dalene','albeni falls', 'jackson lake','american falls',\
#                  'brownlee', 'dworshak','lower granite', 'ice harbor', 'pelton', 'bonners ferry', 'columbia falls'\
#                      ,'corra linn', 'spalding','kiona']

# REad DAm Shapefile
gd=geopandas.read_file(damSHP)
dam_shp=pd.DataFrame(gd.drop(columns='geometry'))
dam_shp['Dam_name']=dam_shp['Dam_name'].str.lower()


# Generate a shape file for the 5 sites that are not in dam shape file
site=['bonners ferry','coeur dalene', 'columbia falls', 'kiona','spalding']
lat=[48.697693,47.675368,48.3769,46.274622,48.367611]
lon=[-116.3123,-116.80379,-114.1831,-119.478813,-119.582826]
df_point=pd.DataFrame(zip(site,lat,lon), columns=['site','lat','lon'])
df_point['geometry'] = df_point.apply(lambda x: Point((x.lon, x.lat)),axis = 1)
crs_dam = gd.crs
point_gdb = geopandas.GeoDataFrame(df_point,crs = crs_dam,geometry = df_point.geometry)
point_gdb['calibration_site']='Yes'
path=direc+'GIS/Shapefile/sitesNotInDamsShp.shp'
point_gdb.to_file(path)

# merge dam shapefile with 
# Add 'calibration_site' column to shp and put 'Yes' if it represents a calibration point
gd['Dam_name']=gd['Dam_name'].str.lower()
l=list(gd['Dam_name'])
l.sort()
k=[]
gd['calibration_site']='No'
for i in HMS_Mod:
    new_list = [x for x in l if re.search(i, x)]
    if len(new_list) >0: 
        gd.loc[gd[gd['Dam_name']==new_list[0]].index[0],'calibration_site']='Yes'
        k.append(new_list[0])
        print(new_list)
    else: print(i)   
# Change the 'Dam_name' column to 'site'
names = gd.columns.tolist()
names[names.index('Dam_name')] = 'site'
gd.columns = names
# merge two shp
new_gd=gd.append(point_gdb)
# Spatial join, add reach and subbasin information 
gd_reach=geopandas.read_file(reachSHP)
gd_reach.columns=["HMS_Model",'ReachID','geometry']
gd_subbasin=geopandas.read_file(subbasinSHP)
gd_reach_reproj=gd_reach.to_crs(new_gd.crs)
gd_subbasin_reproj=gd_subbasin.to_crs(new_gd.crs)
joined1 = geopandas.sjoin(new_gd,gd_reach_reproj,op="within")
joined1 = joined1.drop(['index_right'], axis=1)
joined2 = geopandas.sjoin(joined1,gd_subbasin_reproj[['SubbasinID','Name','geometry']],op="within")
joined2=joined2.rename(columns={'Name':'SubasinName'})
path=direc+'GIS/Shapefile/DamsWithRemaingSite_WithReachSubInfo.shp'
joined2.to_file(path)
# Select only calibration site and sort the df based on 'site'
path2=direc+'GIS/Shapefile/CalibrationSite_WithReachSubInfo.shp'
junction='C:/Users/SARDEKANI/Documents/USACE_Seattle/WEST/Junction1.csv'
df_junc=pd.read_csv(junction, encoding='utf-8')
df_junc.columns=['site', 'DownStream', 'ds_element']
gd_site=joined2[joined2['calibration_site']=='Yes']
gd_site=gd_site.merge(df_junc, on='site')
gd_site.to_file(path2)
gd_crop=joined2[joined2['calibration_site']=='Yes'][['site','HMS_Model', 'ReachID','SubbasinID', 'SubasinName']]
gd_crop=gd_crop.sort_values('site')

# Generate plot
fig, ax=plt.subplots(1,figsize=[12,8],dpi=400)
joined2[joined2['calibration_site']=='Yes'].plot(ax=ax,c='red',marker='p')
gd_subbasin_reproj.plot(ax=ax,facecolor="none",edgecolor='yellow')
gd_reach_reproj.plot(ax=ax,facecolor="none",edgecolor='blue')
img=direc+'plot/Map.jpg'

plt.savefig(img)
plt.close()   
plt.show()


# Compare PNW unimpaired with and with out Natural Lake
for i in df_PNW_with.columns[1:]:
    print(i)
    col1=df_PNW_with.loc[:, i]
    col2=df_PNW_out.loc[:, i]

    fig=plt.figure(3)
    fig.set_figheight(12)
    fig.set_figwidth(8)
    
    ax1 = plt.subplot(311)
    ax1.plot(col1,col2,marker='.')
    plt.xlabel('PNW_unimpaired_flow_naturallakes')
    plt.ylabel('PNW_unimpaired_flow_without_naturallakes')
    ax1.plot([-10000,100000],[-10000,100000],'--', color='red')
    plt.title(i)
    ax2 = plt.subplot(312)
    ax2.plot(col1)
    ax2.legend(['with Natural lakes'])
    ax3 = plt.subplot(313)
    ax3.plot(col2)
    ax3.legend(['without Natural lakes'])
    img=direc+'plot/PNW/'+i+'.jpg'
    
    plt.savefig(img)
    plt.close()    


df_MOD=df_MOD[df_IncrInf.index[0]:df_IncrInf.index[-1]]
for i in df_MOD.columns[1:]:
    col=df_IncrInf.loc[:, df_IncrInf.columns.str.startswith(i)]

    if len(col.columns)>0:
        fig=plt.figure(3)
        fig.set_figheight(12)
        fig.set_figwidth(8)
        
        ax1 = plt.subplot(311)
        ax1.plot(df_MOD[i],col)
        plt.xlabel('DSS-Flow')
        plt.ylabel('csv_incrementalFlow')
        ax1.plot([-10000,100000],[-10000,100000],'--', color='red')
        plt.title(i+' - '+col.columns[0])
        ax2 = plt.subplot(312)
        ax2.plot(df_MOD[i])
        ax2.legend(['DSS MOD FLOW'])
        ax3 = plt.subplot(313)
        ax3.plot(col, label='CSV ELEV Incre FLOW')
        ax3.legend(['CSV ELEV Incre FLOW'])
        img=direc+'plot/'+i+'.jpg'
        
        plt.savefig(img)
        plt.close()
    else:
        print('No Incremental', i)
        """
        No Incremental ANATONE
        No Incremental ARROW LAKES
        No Incremental BOX CANYON
        No Incremental LIME POINT
        No Incremental LITTLE FALLS
        No Incremental OROFINO
        No Incremental SLOCAN
        No Incremental THE DALLES.1
        No Incremental WHITEBIRD
        No Incremental YAKIMA"""
 
    
"""
MOD DSS list:
    
'ALBENI FALLS', 'ANATONE', 'ARROW LAKES',
       'BONNERS FERRY', 'BONNEVILLE', 'BOUNDARY', 'BOX CANYON', 'BRILLIANT',
       'BROWNLEE', 'CABINET GORGE', 'CHELAN', 'CHIEF JOSEPH', 'COLUMBIA FALLS',
       'CORRA LINN', 'DUNCAN', 'DWORSHAK', 'GRAND COULEE', 'HELLS CANYON',
       'HUNGRY HORSE', 'JOHN DAY', 'KERR', 'LIBBY', 'LIME POINT',
       'LITTLE FALLS', 'LOWER GRANITE', 'LOWER MONUMENTAL', 'MCNARY', 'MICA',
       'NOXON RAPIDS', 'OROFINO', 'POST FALLS', 'PRIEST LAKE', 'PRIEST RAPIDS',
       'REVELSTOKE', 'ROCK ISLAND', 'ROCKY REACH', 'SEVEN MILE', 'SLOCAN',
       'SPALDING', 'THE DALLES', 'THE DALLES.1', 'THOMPSON FALLS',
       'UPPER FALLS', 'WELLS', 'WHITEBIRD', 'YAKIMA'
       
   """
   

    
#arrow->arrow lakes
#noxon->noxon rapids
# ???? 'chelan' is the same as 'cle elum'


gd=geopandas.read_file(reachSHP)
df_reach_shp=pd.DataFrame(gd.drop(columns='geometry'))
df_reach_shp['Reach_modify']=df_reach_shp['Reach'].str.replace( r"([A-Z])", r" \1").str.strip()
df_reach_shp['Reach_modify']=df_reach_shp['Reach_modify'].str.lower()

gd1=geopandas.read_file(subbasinSHP)
df_subbasin_shp=pd.DataFrame(gd1.drop(columns='geometry'))

for i in df_subbasin_shp.columns:
    print(i,df_subbasin_shp[i].min(),df_subbasin_shp[i].max())
    
    
l=list(df_DSS_PartA['DSS_FLOW'])
for i in HMS_Mod:
    if i not in l: print(i)

    
for i in df_reach_shp['Reach_modify']:
    if i in l: print('Yes')
    else: print (i)
    
    
l=list(dam_shp['Dam_name'])
l.sort()
k=[]
for i in HMS_Mod:
    new_list = [x for x in l if re.search(i, x)]
    if len(new_list) >0: 
        k.append(new_list[0])
        print(new_list)
    else: print(i)
        
k=[x.upper() for x in k]
    
gd=geopandas.read_file(damSHP)
gd_crop=gd[gd['Dam_name'].isin(k)]
damSHP2=direc+'GIS/Shapefile/Columbia_Basin_PNRS_Dams_intersect_CAlibrationPoint.shp'
gd_crop.to_file(damSHP2)

gd_reach=geopandas.read_file(reachSHP)
gd_reach_reproj=gd_reach.to_crs(epsg=4326)

gd_crop.intersection(gd_reach)
fig,ax=plt.subplots(figsize=(12,6))
gd_crop.plot(ax=ax, color='r')
gd_reach_reproj.plot(ax=ax)


l=list(df_PNW_with.columns.str.lower())
for i in HMS_Mod:
    new_list = [x for x in l if re.search(i, x)]
    if len(new_list)>0:
        print(new_list)
    else:
        print(i)
        
l=list(df_PNW_out.columns.str.lower())
for i in HMS_Mod:
    new_list = [x for x in l if re.search(i, x)]
    if len(new_list)>0:
        print(new_list)
    else:
        print(i)


"""
Missing drainage area from HEC-DSS flow:
arrow
noxon
rockey reach
wanapum
cle elum
keechelus
kachess
bumping lake
coeur dalene
jackson lake
american falls
ice harbor
pelton
kiona
"""


df_MOD=df_MOD[df_IncrInf.index[0]:df_IncrInf.index[-1]]
for i in df_MOD.columns[1:]:
    col=df_IncrInf.loc[:, df_IncrInf.columns.str.startswith(i)]

    if len(col.columns)==0:
        print('No Incremental', i)
        
