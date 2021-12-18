# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 13:47:04 2021

@author: Paula

Visualizes the snow depth around a selected city (ERA5 data).
The user (tourist) can see, where around the selected city is the most snow for a selected month (in average).
"""

from climvis import cfg
import matplotlib.pyplot as plt  # plotting library
import numpy as np  # numerical library
import xarray as xr  # netCDF library
import cartopy  # Map projections libary
import cartopy.crs as ccrs  # Projections list





def get_data():
    """Opens the file of monthly snow data (ERA5). The user should have download the data before and saved this
    at the same directory as the CRU files. (link for download: https://fabienmaussion.info/climate_system/download.html)
    Computes the snow depth in m (from meter in water eqivalent).
    
    Returns
    -------
    Data Array
        Snow depth in m (dim: longitude, latitude, time(monthly)) 
    """
    # Open ERA5 snow data
    df_snow = xr.open_dataset(cfg.era5_snow_file)
    
    # Compute snow depth in m from snow depth in meter of water equivalent
    density_water = 1000 #kg/m^3
    snow_depth = density_water * df_snow.sd / df_snow.rsn
    
    return snow_depth

def extract_map_part(lon,lat,month, years):
    """Extracts data, which are plotted: 
    around the selected city,
    the average of snow depth over a certain period of time,
    for a selected month.
    
    Parameters
    -------
    lon : float
        Longitude of the selected city
    lat : float
        Latitude of the selected city
    month : int
        Selected month (input)
    years : int
        Number of years over which is avereged (until 2018)
    
    Returns
    -------
    Data Array
        Snow depth in m, which can be plotted (dim: longitude, latitude) 
    """
    
    snow_depth = get_data()
    
    # Compute the range for the coordinates, at which distance from the city the data is visualized.
    # The data is visualized on a map with 2° distance of the city in each direction.
    d_lon = 2
    d_lat = 2
    lon_range = slice(lon - d_lon, lon + d_lon)
    lat_range = slice(lat + d_lat, lat - d_lat)
    
    # Compute the average over the time period.
    # Extract the data for computed coordinates (around the slected city) and the selected month.
    year_begin = 2018-years
    snow_depth_year = snow_depth.sel(time = slice(str(year_begin), '2019'))
    snow_depth_mon = snow_depth_year.groupby('time.month').mean().sel(month = month)
    snow_depth_map = snow_depth_mon.sel(latitude = lat_range).sel(longitude = lon_range)
    
    return snow_depth_map
    

def plot_snowdepth(lon,lat,month,years, filepath = None):
    """Plots the snow depth around the selected city,
    the data is averaged of over a certain period for a selected month.
    
    Parameters
    -------
    lon : float
        Longitude of the selected city
    lat : float
        Latitude of the selected city
    month : int
        Selected month (input)
    years : int
        Number of years over which should be avereged (until 2018)
    """

    snow_depth_map = extract_map_part(lon,lat,month,years)
    year_begin = 2018-years
   
    
    g, ax = plt.subplots(figsize=(6,4))
    
    plt.gca().axes.yaxis.set_visible(False)
    plt.gca().axes.xaxis.set_visible(False)
    plt.box(on = False)
    
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    # Compute the levels and ticks for the colorbar of the plot
    snowdepth_max = np.round(np.max(snow_depth_map),decimals = 1)
    levels = np.round(np.linspace(0, snowdepth_max, 11),decimals = 1)
    ticks = np.round(np.linspace(0, snowdepth_max, 6),decimals = 1)
    
    # Visualizing the snow depth
    snow_depth_map.plot(ax=ax, transform=ccrs.PlateCarree(), cmap = 'Blues', levels = levels, vmin = 0, alpha = 0.7, cbar_kwargs={'label': 'm', 'ticks' : ticks})
    # Showing the selected city in the map
    plt.plot(lon,lat,'rx', ms = 12, mew = 3) 
    
    # Add state boarders and coastline to the map
    ax.add_feature(cartopy.feature.BORDERS);
    ax.coastlines();
    
    # Adjust the coordinate lines and labels
    gl = ax.gridlines(draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False
    
    # Add title to the figure
    month_label = ['January','February','March', 'April', 'May', 'June', 'July', 'August', 'September', 'Ocotber', 'November', 'December']
    plt.title(f'Snow depth (in m) averaged (over {year_begin} - 2018) in {month_label[month-1]}');
    

    if filepath is not None:
        plt.savefig(filepath, dpi=150)
        plt.close()
        
    return g


#ax = plot_snowdepth(11,47,2,5, filepath = None)
