"""
Client for uibkvis

Author: Brnjar
"""
import webbrowser
import sys
import climvis

HELP_uibkvis = """
uibkvis: Visualization of data from ACINN.

Available data stations is: Innsbruck (i), Ellbögen (e), Obergurgl (o) and Sattelberg (s).
Available time intervals is: 1, 3, 7.

You need to be connected to the Internet to use uibkvis.

Usage:
    -h, --help                          : print the help
    -v, --version                       : print the installed version
    -l, --loc [station] [days]          : set station and duration. Valid input: i/e/o/s 1/3/7

    --no-browser                        : the default behavior is to open a browser with the newly generated 
                                        visualisation. Set to ignore and print the path to the html file instead 
"""
version_uibk = f'climvis: {climvis.__version__} \n License: public domain \n climvis is provides "as is", without ' \
               f'warranty of any kind '


def uibkvis():
    """
    Entry point for the uibkvis application script.

    Author: Brynjar
    """

    uibkvis_io(sys.argv[1:])


def uibkvis_io(args):
    """
     The input/output commandline tool for the uibkvis application.

     Author: Brynjar

    Parameters
    ----------
    args: list
        sys.args[1:], which is sys.args without 'uibkvis'
    """

    # Defining the possible stations and intervals through a dictionary
    # This is done to ensure right input.
    stations = {'i': 'innsbruck', 'e': 'ellboegen', 'o': 'obergurgl', 's': 'sattelberg'}
    intervals = {'1': '1', '3': '3', '7': '7'}
    no_browser = False

    # Checking for --no-browser, then removing that argument. This is done first to make len(args) easier to use
    if '--no-browser' in args:
        no_browser = True
        args.remove('--no-browser')

    # Checking which input the user gave
    if len(args) == 0 or args[0] in ['-h', '--help']:
        print(HELP_uibkvis)
    elif args[0] in ['-v', '--version']:
        print(version_uibk)

    # when the user actually (tries to) use uibkvis
    elif args[0] in ['-l', '--location']:

        # if there are no additional arguments, or too many arguments
        if len(args) == 1 or len(args) > 3:
            raise ValueError('Please specify station and interval when using "-l".\n Type "uibkvis -h" for help')

        # assigning the commandline input to variables
        try:
            station = stations[args[1]]
            interval = intervals[args[2]]
        # This except catch is just to make it clearer to the user that the input is not valid.
        except KeyError:
            raise KeyError('Invalid input! Station must be in [i, e, o, s] and interval in [1, 3, 7]')

        # passing the station and interval to the function making the html
        html_path = climvis.write_html_uibkvis(station, interval)

        if no_browser:
            print("File successfully generated at: " + html_path)
        else:
            webbrowser.get().open_new_tab("file://" + html_path)

    # fallback if the commandline arguments does not match any option
    else:
        print('uibkvis: command not understood. Type "uibkvis --help" for usage options.')
