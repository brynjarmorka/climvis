#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 18:29:18 2022

@author: sebastian
"""

import climvis
import pytest
import climvis.solar as solar
import numpy as np
import matplotlib
from datetime import datetime as dt
import pytz


def test_calculate_declination():
    days = np.arange(1,366,1)
    for x in days:
        testdates = dt.strptime(str(x), "%j")
        decl = solar.calculate_declination(testdates)
        assert decl > -23.44
        assert decl < 23.44
    

def test_calculate_hr_angle():
    lon = [-180, 0, 180] 
    date = dt(2000,1,1,0), dt(2000,1,1,12), dt(2000,1,1,23,59,59)
    for x in lon:
        for y in date:
            local_time = solar.calculate_hr_angle(x, y)[1][-1]
            assert (local_time <= 24)
            assert (local_time >= 0)


def test_calculate_azimuth_and_elevation():
    date = dt(2000,12,21,12,1)
    lat = -23.44
    lon = 0
    a = solar.calculate_azimuth_and_elevation(lat, lon, date)
    assert np.rad2deg(a[0][-1]) > 179
    assert a[1][-1] > 89
    

def test_get_sunrise_sunset():
    lat = 0
    lon = 0
    date = dt(2000,3,21,12,1)
    suntimes = solar.get_sunrise_sunset(lat, lon, date)
    assert suntimes[0] < 6.25
    assert suntimes[0] > 5.75
    assert suntimes[1] < 18.25
    assert suntimes[1] > 17.75
    assert suntimes[2] < 12.25
    assert suntimes[2] > 11.75

def test_plot_solar_elevation():
    f = solar.plot_solar_elevation(0, 0, 0,"200001010000")
    assert type(f) == matplotlib.figure.Figure
  