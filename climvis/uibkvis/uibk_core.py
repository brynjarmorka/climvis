"""
Core file for uibkvis
"""
import os
from tempfile import mkdtemp
from climvis import cfg
from climvis.uibkvis import uibk_graphics
import pandas as pd
import sys
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from climvis.core import mkdir


def write_html_uibkvis(station, interval, directory=None):
    """
    Function which makes the plots, loads ACINN data and puts it together to a HTML-file.

    Author: Brynjar


    Parameters
    ----------
    station : str
            The name of the station
    interval : str
            Interval in days
    directory : str
            The directory for the html-file. Will be a temp-dir if it is None

    Returns
    -------
    str
        directory of the html-file, ending with "uibk.html"
    """
    # Set defaults
    if directory is None:
        directory = mkdtemp()

    mkdir(directory)

    # Make the plot
    png = os.path.join(directory, "winds_lvl1.png")
    png2 = os.path.join(directory, "windrose.png")

    # Read inn the ACINN data
    df = load_acinn_data(station, interval)

    # make plots
    uibk_graphics.plot_wind_dir(df, station, interval, filepath=png)
    uibk_graphics.plot_windrose(df, station, interval, filepath=png2)

    # make the html
    outpath = os.path.join(directory, "uibk.html")
    with open(cfg.html_tpl_uibkvis, "r") as infile:
        lines = infile.readlines()
        out = []
        for txt in lines:
            txt = txt.replace("[STATION]", station[0] + station[1:])
            txt = txt.replace("[INTERVAL]", interval)
            out.append(txt)
        with open(outpath, "w") as outfile:
            outfile.writelines(out)

    return outpath


def load_acinn_data(station, interval):
    """
    Helper function which fetches the data from the ACINN webpage. The inputs have been checked earlier.

    Author: Brynjar

    Parameters
    ----------
    station: str
        either innsruck, ...
    interval: str
        either 1, 3 or 7

    Returns
    -------
    data: pandas dataframe
        the data from the station in a dataframe
    """
    url = f"https://acinn-data.uibk.ac.at/{station}/{interval}"

    # Parse the given url
    try:
        req = urlopen(Request(url)).read()
    except HTTPError:
        sys.exit(f'HTTPError. The url did not work. Check your connection. Check the url yourself:\n{url}')

    # Read the data
    df = pd.read_json(req.decode("utf-8"))
    df["time"] = [datetime(1970, 1, 1) + timedelta(milliseconds=ds) for ds in df["datumsec"]]

    # Check if the df is empty.
    if df.isnull().values.any():
        sys.exit(f"Something is wrong on the ACINN database. Try again, or visit the url yourself:\n{url}")

    return df
