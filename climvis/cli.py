import webbrowser
import sys
import climvis
import numpy as np

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


def cruvis_io(args, timespan, month, add_clim_change):
    """The actual command line tool.

    changed by Paula and Leo

    Parameters
    ----------
    args: list
        output of sys.args[1:]
    timespan, month and add_clim_change are given as userinput
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
        args2 = args.copy()
        if "--no-browser" in args:
            args.remove("--no-browser")   #changes made!!!
            

        # get coordinates of asked city
        city = args[1]
        coord = climvis.core.coordinates_city(city)

        # Check if there are more cities with the same name
        if len(coord) > 1:
            if len(args) == 3:  #changes made!!!!
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
        if len(args) == 3:   
            country = args[2]
            if (coord['Country'] != country).item():
                raise ValueError(f'The city {city} does not exist in {country}')

        lon = float(coord["Lon"].item())
        lat = float(coord["Lat"].item())
        

        html_path = climvis.write_html(lon, lat, add_clim_change, timespan, month, city)    
        if "--no-browser" in args2:                                  
            print("File successfully generated at: " + html_path)
        else:
            webbrowser.get().open_new_tab("file://" + html_path)
            
    else:
        print(
            "cruvis: command not understood. " 'Type "cruvis --help" for usage options.'
        )


def cruvis():
    """Entry point for the cruvis application script
    
    changed by Leo
    
    The code asks here for the needed userinput and hands it over to rest 
    of the program. If the inputs were later on in the code some of the tests
    would fail"""

    # Minimal code because we don't want to test for sys.argv
    # (we could, but this is too complicated for now)

    if len(sys.argv) >= 3 and "-l" in sys.argv:
        add_clim_change = user_input()    
        
        #if yes the user can give the two timespans as input arguments
        if add_clim_change == 'yes':
            timespan = get_timespan()
            year1, year2, year3, year4 = timespan
            timespan = check_timespan(year1, year2, year3, year4)
        #if not 4 standard years are given to the rest of the code to make it work,
        #but aren't displayed in the graphics
        elif add_clim_change == 'no':
            timespan = [1901, 1970, 1971, 2018]
            
            
        #ask for the month of which the snowcover is wanted
        month = get_month()
        month = valid_month(month)
    else: 
        timespan, month, add_clim_change = None, None, None
    
    cruvis_io(sys.argv[1:], timespan, month, add_clim_change)

def user_input():
     """
     author: Leo
     
     short function which asks the user if additional climate change 
     information is wanted
     returns one variable which equals "yes" or "no" which can be used in 
     if statements
     """
     while True:
         try:
             add_clim_change = str(input('''do you want additional climate change information? 
             type either yes or no '''))
             if add_clim_change != 'yes' and add_clim_change != 'no':
                 raise ValueError('input has to be yes or no')
             break
         except ValueError:
             print('input has to be yes or no!')
     return add_clim_change
     

def get_timespan():
    """
    author: Leo
    function to ask the user for the two timespans which he wants to compare
    returns a list of the 4 border years
    """
    
    while True:
        try:
            year1 = int(input('start year of first timespan: '))
            year2 = int(input('end year of first timespan: '))
            year3 = int(input('start year of second timespan: '))
            year4 = int(input('end year of second timespan: '))
             
            if 1901>year1 or year1>=year2 or year2>=year3 or year3>=year4 or year4>2018:
                raise ValueError('''The data includes the timespan from 1901 - 2018,
                                  the years have to be given in ascending order!''')
            break
        except ValueError:
            print('''the years has to be given as an integer and in ascending order 
                   in the range of 1901-2018''')
    timespan = [year1, year2, year3, year4]
    return timespan
    

def check_timespan(year1, year2, year3, year4):
    """
    author: Leo
    
    checks if the years for the timespans the user gets in the get_timespan() function
    are valid.
    
    If not, a ValueError for a wrong order or wrong years is raised, if input isn't
    an integer a TypeError is raised
    If the input is valid, the function returns again a list of the 4 border years
    """
    
    timespan = [year1, year2, year3, year4]
    
    #check if 4 years are given
    if len(timespan) != 4:
        raise ValueError('''expected number of years for the input is 4.
                         Start- and endyear for each of the two period''')
    #check if the years are of class integer                     
    elif any(type(n) is not int for n in timespan):  
        raise TypeError('expected input type is an integer')
    #check if the years are in the data range and in the right order
    elif 1901>year1 or year1>=year2 or year2>=year3 or year3>=year4 or year4>2018:
        raise ValueError('''The data includes the timespan from 1901 - 2018,
                         the years have to be given in ascending order!''')
    else: return timespan
    
def get_month():
    """
    Get month for which the snow data is viusalized.
    
    author: Paula
    
    Returns
    -------
    int
        Month for which data is shown
    """
    month = int(input('Which month should be shown? Please give the number of the month.'))
    return month

def valid_month(month):
    """
    Test if the input month is valid. In this month the snow data is viusalized.
    
    author: Paula
    
    Parameters
    -------
    month : int
        Month for which data is shown
        
    Raises
    -------
    TypeError
        When the type of ``month`` is not an integer.
    ValueError
        When the ``month`` is not between 1 and 12.
    
    """   
   
    if type(month) != int:
        raise TypeError('The month should be an integer')
    if month not in np.linspace(1,12,12):
        raise ValueError('The number was not valid. The month is between 1 and 12.')
        
    return month
