# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 13:47:04 2021

@author: Paula
"""

# function for a plot on snow cover

from climvis import cfg, core, graphics
import matplotlib.pyplot as plt  # plotting library
import numpy as np  # numerical library
import xarray as xr  # netCDF library
import cartopy  # Map projections libary
import cartopy.crs as ccrs  # Projections list
import cartopy.feature as cfeature
import datetime
# Some defaults:
plt.rcParams['figure.figsize'] = (12, 5)  # Default plot size

lon = float(47)
lat = float(11)

def get_snow_data(lon, lat):
    """Read the snow time series out of the netcdf files.
    
    Parameters
    ----------
    lon : float
        the longitude
    lat : float
        the latitude
        
    Returns
    -------
    a pd.DataFrame with additional attributes: ``grid_point_elevation`` and
    ``distance_to_grid_point``.
    """

    with xr.open_dataset(cfg.era5_snow_file) as ds:
        snow_depth = ds.sd.sel(longitude=lon, latitude=lat, method="nearest")
        df = snow_depth.to_dataframe()
        snow_fall = ds.sf.sel(longitude=lon, latitude=lat, method="nearest")
        df["fall"] = snow_fall.to_series()
        snow_density = ds.sd.sel(longitude=lon, latitude=lat, method="nearest")
        df["density"] = snow_density.to_series()
        

    #df.grid_point_elevation = z
    df.distance_to_grid_point = core.haversine(lon, lat, float(snow_depth.longitude), float(snow_depth.latitude))
    return df


df_snow = get_snow_data(11.25,47.25)


#df_snow
#depth_we = df_snow.sd
#density_snow = df_snow.rsn
density_water = 1000 #kg/m^3

snow_depth = density_water * df_snow.sd / df_snow.density
snow_fall = density_water * df_snow.fall / df_snow.density

def get_data():
    df_snow = xr.open_dataset('D:/Uni/Master/2021_WS_Programming/Project/ERA5_LowRes_Monthly_snow.nc')
    
    snow_depth = density_water * df_snow.sd / df_snow.rsn
    snow_fall = density_water * df_snow.sf / df_snow.rsn
    
    return snow_depth

def extract_map_part(lon,lat,month, years):
    snow_depth = get_data()
    d_lon = 2
    d_lat = 2
    lon_range = slice(lon - d_lon, lon + d_lon)
    lat_range = slice(lat + d_lat, lat - d_lat)
    
    int(years)
    year_begin = 2018-years
    snow_depth_year = snow_depth.sel(time = slice(str(year_begin), '2019'))
    snow_depth_mon = snow_depth_year.groupby('time.month').mean().sel(month = month)
    snow_depth_map = snow_depth_mon.sel(latitude=lat_range).sel(longitude=lon_range)
    return snow_depth_map
    

def plot_allyears(lon,lat,month,years):
    
    d_lon = 2
    d_lat = 2
    snow_depth_map = extract_map_part(lon,lat,month,years)
    int(years)
    year_begin = 2018-years
   
    
    
    ax = plt.axes(projection=ccrs.PlateCarree())
    #ax.stock_img()
    #from mpl_toolkits.basemap import Basemap
    # setup Lambert Conformal basemap.
    # set resolution=None to skip processing of boundary datasets.
    #ax = Basemap(width=12000000,height=9000000,projection='lcc',
                #resolution=None,lat_1=45.,lat_2=55,lat_0=50,lon_0=-107.)
    #ax.shadedrelief()
    snow_depth_map.plot(ax=ax, transform=ccrs.PlateCarree(), cmap = 'Blues', levels = 10, vmin = 0, alpha = 0.7)
    ax.add_feature(cartopy.feature.BORDERS);
    ax.coastlines();
    ax.set_xlim(lon - d_lon, lon + d_lon)
    ax.set_ylim(lat - d_lat, lat + d_lat)
    ax.gridlines(draw_labels=True)

    plt.plot(lon,lat,'rx', ms = 12, mew = 3) #Plot selected point
    month_label = ['January','February','March', 'April', 'May', 'June', 'July', 'August', 'September', 'Ocotber', 'November', 'December']
    
    plt.title(f'Snow depth (in m) averaged ({year_begin} - 2018) in {month_label[month]}');


    

plot_allyears(11,47,2,5)


