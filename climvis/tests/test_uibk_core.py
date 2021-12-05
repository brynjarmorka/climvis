"""
Test for uibk_core.py

Author: Brynjar
"""
import pytest
import pandas as pd

from climvis.uibkvis.uibk_core import load_acinn_data


def test_load_acinn_data():
    """
    This test runs all the valid user inputs to check if the databases are up and running.
    The test takes around 5 sec.
    """
    stations = ["innsbruck", "ellboegen", "obergurgl", "sattelberg"]
    intervals = ["1", "3", "7"]
    for s in stations:
        for i in intervals:
            df = load_acinn_data(s, i)
            assert type(df) == pd.core.frame.DataFrame


def test_error_load_acinn_data():
    """
    This test gives a input which should fail.
    """
    station = "innnsbruck"
    interval = "3"
    with pytest.raises(SystemExit, match="HTTPError"):
        df = load_acinn_data(station, interval)


# dont know how to test write_html_uibkvis() in a good way
# def test_write_html_uibkvis()
#     ...
