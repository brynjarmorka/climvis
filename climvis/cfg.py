"""This configuration module is a container for parameters and constants."""
import os
from pathlib import Path

# Hard coded overview over the required data files.
required_data_files = [
    "cru_ts4.03.1901.2018.tmp.dat.nc",
    "cru_ts4.03.1901.2018.pre.dat.nc",
#    "cru_ts4.03.1901.2018.frs.dat.nc",
    "cru_cl1_topography.nc",
    "ERA5_LowRes_Monthly_snow.nc",
]

no_cru = (
    'The CRU and ERA5* files are not available on this system. For cruvis (part of the climvis package) to work '
    'properly, please create a file called ".climvis.txt" in your HOME directory**, and indicate the path to the data '
    'folder directory in it. \n\n'
    f'Required data files are: {required_data_files}\n\n'
    '*The ERA5 data is here available: https://fabienmaussion.info/climate_system/download.html.'
    f'**Your HOME directory is "{os.path.expanduser("~")}".\n'
)


def get_cru_dir():
    """
    Short functions which reads the "~/.climvis" and gives it as the dirname for the CRU files. If the .climvis file
    does not exist, the try/except below will throw an error.

    get_cru_dir() assumes that the .climvis.txt contains only the path, with eventually some whitespace

    Author: Brynjar

    Returns
    -------
    string
        local path for CRU files
    """
    path = Path("~/.climvis.txt")  # Accessing the HOME dir of the user
    full_path = os.path.expanduser(path)
    f = open(full_path, "r")
    local_path = f.read()
    local_path = local_path.replace('\n','')  # Removes any potential newlines in the file
    f.close()
    return local_path


# First make the filenames
# Remember to update the list required_data_files when more data files are added here
try:
    cru_dir = get_cru_dir()
    cru_tmp_file = Path(cru_dir,"cru_ts4.03.1901.2018.tmp.dat.nc")
    cru_pre_file = Path(cru_dir,"cru_ts4.03.1901.2018.pre.dat.nc")
#    cru_frs_file = Path(cru_dir,"cru_ts4.03.1901.2018.frs.dat.nc")
    cru_topo_file = Path(cru_dir,"cru_cl1_topography.nc")
    era5_snow_file = Path(cru_dir,"ERA5_LowRes_Monthly_snow.nc")
except Exception as exc:
    print(f'Could not find the file at "{os.path.expanduser("~")}/.climvis.txt"')
    raise FileNotFoundError(no_cru)

# Then check if the files actually exists
if (
    cru_topo_file.exists()
    and cru_pre_file.exists()
#    and cru_frs_file.exists()
    and cru_topo_file.exists()
    and era5_snow_file.exists()
):
    print("Data files successfully found.")
else:
    print('Unable to find the datafiles. Make sure that the ".climvis.txt" file only contains the data folder path.')
    raise FileNotFoundError(no_cru)

# Making some path names
bdir = os.path.dirname(__file__)
html_tpl = os.path.join(bdir, "data", "template.html")
html_tpl_solar = os.path.join(bdir, "data", "solar_template.html")
html_tpl_clim_change = os.path.join(bdir, "data", "clim_change_template.html")
html_tpl_clim_change_solar = os.path.join(bdir, "data",
                                          "clim_change_solar_template.html")
html_tpl_uibkvis = os.path.join(bdir, "data", "uibkvis_template.html")
world_cities = os.path.join(bdir, "data", "world_cities_41k.csv")
world_cities_elevation = os.path.join(bdir, "data", "world_cities.csv")

default_zoom = 8  # Default zoom for the google maps image
