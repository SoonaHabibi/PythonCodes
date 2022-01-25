# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 11:33:15 2019

@author: sardekani
"""
import pandas as pd
import sys
sys.path.append("//westfolsom/Office/Python/WEST_Python_FunctionAug2019");
import BasicFunction_py3 as BF

month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul','Aug', 'Sep','Oct','Nov','Dec']
Dir = "D:/CouleeDam/"

for i in range(0,len(month)):
    infile = Dir + month[i] + '.csv'
    df = pd.read_csv(infile)
    x = df.iloc[:,0].apply(lambda x: int(x))
    y = df.iloc[:,1].apply(lambda x: x/1000000)
    labelx = 'Year'
    labely = month[i] + ' Max inFlow Vol (Acf*10^6)'
    labely = month[i] + ' Max inFlow Vol ()'
    Outplot = Dir + month[i] + '.jpg'
    pvalue, Slope, Interc = BF.PlotLinearRelationship(x,y,labelx,labely,Outplot)
    print(month[i],': ', pvalue, Slope, Interc)


# remove the trend using last year and the last 10 years as a reference
for i in range(0,len(month)):
    infile = Dir + month[i] + '.csv'
    df = pd.read_csv(infile)
    x = df.iloc[:,0].apply(lambda x: int(x))
    y = df.iloc[:,1]
    labelx = 'Year'
    #labely = month[i] + ' Max inFlow Vol (Acf*10^6)'
    labely = month[i] + ' Max inFlow Vol ()'
    #Outplot = Dir + month[i] + '.jpg'
    Outplot = Dir+ 'plot_ac_ft/' + month[i] +'_acf.jpg'
    pvalue, Slope, Interc = BF.PlotLinearRelationship(x,y,labelx,labely,Outplot)
    print(month[i],': ', pvalue, Slope, Interc)
    
    if pvalue<0.05:             #remove the trend      
        # remove the trend
        # variables ending with one/1 are those detrending based on the last year
        # variables ending with two/2 are those detrending based on the 10 last year
        yref1 = Slope*x.tail(1)+Interc
        cor1 = x.apply(lambda x: yref1-(Slope*x+Interc))
        yfinal1 = cor1.iloc[:,0].add(y)
        df1 = pd.concat([x,yfinal1],axis=1)
        df1.columns=['year','flow volume(ac-ft)']

        labely1 = month[i] + ' detrend Max inFlow Vol (ac-ft *10^6)'
        labely2 = month[i] + ' detrend Max inFlow Vol (ac-ft*10^6)'
        Outplot1 = Dir+ 'plot_ac_ft/' + month[i] +'_detrend_ref_last_yr.jpg'
        Outplot2 = Dir+ 'plot_ac_ft/' + month[i] +'_detrend_ref_last_10yrs.jpg'
        
        yref2 = (Slope*x.tail(10)+Interc).mean()
        cor2 = x.apply(lambda x: yref2-(Slope*x+Interc))
        yfinal2 = cor2.add(y)
        df2 = pd.concat([x,yfinal2],axis=1)
        df2.columns=['year','flow volume(ac-ft)']
        
        
        pvalue1, Slope1, Interc1 = BF.PlotLinearRelationship(x,yfinal1/1000000,labelx,labely1,Outplot1)
        pvalue2, Slope2, Interc2 = BF.PlotLinearRelationship(x,yfinal2/1000000,labelx,labely2,Outplot2)
        
        print(month[i],': ', pvalue1, Slope1, Interc1)
        print(month[i],': ', pvalue2, Slope2, Interc2)
        
        out1 = "D:/CouleeDam/detrend/"+month[i]+'_refe_lastyear.csv'
        out2 = "D:/CouleeDam/detrend/"+month[i]+'_refe_10lastyears.csv'
        df1.to_csv(out1, index=False)
        df2.to_csv(out2, index=False)
        
        
# remove the trend using last year and the last 10 years as a reference
for i in range(0,len(month)):
    infile = Dir + month[i] + '.csv'
    df = pd.read_csv(infile)
    x = df.iloc[:,0].apply(lambda x: int(x))
    y = df.iloc[:,1]
    labelx = 'Year'
    labely = month[i] + ' Max inFlow Vol ()'
    Outplot = Dir+ 'plot_ac_ft/' + month[i] +'_acf.jpg'
    pvalue, Slope, Interc = BF.PlotLinearRelationship(x,y,labelx,labely,Outplot)
    print(month[i],': ', pvalue, Slope, Interc)
    
    if pvalue<0.15:             #remove the trend      
        # remove the trend
        # use the middle year as a refrence
        yref = Slope*x.tail(round(len(x)/2))+Interc
        cor = x.apply(lambda x: yref-(Slope*x+Interc))
        yfinal = cor.iloc[:,0].add(y)
        df = pd.concat([x,yfinal],axis=1)
        df.columns=['year','flow volume(ac-ft)']

        labely = month[i] + ' detrend inFlow Vol (ac-ft *10^6)'

        Outplot = Dir+ 'plot_ac_ft/' + month[i] +'_detrend_ref_middle_yr.jpg'

        pvalue, Slope, Interc = BF.PlotLinearRelationship(x,yfinal/1000000,labelx,labely,Outplot)
        
        print(month[i],': ', pvalue, Slope, Interc)
        
        out = "D:/CouleeDam/detrend/"+month[i]+'_refe_middleyear.csv'
        df.to_csv(out, index=False)