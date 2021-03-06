from urllib.request import Request, urlopen
import json
import os
import numpy as np
import pandas as pd
import pytest
from climvis import core, cfg, climate_change, cli


def test_get_ts():

    df_cities = pd.read_csv(cfg.world_cities, encoding="windows-1252")
    dfi = df_cities.loc[
        df_cities.Name.str.contains("innsbruck", case=False, na=False)
    ].iloc[0]

    df = core.get_cru_timeseries(dfi.Lon, dfi.Lat)
    assert df.grid_point_elevation > 500  # we are in the alps after all
    assert df.distance_to_grid_point < 50000  # we shouldn't be too far

    # It's different data but I wonder how we compare to the
    # Innsbruck climate station we studied a couple of weeks ago?
    url = (
        "https://raw.githubusercontent.com/fmaussion/"
        "scientific_programming/master/data/innsbruck_temp.json"
    )
    req = urlopen(Request(url)).read()

    # Read the data
    data = json.loads(req.decode("utf-8"))
    for k, v in data.items():
        data[k] = np.array(data[k])

    # select
    t = data["TEMP"][np.nonzero((data["YEAR"] <= 2016))]
    yrs = data["YEAR"][np.nonzero((data["YEAR"] <= 2016))]
    dfs = df.loc[(df.index.year >= yrs.min()) & (df.index.year <= yrs.max())].copy()
    assert len(dfs) == len(yrs)
    dfs["ref"] = t
    dfs = dfs[["tmp", "ref"]]

    # Check that we have good correlations at monthly and annual scales
    assert dfs.corr().values[0, 1] > 0.95
    assert dfs.groupby(dfs.index.year).mean().corr().values[0, 1] > 0.9

    # The newer data set does not have the Elevation
    # # Check that altitude correction is helping a little
    # z_diff = df.grid_point_elevation - dfi.Elevation
    # dfs["tmp_cor"] = dfs["tmp"] + z_diff * 0.0065
    # dfm = dfs.mean()
    # assert np.abs(dfm.ref - dfm.tmp_cor) < np.abs(dfm.ref - dfm.tmp)


def test_get_url():

    df_cities = pd.read_csv(cfg.world_cities, encoding="windows-1252")
    dfi = df_cities.loc[
        df_cities.Name.str.contains("innsbruck", case=False, na=False)
    ].iloc[0]

    url = core.get_googlemap_url(dfi.Lon, dfi.Lat)
    assert "maps.google" in url



def test_write_html(tmpdir):

    """
    changed by Leo
    Test for write_html with the needed input parameters
    """
    
    df_cities = pd.read_csv(cfg.world_cities, encoding="windows-1252")
    dfi = df_cities.loc[
        df_cities.Name.str.contains("innsbruck", case=False, na=False)
    ].iloc[0]
    
    add_clim_change_and_solar = 'c'   #changes made!!!!!
    timespan = [1901, 1970, 1971, 2018]
    #month = 2
    city = "Innsbruck"
    
    date, Altitude = None, None
    dir = str(tmpdir.join("html_dir"))
    #core.write_html(dfi.Lon, dfi.Lat, add_clim_change_and_solar, timespan, month, city, date, Altitude, directory=dir)
    core.write_html(dfi.Lon, dfi.Lat, timespan, city, date, Altitude, directory=dir)
    assert os.path.isdir(dir)
    
def test_open_cities_file():
    cities = core.open_cities_file()
    assert type(cities) == pd.core.frame.DataFrame
    assert cities.columns[1] == 'Name'
    
# =============================================================================
# def test_valid_month():
#     
#     with pytest.raises(ValueError, match = 'The number was not valid. The month is between 1 and 12.'):
#         cli.valid_month(int(13))
#         
#     with pytest.raises(TypeError, match = 'The month should be an integer'):
#         cli.valid_month('month')
# =============================================================================
        