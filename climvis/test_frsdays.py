# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 17:16:01 2021

@author: leopo
"""

import xarray as xr
import numpy as np
from climvis import cfg

lon = 9
lat = 47

with xr.open_dataset(cfg.cru_tmp_file) as ds:
    tmp_ts = ds.tmp.sel(lon=lon, lat=lat, method="nearest")
    df = tmp_ts.to_dataframe()
with xr.open_dataset(cfg.cru_pre_file) as ds:
    pre_ts = ds.pre.sel(lon=lon, lat=lat, method="nearest")
    df["pre"] = pre_ts.to_series()
with xr.open_dataset(cfg.cru_frs_file) as ds:
    frs_ts = ds.frs.sel(lon=lon, lat=lat, method="nearest")
    df["frs"] = frs_ts.to_series()
with xr.open_dataset(cfg.cru_topo_file) as ds:
    z = float(ds.z.sel(lon=lon, lat=lat, method="nearest"))
    
#df = df.loc['1901':'2018']
#df = df.groupby(df.index.year).mean()
#df.index = list(range(1901, 2019, 1))
#read the datafile
#data = "cru_ts4.03.1901.2018.frs.dat.nc"
#ds = xr.open_dataset(data)
#frs_ts = ds.frs.sel(lon = lon, lat = lat, method = "nearest")
#df = frs_ts.to_dataframe()

#with xr.open_dataset(cfg.cru_pre_file) as ds:
 #   pre_ts = ds.pre.sel(lon=lon, lat=lat, method="nearest")
  #  df["pre"] = pre_ts.to_series()

#with xr.open_dataset(cfg.cru_tmp_file) as ds:
 #   tmp_ts = ds.tmp.sel(lon=lon, lat=lat, method="nearest")
  #  df = tmp_ts.to_dataframe()