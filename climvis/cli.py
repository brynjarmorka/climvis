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

        # extract city and country argment if --no-browser is in argument
        args2 = args
        if "--no-browser" in args:
            args2 = args[:-1]

        # get coordinates of asked city
        city = args[1]
        coord = climvis.core.coordinates_city(city)

        # Check if there are more cities with the same name
        if len(coord) > 1:
            if len(args2) == 3:
                country = args[2]
                coord = coord[(coord['Country'] == country)]
            else:
                # Now the user selects the city with an user input, because e.g. Paris occurs 6 times with 5 in the US.
                coord = coord.reset_index(drop=True)
                print(f'There are more cities with the name {city}.\nSelect the city you want from this list:\n{coord}')
                while True:
                    user_select = input('Select the index (first element in the list above): ')
                    try:
                        user_select = int(user_select)
                    except ValueError:
                        print('Input must be an integer!')
                    if user_select in range(0, len(coord)):
                        break
                    else:
                        print(f'Select an integer index in the range [0, {len(coord) - 1}]')
                coord = coord.iloc[user_select:user_select + 1]
                # raise ValueError(f'There are more cities with the name {city}.\n'
                #                  'Please add the country of the city as input!\n'
                #                  f'This is the possibilities: \n{coord}\n')

        # Check if city is available in list
        if coord.empty:
            raise ValueError(
                f'The city {city} -and corresponding country- does not exist in the available list of cities. Please '
                f'try another city nearby! Also, cities with whitespace must be written with quotation marks.')

        # Check if given city is in given country
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
