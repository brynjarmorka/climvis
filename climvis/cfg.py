"""This configuration module is a container for parameters and constants."""
import os
from pathlib import Path

no_cru = 'The CRU files are not available on this system. For cruvis (part of the climvis package) to work properly,\n'\
         'please create a file called ".climvis.txt" in your HOME directory*, and indicate the path to the CRU '\
         f'directory in it.\n*Your HOME directory is "{os.path.expanduser("~")}"'


def get_cru_dir():
    """
    Author: Brynjar
    Short functions which reads the "~/.climvis" and gives it as the dirname for the CRU files. If the .climvis file
    does not exist, the try/except at line 26 will throw an error.

    Returns
    -------
    string
        local path for CRU files
    """
    path = Path("~/.climvis.txt")
    full_path = os.path.expanduser(path)
    f = open(full_path, 'r')
    local_path = f.read()
    f.close()
    return local_path


# first make the filenames
try:
    cru_dir = Path(get_cru_dir())
    cru_tmp_file = cru_dir / "cru_ts4.03.1901.2018.tmp.dat.nc"
    cru_pre_file = cru_dir / "cru_ts4.03.1901.2018.pre.dat.nc"
    cru_topo_file = cru_dir / "cru_cl1_topography.nc"
    #era5_snow_file = cru_dir / "ERA5_LowRes_Monthly_snow.nc"
except Exception as exc:
    raise FileNotFoundError(no_cru)

# then check if the files actually exists
if cru_topo_file.exists() and cru_pre_file.exists() and cru_topo_file.exists():
    print("CRU files successfully found.")
else:
    raise FileNotFoundError(no_cru)


bdir = os.path.dirname(__file__)
html_tpl = os.path.join(bdir, "data", "template.html")
world_cities = os.path.join(bdir, "data", "world_cities_41k.csv")

default_zoom = 8
