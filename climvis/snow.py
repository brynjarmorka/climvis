# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 13:47:04 2021

@author: Paula

Takes ERA5 data of snow depth (and snow densitiy) to visualize th snow depth at the selected city and around.
The user (tourist) can see, where the most snow is in average.
"""

# function for a plot on snow cover

from climvis import cfg, core, graphics
import matplotlib.pyplot as plt  # plotting library
import numpy as np  # numerical library
import xarray as xr  # netCDF library
import cartopy  # Map projections libary
import cartopy.crs as ccrs  # Projections list
import cartopy.feature as cfeature
import matplotlib.ticker as mticker
from cartopy.mpl.ticker import (LongitudeFormatter, LatitudeFormatter,
                                LatitudeLocator)
import datetime
# Some defaults:




def get_data():
    """Opens file of monthly snow data (ERA5). The user should have download the data before and saved this
    at the same directory as the CRU files. (link for download: https://fabienmaussion.info/climate_system/download.html)
    Computes the snow depth in m (from meter in water eqivalent).
    
    Returns
    -------
    snow_depth: Data Array, snow depth in m (dim: longitude, latitude, time(monthly)) 
    """
    
    df_snow = xr.open_dataset(cfg.era5_snow_file)
    density_water = 1000 #kg/m^3
    
    snow_depth = density_water * df_snow.sd / df_snow.rsn
    snow_fall = density_water * df_snow.sf / df_snow.rsn
    
    return snow_depth

def extract_map_part(lon,lat,month, years):
    """Extracts data, which should be plotted: around the selected city,
    the average of snow depth over a certain period of time until the end of data (2018),
    for a selected month.
    
    Parameters
    -------
    lon: float, longitude of the selected city
    lat: float, latitude of the selected city
    month: int, selected month (input)
    years: int, number of years which should be avereged (until 2018)
    
    Returns
    -------
    snow_depth_map: Data Array, snow depth in m, which should be plotted (dim: longitude, latitude) 
    """
    
    snow_depth = get_data()
    d_lon = 2
    d_lat = 2
    lon_range = slice(lon - d_lon, lon + d_lon)
    lat_range = slice(lat + d_lat, lat - d_lat)
    
    year_begin = 2018-years
    
    snow_depth_year = snow_depth.sel(time = slice(str(year_begin), '2019'))
    snow_depth_mon = snow_depth_year.groupby('time.month').mean().sel(month = month)
    snow_depth_map = snow_depth_mon.sel(latitude = lat_range).sel(longitude = lon_range)
    return snow_depth_map
    

def plot_snowdepth(lon,lat,month,years, filepath = None):
    """Plots snow depth around the selected city
    the average of snow depth over a certain period of time until the end of data (2018),
    for a selected month.
    
    Parameters
    -------
    lon: float, longitude of the selected city
    lat: float, latitude of the selected city
    month: int, selected month (input)
    years: int, number of years which should be avereged (until 2018)

    """
    
    d_lon = 2
    d_lat = 2
    snow_depth_map = extract_map_part(lon,lat,month,years)
    int(years)
    year_begin = 2018-years
   
    
    g, ax = plt.subplots(figsize=(6,4))
    
    plt.gca().axes.yaxis.set_visible(False)
    plt.gca().axes.xaxis.set_visible(False)
    plt.box(on = False)
    
    ax = plt.axes(projection=ccrs.PlateCarree())
    #ax.stock_img()
    #from mpl_toolkits.basemap import Basemap
    # setup Lambert Conformal basemap.
    # set resolution=None to skip processing of boundary datasets.
    #ax = Basemap(width=12000000,height=9000000,projection='lcc',
                #resolution=None,lat_1=45.,lat_2=55,lat_0=50,lon_0=-107.)
    #ax.shadedrelief()
    snow_depth_map.plot(ax=ax, transform=ccrs.PlateCarree(), cmap = 'Blues', levels = 10, vmin = 0, alpha = 0.7)
    plt.plot(lon,lat,'rx', ms = 12, mew = 3) #Plot selected point
    ax.add_feature(cartopy.feature.BORDERS);
    ax.coastlines();
    ax.set_xlim(lon - d_lon, lon + d_lon)
    ax.set_ylim(lat - d_lat, lat + d_lat)
    gl = ax.gridlines(draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False
   # gl.xlocator = mticker.FixedLocator(np.linspace(lon - d_lon, lon + d_lon,1))
    #gl.xformatter = LongitudeFormatter()
    month_label = ['January','February','March', 'April', 'May', 'June', 'July', 'August', 'September', 'Ocotber', 'November', 'December']
    plt.title(f'Snow depth (in m) averaged ({year_begin} - 2018) in {month_label[month]}');


    if filepath is not None:
        plt.savefig(filepath, dpi=150)
        plt.close()
        
    return g

ax = plot_snowdepth(11,47,2,5, filepath = None)

