# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 23:17:30 2021

@author: Leo

Tests for the climate change file
"""

import pytest
import climvis
from climvis import climate_change, core
import numpy

# =============================================================================
# def test_user_input(monkeypatch):
#     monkeypatch.setattr('builtins.input', lambda _: "yes")
#     
#     i = input("do you want additional climate change information? type either yes or no")
#     assert i == "yes"# or i == "no"
#     
#     monkeypatch.setattr('builtins.input', lambda _: "no")
#     
#     i = input("do you want additional climate change information? type either yes or no")
#     assert i == "no"
# =============================================================================

def test_timeseries():
    timespan = climate_change.check_timespan(1901, 1970, 1971, 2018)

    assert max(timespan) <= 2018
    assert min(timespan) >= 1901
    assert len(timespan) == 4
    assert all(type(n) is int for n in timespan)
    assert timespan[0]<timespan[1]<timespan[2]<timespan[3]

def test_calculate_mean():
    df = core.get_cru_timeseries(12, 45)
    mean_anual_tmp = climate_change.calculate_mean(df, 1901, 2018)
    
    assert type(mean_anual_tmp) == float