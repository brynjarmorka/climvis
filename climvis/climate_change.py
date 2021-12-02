# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 09:54:53 2021

@author: leopo
if this file is called, the user should get additional information if/how the
choosen location is affected by the climate change. The user gets asked if he/she 
wants climate change information and if yes is given as an input, this file is
called.
for input shoud be asked in the .cli file
data is read in in the .cfg file
"""
import numpy as np
import xarray as xr
from climvis import cfg, core, graphics
import matplotlib.pyplot as plt
#from sklearn.linear_model import LinearRegression

#lon = 12
#lat = 45
#def timeseries(lon, lat):
    #df = core.get_cru_timeseries(lon, lat)
    #return df

def calculate_mean(df, startyear, endyear):
    #divide the timeseries in two parts
    startyear = str(startyear)
    endyear = str(endyear)
    
    df = df.loc[startyear:endyear]
    df = df.groupby(df.index.year).mean()
    df.index = list(range(int(startyear), int(endyear)+1, 1))
    
    #compute the mean anual temperature over the timeseries
    mean_anual_tmp = df.tmp.mean()# * np.ones((2018-1901+1))
    
    return mean_anual_tmp

def plot_timeseries(df, filepath = None):
    z = df.grid_point_elevation
    lon, lat = df.lon[0], df.lat[0]
    df_org = df
    mean_overall = np.round_(calculate_mean(df_org, 1901, 2018), 2)
    mean_early = np.round_(calculate_mean(df_org, 1901, 1979), 2)# * np.ones((79))
    mean_late = np.round_(calculate_mean(df_org, 1980, 2018), 2)# * np.ones((39))
    
    df = df.loc['1901':'2018']
    df = df.groupby(df.index.year).mean()
    df.index = list(range(1901, 2019, 1))
    
    
    g, ax = plt.subplots(figsize=(6, 4))

    df.tmp.plot(ax=ax, color='k', linewidth = 1, label='Temperature')
    ax.set_xlabel('Year')
    ax.set_ylabel('Temperature (°C)', color='k')
    ax.tick_params('y', colors='k')
    plt.axhline(mean_overall, color = 'lime', linewidth = 1, linestyle = 'solid', 
                     label=f'mean Temperature 1901-2018 = {mean_overall} °C')
    plt.axhline(mean_early, color = 'b', linewidth = 1, linestyle = 'dashed',
                    label =f'mean Temperature 1901-1979 = {mean_early} °C')
    plt.axhline(mean_late, color = 'r', linewidth = 1, linestyle = 'dashed',
                   label = f'mean Temperature 1980-2018 = {mean_late} °C')
    
    title = 'yearly mean Temperature at location ({}°, {}°)\nElevation: {} m a.s.l'
    plt.title(title.format(lon, lat, int(z)), loc='left')
    #text = 'The average temperature from {} to {} was {}°C\ncompared to {}°C between {} and {}'
    #plt.text(1902, 14.5, text.format(1901, 1979, mean_early[0], mean_late[0], 1980, 2018), fontsize = 8)
    plt.legend(loc = 'best', fontsize = 7 )
    #plt.tight_layout()

    if filepath is not None:
        plt.savefig(filepath, dpi=150)
        plt.close()
        
    return g
    
#figure = plot_timeseries(df = timeseries(lon, lat), filepath = None)

    