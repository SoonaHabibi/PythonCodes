# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 10:54:00 2019

@author: sardekani
"""
import pandas as pd
import csv
import datetime
from datetime import datetime, timedelta
path = '//westfolsom/projects/2019/UmpquaRiver/Precipitation_Temperature/common2/original\\C5302.2019-08-19.csv'

try:
    DF1 = pd.read_csv(path)
    DF1['date'] = pd.to_datetime(DF1['date'])
    DF1['date'] = DF1['date'].dt.tz_localize(None)                             #remove the time zone
except:
    station = path[path.index('\\')+1:path.index('\\')+5]
    head_num = 0
    with open(path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if (row[0][0:4]!=station):
                head_num = head_num + 1
            else:
                head_num = head_num - 1
                break
    DF1 = pd.read_csv(path, header = head_num)
col = ['station', 'date', 'Fahrenheit', 'Inches', 'Inches.1','Inches.2']
DF1.columns = col
DF1.set_index(['date'])
raincum = DF1['Inches.2']
date = DF1['date']
