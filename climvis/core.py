"""Plenty of useful functions doing useful things."""
import os
from tempfile import mkdtemp
import shutil
import xarray as xr
import numpy as np
from motionless import DecoratedMap, LatLonMarker
from climvis import cfg, graphics, cli, climate_change, snow, solar
import csv
import pandas as pd
import sys

GOOGLE_API_KEY = "AIzaSyAjPH6t6Y2OnPDNHesGFvTaVzaaFWj_WCE"


def haversine(lon1, lat1, lon2, lat2):
    """Great circle distance between two (or more) points on Earth
    Parameters
    ----------
    lon1 : float
       scalar or array of point(s) longitude
    lat1 : float
       scalar or array of point(s) longitude
    lon2 : float
       scalar or array of point(s) longitude
    lat2 : float
       scalar or array of point(s) longitude
    Returns
    -------
    the distances
    Examples:
    ---------
    >>> haversine(34, 42, 35, 42)
    82633.46475287154
    >>> haversine(34, 42, [35, 36], [42, 42])
    array([ 82633.46475287, 165264.11172113])
    """

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return c * 6371000  # Radius of earth in meters


def get_cru_timeseries(lon, lat):
    """Read the climate time series out of the netcdf files.
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

    with xr.open_dataset(cfg.cru_tmp_file) as ds:
        tmp_ts = ds.tmp.sel(lon=lon, lat=lat, method="nearest")
        df = tmp_ts.to_dataframe()
    with xr.open_dataset(cfg.cru_pre_file) as ds:
        pre_ts = ds.pre.sel(lon=lon, lat=lat, method="nearest")
        df["pre"] = pre_ts.to_series()

    with xr.open_dataset(cfg.cru_topo_file) as ds:
        z = float(ds.z.sel(lon=lon, lat=lat, method="nearest"))
    
    df.grid_point_elevation = z
    df.distance_to_grid_point = haversine(
        lon, lat, float(pre_ts.lon), float(pre_ts.lat)
    )
    return df


def get_googlemap_url(lon, lat, zoom=10):

    dmap = DecoratedMap(
        lat=lat,
        lon=lon,
        zoom=zoom,
        size_x=640,
        size_y=640,
        maptype="terrain",
        key=GOOGLE_API_KEY,
    )
    dmap.add_marker(LatLonMarker(lat, lon))
    return dmap.generate_url()


def mkdir(path, reset=False):
    """Checks if directory exists and if not, create one.
    Parameters
    ----------
    reset: erase the content of the directory if exists
    Returns
    -------
    the path
    """

    if reset and os.path.exists(path):
        shutil.rmtree(path)
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
    return path


def write_html(lon, lat, add_clim_change, timespan, month, city, date, Altitude, directory=None, zoom=None): 
    """writes the html webpage
    
    changed by Leo and Paula
    Change 1 is a short piece of code, which checks for NaN and throws a Error + Message 
    to the User that his chosen location migth be somewhere in the oceans
    
    Change 2 is in order to display additional climate change information,
    if the user wants to have it and choose the corresponding html template
    
    Change 3 is in order to display the snow cover during the chosen month
    
    returns the html path, which is either printed or used to open a html webpage
    later on"""

    # Set defaults
    if directory is None:
        directory = mkdtemp()

    if zoom is None:
        zoom = cfg.default_zoom

    # Info string
    lonlat_str = "({:.3f}E, {:.3f}N)".format(abs(lon), abs(lat))
    if lon < 0:
        lonlat_str = lonlat_str.replace("E", "W")
    if lat < 0:
        lonlat_str = lonlat_str.replace("N", "S")

    mkdir(directory)

    # Make the plot
    png = os.path.join(directory, "annual_cycle.png")
    png2 = os.path.join(directory, "annual_tmp_averages.png")
    png3 = os.path.join(directory, "solar_path.png")
    png_snow = os.path.join(directory, "snow_depth_averages.png")
    png_snow2 = os.path.join(directory, "snow_depth_averages2.png")    
    df = get_cru_timeseries(lon, lat)
    
    #checking for NaN's
    if df.isnull().values.any():
        sys.exit('''Only land data is covered in this dataset!!!
                 Your coordinates might be located somewhere in the oceans!''')
    
    graphics.plot_annual_cycle(df, filepath=png)
    
    #check if the user wants to have additional temperature timeseries
    #and choose the corresponding html template
    if add_clim_change == 'c':
        #if __name__ == "__main__":
        climate_change.plot_timeseries(df, timespan, filepath = png2)
        #choose html template which includes climate change graphics
        html_tpl = cfg.html_tpl_clim_change
    
    #choose html template which doesn't include climate change graphics
    elif add_clim_change == 'no':
        html_tpl = cfg.html_tpl
    
    elif add_clim_change == 'both':
        climate_change.plot_timeseries(df, timespan, filepath = png2)
        solar.plot_solar_elevation(lat, lon, Altitude, date, filepath = png3)
        html_tpl = cfg.html_tpl_clim_change_solar
    elif add_clim_change == 's':
        solar.plot_solar_elevation(lat, lon, Altitude, date, filepath=png3)
        html_tpl = cfg.html_tpl_solar
    
    #choosing the month for the snow information
    #if __name__ == "__main__":
    month_snow = month
    snow.plot_snowdepth(lon,lat,month_snow,5, filepath = png_snow)
    snow.plot_snowdepth(lon,lat,month_snow,40, filepath = png_snow2)
    

    outpath = os.path.join(directory, "index.html")
    with open(html_tpl, "r") as infile:
        lines = infile.readlines()
        out = []
        url = get_googlemap_url(lon, lat, zoom=zoom)
        city = city
        #city = cli.sys.argv[2]
        for txt in lines:
            txt = txt.replace("[LONLAT]", lonlat_str)
            txt = txt.replace("[IMGURL]", url)
            txt = txt.replace("[CITY]", city)            
            out.append(txt)
        with open(outpath, "w") as outfile:
            outfile.writelines(out)
        
    return outpath


def open_cities_file(elev=None):
    """
    Opens file with cities and corresponding coordinates
    
    author: Paula
    modified with elevation variation: Sebastian
    Returns
    -------
    panda DataFrame
        country, name, longitude, latitude, elevation of cities.
    """
    #world_cities = 'C:/Users/Paula/Programming/climvis/climvis\data\world_cities.csv'
    if elev is True:
        world_cities = cfg.world_cities_elevation
    elif elev is None:
        world_cities = cfg.world_cities
    cityfile = open(world_cities,encoding= "windows-1252")
    reader = csv.reader(cityfile)
    # read header (first row)
    header = next(reader)
    cities_list = []
    
    #read rows in a list
    for row in reader:
        cities_list.append(row)
        
    cityfile.close()
    
    # Convert list to Data Frame
    cities = pd.DataFrame(cities_list, columns = header)
    
    return(cities)


def coordinates_city(city, elev=None):
    """
    Extracts coordinates for the asked country
    
    author: Paula
    
    Parameters
    -------
    city : str
        City, which is selected (argument)
    
    Returns
    -------
    panda DataFrame
        country, name, longitude, latitude, elevation of selected city.
    
    """
    cities = open_cities_file(elev)
    coord_city = cities[(cities['Name'] == city)]
    return coord_city
