import webbrowser
import sys
import climvis

HELP = """cruvis: CRU data visualization at a selected location.

Usage:
   -h, --help                 : print the help
   -v, --version              : print the installed version
   -l, --loc [city] [country] : the city at which the climate data must be
                               extracted (if the city exists more often than once
                                          the country is necassary)
   --no-browser               : the default behavior is to open a browser with the
                               newly generated visualisation. Set to ignore
                               and print the path to the html file instead
"""


def cruvis_io(args):
    """The actual command line tool.
    
    changed by Paula

    Parameters
    ----------
    args: list
        output of sys.args[1:]
    """

    if len(args) == 0:
        print(HELP)
    elif args[0] in ["-h", "--help"]:
        print(HELP)
    elif args[0] in ["-v", "--version"]:
        print("cruvis: " + climvis.__version__)
        print("License: public domain")
        print('cruvis is provided "as is", without warranty of any kind')
    elif args[0] in ["-l", "--loc"]:
        if len(args) < 2:
            print("cruvis --loc needs city parameter!")
            return
        
        args2 = args
        if "--no-browser" in args:
            args2 = args[:-1]
            
        city = args[1]
        coord = climvis.core.coordinates_city(city) 
        
        if len(coord) > 1:
            # Check if there are more cities with the same name
            if len(args2) == 3:
                country = args[2]
                coord = coord[(coord['Country'] == country)]
            else:
                raise ValueError(f'There are more cities with the name {city}.'
                                 'Please add the country of the city as input!')
        
        if coord.empty:
            raise ValueError(f'The city {city} -and corresponding country- does not exist in the available list of cities. Please try another city nearby!')
        
        if len(args2) == 3:
            country = args[2]
            if (coord['Country'] != country).item():
                raise ValueError(f'The city {city} does not exist in {country}')
            
         
        lon = float(coord["Lon"].item())
        lat = float(coord["Lat"].item())
        
        html_path = climvis.write_html(lon, lat)
        if "--no-browser" in args:
            print("File successfully generated at: " + html_path)
        else:
            webbrowser.get().open_new_tab("file://" + html_path)
    else:
        print(
            "cruvis: command not understood. " 'Type "cruvis --help" for usage options.'
        )


def cruvis():
    """Entry point for the cruvis application script"""

    # Minimal code because we don't want to test for sys.argv
    # (we could, but this is too complicated for now)
    cruvis_io(sys.argv[1:])
