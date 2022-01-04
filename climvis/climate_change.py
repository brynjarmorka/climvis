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

# =============================================================================
# def user_input():
#     """short function which asks the user if additional climate change 
#     information is wanted
#     
#     """
#     
#     add_clim_change = str(input('''do you want additional climate change information?
#                             type either yes or no '''))
#     if add_clim_change != 'yes' and add_clim_change != 'no':
#         raise ValueError('input has to be yes or no')
#     else: return add_clim_change
# =============================================================================


def check_timespan(year1, year2, year3, year4):
    """checks if the years for the timespans the user wants to compare 
    are correctly given. If yes the function returns the years for the timespans
    """
    
    timespan = (year1, year2, year3, year4)
    
    #check if 4 years are given
    if len(timespan) != 4:
        raise ValueError('''expected number of years for the input is 4.
                         Start- and endyear for each of the two period''')
    #check if the years are of class integer                     
    elif any(type(n) is not int for n in timespan):  
        raise TypeError('expected input type is an integer')
    #check if the years are in the data range and in the right order
    elif 1901>year1 or year1>=year2 or year2>=year3 or year3>=year4 or year4>2018:
        raise ValueError('''The data includes the timespan from 1901 - 2018,
                         the years have to be given in ascending order!''')
    else: return timespan



def calculate_mean(df, startyear, endyear):
    """calculates the mean temperature of the specified period
    and returns it
    """
    #divide the timeseries in two parts
    startyear = str(startyear)
    endyear = str(endyear)
    
    df = df.loc[startyear:endyear]
    df = df.groupby(df.index.year).mean()
    df.index = list(range(int(startyear), int(endyear)+1, 1))
    
    #compute the mean anual temperature over the timeseries
    mean_anual_tmp = df.tmp.mean()
    
    return mean_anual_tmp

def plot_timeseries(df, filepath = None):
    """function to plot the overall timeseries of the temperature,
    and the average temperature of the specified periods and the overall 
    temperature average between 1901 and 2018
    """
    
    #Userinput to specify the two timespans which should be compared
    while True:
        try:
            year1 = int(input('start year of first timespan: '))
            year2 = int(input('end year of first timespan: '))
            year3 = int(input('start year of second timespan: '))
            year4 = int(input('end year of second timespan: '))
            
            if 1901>year1 or year1>=year2 or year2>=year3 or year3>=year4 or year4>2018:
                raise ValueError('''The data includes the timespan from 1901 - 2018,
                                 the years have to be given in ascending order!''')
            break
        except ValueError:
            print('''the years has to be given as an integer and in ascending order 
                  in the range of 1901-2018''')
                
    #check if the specified timespans are valid
    timespan = check_timespan(year1, year2, year3, year4)
    year1, year2, year3, year4 = timespan
    
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
    
    
#def frost_freq():
    #function which gives/plots the number of frost days per year and plots the 
    #timeseries of it

    