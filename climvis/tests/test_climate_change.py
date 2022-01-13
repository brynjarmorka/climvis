# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 23:17:30 2021

@author: Leo

Tests for the climate_change file
"""

import pytest
import climvis
from climvis import climate_change, core, cli
import numpy


def test_timeseries():
    timespan = cli.check_timespan(1901, 1980, 1981, 2018)
    timespan1 = cli.check_timespan(1901, 1985, 1975, 2018)

    assert max(timespan) <= 2018
    assert min(timespan) >= 1901
    assert len(timespan) == 4
    assert all(type(n) is int for n in timespan)
    assert timespan[0]<timespan[1]<timespan[3]
    assert timespan1[0]<timespan1[2]<timespan1[3]
    assert timespan1[1]>=timespan1[2]

def test_calculate_mean(capsys):
    df = core.get_cru_timeseries(12, 45)
    mean_anual_tmp = climate_change.calculate_mean(df, 1901, 2018)
    assert type(mean_anual_tmp) == float
    
    