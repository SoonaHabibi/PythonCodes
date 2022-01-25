 # -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 12:53:06 2020
Updated on Mon Dec             2021

@author: lotto
"""

import pandas as pd #important
import numpy as np
import glob 
import re
import collections as co
import matplotlib.pyplot as plt
import datetime
import time
import math
import warnings
warnings.filterwarnings("ignore")

''' for this example, the column names were Reading, Receive, Gauge 2547, Unit, Data Quality, and Accum
    make sure to delete any mention of these columns in the code if your Alert data does not have those columns
    make sure to properly rename any columns if your alert data uses another name
'''

save_switch = 'True'
save_switch = 'False'

InFolder = "//WESTFOLSOM/Projects/2020/Meyers Nave/Python/"#"AllStations/"
OutFolder = "//WESTFOLSOM/Projects/2020/Meyers Nave/Python/Out"

#pay attention to parse_dates, index_col, the 0 corresponds to the first column in the csv file being read in
data = pd.read_csv(InFolder+"2547_onerain_Montecito.csv", sep=',',parse_dates=[0],index_col=[0]) 
data['tvalue'] = data.index #create column from the "Reading" index column for further manipulation
data['tvalue'] = data['tvalue'].dt.round('Min') #round this new column to the minute - get rid of seconds

data_old = data #keep track of Raw data
# data = data_old
data.index = data.index.round('min')
data_new = data.sort_values('Gauge 2547') #sort by the tip values, not sure why I did this

#these lines start looking at "duplicate tips" aka series of tips that happen in a minute
data_series = data_new.duplicated('tvalue', keep=False)
data_new['TF'] = data_series #add new column that has a boolean regarding if there is one or more tip in a minute
data_new = data_new.sort_values('tvalue') #sort by time

data = data_new.reset_index()
data = data.loc[~data.TF,:] #here is a dataframe without any of those "duplicate tips"
data = data.reset_index()
data = data.drop('tvalue', axis=1)

data0 = data_new.reset_index()
data0 = data0.loc[data0.TF,:] #here is a dataframe with only the "duplicate tips"
data0 = data0.reset_index()

dfmax = data0.groupby(['tvalue']).max()
dfmin = data0.groupby(['tvalue']).min()
dfsum = data0.groupby(['tvalue']).sum()
df = dfmax.copy() #used the maximum value for the entire new dataframe - most important that the Accum is the max
df['index'] = dfmin['index'] #not important, but I used the minimum duplicate for the index.
df['Gauge 2547'] = dfsum['Gauge 2547'] #very important, the tip increment must be the sum

data = pd.concat([data, df]) #combine the without duplicates and with duplicates back together
                             #all of the duplicates are at the bottom currently

del dfmin, dfmax, dfsum, df 
del data_series, data_new, data0, data_old

data['tvalue'] = data['Reading'] #recreate the tvalue variable and use time of Reading for that
data = data.set_index('Reading') #set index back to Reading
data = data.drop(['TF','index'], axis=1)
data = data.sort_values('tvalue') #sort chronologically

#find the "delta," the time difference between two tips
data['delta'] = (data['tvalue']-data['tvalue'].shift()).fillna(pd.Timedelta('0 days'))
#convert that "delta" to minutes - !!! make sure that the value following the % sign is large enough - example if the delta is 27 minutes but your value is only 24 minutes, the min will show up as 3 minutes
data['min'] = data['delta'].apply(lambda x: x  / np.timedelta64(1,'m')).astype('int64') % (24*60*60*366*32)

data['min'][0] = 10 #assume that the first tip accumulated over ten minutes - assume all other tips accumulated over the time between the tip and the previous tip

###

InitialDate=datetime.date(data.index.min().year,data.index.min().month, data.index.min().day)

#RainInt dataframe will span from the initial date called out above and one minute after the last tip    
RainInt=pd.DataFrame(index=pd.date_range(start=InitialDate, end=data.index.max()+datetime.timedelta(minutes = 1),freq='min'))
RainInt['RainIntensity'] = np.nan #create a column to be back-filled by the tips
RainInt['tvalue'] = RainInt.index
RainInt['time_step'] = RainInt['tvalue']

# pd.DataFrame.head(RainInt)
#merge the empty RainInt dataframe with the alert "data" dataframe
RainInt = pd.merge(left=RainInt, right=data, how='left', left_on='tvalue', right_on='tvalue')
RainInt = RainInt.set_index('time_step')

#drop unnecessary columns
RainInt = RainInt.drop(["Receive","Unit","Data Quality",'Accum'], axis=1) 

#start the "back filling"
start_time = time.time()

for i in range(0,len(data)-1):
    
    if ( (data['Gauge 2547'][i+1]!=0) and (data['Gauge 2547'][i]==0) and (data['min'][i+1]>180) ): 
        #if there is a 0 and the next non0 comes 3 hours later, assume that tip is 
            #back-distributed by 10 minutes and not the time between the current tip and previous tip
        ten_minutes = datetime.timedelta(minutes=10)
        
        RainInt['RainIntensity'][ data['tvalue'][i]:data['tvalue'][i+1]-ten_minutes ] = 0
        RainInt['RainIntensity'][ data['tvalue'][i+1]-ten_minutes:data['tvalue'][i+1] ] = data['Gauge 2547'][i+1]/10
    
    else: #else assume that the tip is back-distributed by the time between current and previous tip
        RainInt['RainIntensity'][ data['tvalue'][i]:data['tvalue'][i+1] ] = data['Gauge 2547'][i+1]/data['min'][i+1]
        
    ten_minutes = datetime.timedelta(minutes=10)  
    one_minute  = datetime.timedelta(minutes=1)   
    RainInt['RainIntensity'][ data['tvalue'][0]-ten_minutes:data['tvalue'][0]-one_minute ] = data['Gauge 2547'][0]/10


end_time = time.time()

RainInt.dropna(subset = ["RainIntensity"], inplace=True) #remove rows based on if the RainIntensity is a nan
RainInt['RainIntensity'][-1] = np.nan #this zero should be a nan

RainInt = RainInt.drop(["delta"], axis=1)
RainInt = RainInt.rename(columns={"min": "delta","Gauge 2547": "tip"})

# print(end_time-start_time)
del end_time, start_time

del i, InFolder, InitialDate, ten_minutes, one_minute 


if save_switch == "True":
    RainInt.to_csv(OutFolder+"/RainInt_"+"gauge_2547.txt")
    print('saved')
elif save_switch == "False":
    print('not saved')
    
del OutFolder, save_switch


#just added for MR 12/13/2021
RainInt_usable = RainInt.set_index('tvalue')
Resamp = RainInt_usable['RainIntensity'].resample('1H', label='right').sum()

    