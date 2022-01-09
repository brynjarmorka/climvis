# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 09:54:53 2021

author: Leo

if this file is called, the user should get additional information if/how the
chosen location is affected by the climate change. The user gets asked if he/she 
wants climate change information and if yes is given as an input, this file is
called.
for input shoud be asked in the .cli file
data is read in in the .cfg file
"""
import numpy as np
import xarray as xr
from climvis import cfg, core, graphics
import matplotlib.pyplot as plt





def calculate_mean(df, startyear, endyear):
    """calculates the mean temperature of the specified period
    and returns it as an floating number
    
    Parameters
    ----------
    df: pd.DataFrame
        contains the Data which is read in in core.get_cru_timeseries:
        temperature, precipitation, elevation
    startyear: int
               first year of the wanted period
    endyear:   int
               last year of the wanted period
               
    Returns
    -------
    mean_anual_tmp: float
                    the average temperature in °C during the analyzed period    
        
    """
    #divide the timeseries in two parts
    startyear = str(startyear)
    endyear = str(endyear)
    
    df = df.loc[startyear:endyear]
    df = df.groupby(df.index.year).mean()
    df.index = list(range(int(startyear), int(endyear)+1, 1))
    
    #compute the mean anual temperature over the timeseries
    mean_anual_tmp = float(df.tmp.mean())
    mean_anual_tmp = check_calculate_mean(mean_anual_tmp)
    
    return mean_anual_tmp

def check_calculate_mean(mean_anual_tmp): 
    """checks if the calculate_mean function works right
    Parameters
    ----------
    mean_anual_tmp: float
                    the average temperature of a certain period which should
                    be checked
    Raises
    ------
    TypeError if the type of the input Parameter isn't float
    
    Returns 
    -------
    mean_anual_tmp: float
                    if the given Parameter has the right type it is returned
             
        
    """
    
    if type(mean_anual_tmp) == float:
        return mean_anual_tmp
    else:
        raise TypeError('The mean anual temperature has to be of type float')

def plot_timeseries(df, timespan, filepath = None):
    """function to plot the overall timeseries of the temperature,
    and the average temperature of the specified periods and the overall 
    temperature average between 1901 and 2018
    
    Parameters
    ----------
    df: pd.DataFrame
        contains the Data which is read in in core.get_cru_timeseries:
        temperature, precipitation, elevation
    timespan: list of 4 years which specify the two timespans of interest
    
    Returns
    -------
    g: the graphic which is plotted on the html page
    """
    

                
    #check if the specified timespans are valid
    year1, year2, year3, year4 = timespan
    #timespan = check_timespan(year1, year2, year3, year4)
    #year1, year2, year3, year4 = timespan
    
    z = df.grid_point_elevation
    lon, lat = df.lon[0], df.lat[0]
    df_org = df.copy()
    
    #computing the temperature averages of the timespans 
    mean_overall = np.round_(calculate_mean(df_org, 1901, 2018), 2)
    mean_early = np.round_(calculate_mean(df_org, year1, year2), 2)# * np.ones((79))
    mean_late = np.round_(calculate_mean(df_org, year3, year4), 2)# * np.ones((39))
    
    df = df.loc['1901':'2018']
    df = df.groupby(df.index.year).mean()
    df.index = list(range(1901, 2019, 1))
    
    
    #plotting the temperature timeseries
    g, ax = plt.subplots(figsize=(6, 4))

    df.tmp.plot(ax=ax, color='k', linewidth = 1, label='Temperature')
    ax.set_xlabel('Year')
    ax.set_ylabel('Temperature (°C)', color='k')
    ax.tick_params('y', colors='k')
    plt.axhline(mean_overall, color = 'lime', linewidth = 1, linestyle = 'solid', 
                     label=f'mean Temperature 1901-2018 = {mean_overall} °C')
    plt.axhline(mean_early, color = 'b', linewidth = 1, linestyle = 'dashed',
                    label =f'mean Temperature {year1}-{year2} = {mean_early} °C')
    plt.axhline(mean_late, color = 'r', linewidth = 1, linestyle = 'dashed',
                   label = f'mean Temperature {year3}-{year4} = {mean_late} °C')
    
    title = '''Temperature timeseries of annual mean 
    at location ({}°, {}°), Elevation: {} m a.s.l'''
    plt.title(title.format(lon, lat, int(z)), loc='left')
    plt.legend(loc = 'best', fontsize = 7 )
    #plt.tight_layout()

    if filepath is not None:
        plt.savefig(filepath, dpi=150)
        plt.close()
        
    return g
    
    


    