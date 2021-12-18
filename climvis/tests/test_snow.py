# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 13:08:11 2021

@author: Paula

Tests for snow.py
"""

import climvis
import pytest
import climvis.snow as snow
import xarray
import numpy as np

def test_getdata():
    snow_depth = snow.get_data()
    assert type(snow_depth) == xarray.core.dataarray.DataArray
    assert snow_depth.coords.dims == ('time', 'latitude', 'longitude')
    
def test_extractmap():
    month = 2
    snow_depth = snow.extract_map_part(11,47,month,5)
    assert type(snow_depth) == xarray.core.dataarray.DataArray
    assert snow_depth.coords.dims == ('latitude', 'longitude')
    assert np.max(snow_depth) > 0
    assert snow_depth.month.item() == month
    
