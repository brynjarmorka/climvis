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


def cruvis_io(args, timespan, add_clim_change_and_solar, date=None, elev=True):
    """The actual command line tool.

    changed by Paula and Leo

    Parameters
    ----------
    args: list
        output of sys.args[1:]
    timespan, month and add_clim_change_and_solar are given as userinput
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
           
        # extract city and country argument if --no-browser is in argument
        args2 = args.copy()
        if "--no-browser" in args:
            args.remove("--no-browser")

        # get coordinates of selected city
        city = args[1]
#        if ((add_clim_change_and_solar == 's')
#            or (add_clim_change_and_solar =='both')):
#            elev=True
        coord = climvis.core.coordinates_city(city,elev)

        # Check if there are more cities with the same name
        if len(coord) > 1:
            if len(args) == 3:
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

        # Check if city is available in list
        if coord.empty and (elev == True):
            cruvis_io(sys.argv[1:], timespan, add_clim_change_and_solar, date, None)
            raise Warning(
                f'Trying to find city in an larger list of cities, but without elevation data '
                f' Attention: UV-Index is calculated as if the city is at sea level')
        if coord.empty:
            raise ValueError(
                f'The city {city} -and corresponding country- does not exist in the available list of cities. Please '
                f'try another city nearby! Also, cities with whitespace must be written with quotation marks. ')

        # Check if selected city is in selected country
        if len(args) == 3:   
            country = args[2]
            if (coord['Country'] != country).item():
                raise ValueError(f'The city {city} does not exist in {country}')

        lon = float(coord["Lon"].item())
        lat = float(coord["Lat"].item())
        if elev is True:
            Altitude = float(coord["Elevation"].item())
        elif elev is None:
            Altitude = None
        
        

        html_path = climvis.write_html(lon, lat, timespan, city, date, Altitude)    
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
    
    The code asks here for the needed user input and calls the cruvis_io 
    function with the user input as parameters
    """

    # Minimal code because we don't want to test for sys.argv
    # (we could, but this is too complicated for now)

    if len(sys.argv) >= 3 and "-l" in sys.argv:
        add_clim_change_and_solar = user_input()    
        
        #if yes the user can give the two timespans as input arguments
        if add_clim_change_and_solar == 'c':
            timespan = get_timespan()
            year1, year2, year3, year4 = timespan
            timespan = check_timespan(year1, year2, year3, year4)
            date = None
        elif add_clim_change_and_solar == 'both':
            timespan = get_timespan()
            year1, year2, year3, year4 = timespan
            timespan = check_timespan(year1, year2, year3, year4)
            datetime = get_datetime()
            date = valid_datetime(datetime)
        # if not 4 standard years are given to the rest of the code
        elif add_clim_change_and_solar == 'no':
            timespan = [1901, 1980, 1981, 2018]
            date = None
        elif add_clim_change_and_solar == "s":
            datetime = get_datetime()
            date = valid_datetime(datetime)
            timespan = [1901, 1980, 1981, 2018]
        #ask for the month of which the snowcover is wanted

    
    else: 
        timespan, add_clim_change_and_solar, date = None, None, None
    
    cruvis_io(sys.argv[1:], timespan, add_clim_change_and_solar, date)
    return timespan


def user_input():


    """
    asks the user if climate change and sun position info  
    information is wanted for custom times
   
    author: Leo
    changed: Sebastian
     
    Raises
    ------ 
    ValueError if input is different from options
     
    Returns
    -------
    add_clim_change: string
                     either c, s, both or no
    """

    while True:
        try:
            add_clim_change_and_solar = str(input(
''' Choosing custom times: 
type either  c       for customizing the temperature timeseries periods
             s       to customize your time of interest for sun position
             both    to specify both of the above 
             no      for default values:
                     Temperature timeseries:
                         1901-1980 and 1981-2018 
                     Sun position info:
                         current time and date
->'''))
            if (add_clim_change_and_solar != 'c' 
                and add_clim_change_and_solar != 'no'
                and add_clim_change_and_solar != 's'
                and add_clim_change_and_solar != 'both'):
                raise ValueError('input has to be one of the following: c s both no')
            break
        except ValueError:
            print('Invalid Input')
    return add_clim_change_and_solar
     

def get_datetime():
    """
    author: Sebastian
    
    function to ask the user for a date in which he is interrested in the solar 
    Position and UV-Index
    
    Returns 
    -------
    datetime : str
        a string with year month day hour and minute 
        e.g. 200001010000 for January 1st 2000  00:00UTC
    """
    datetime = input("put in your date and time of interest in UTC "
                             f"in the format: yyyymmddHHMM \nor type no if " 
                             f"you want to use the current time: ")
    return datetime


def valid_datetime(datetime):
    """
    autor Sebastian

    Control of validity of the given string
    
    Parameters
    ----------
    datetime : str
        Value from Userinput    

    Raises
    ------
    TypeError
        Not just digits in input.
    ValueError
        Out of bounds for month hour day or minute.

    Returns
    -------
    datetime : str
        Parameter datetime
    """

    if not ((datetime == 'no') or (datetime.isdigit())):
        raise TypeError('The datetime should be a 12 digit integer or no')
    elif datetime =='no':
        return datetime
    else:
        if len(datetime) != 12:
            raise ValueError(''' the inputted datetime has to be 12 long''')
        elif ((int(datetime[4]) == 1 and int(datetime[5]) > 2)
                or int(datetime[4]) > 1):
            raise ValueError(''' Something wrong in datetime, month: '''
                             + datetime[4] + datetime[5]
                             + '''doesn't exist''')
        elif (int(datetime[8]) == 2 and int(datetime[9]) > 4
                or int(datetime[8]) > 2):
            raise ValueError(''' Something wrong in datetime, hour: '''
                                 + datetime[8] + datetime[9]
                                 + '''doesn't exist''')
        elif int(datetime[10]) > 6:
            raise ValueError(''' Something wrong in datetime, minute: '''
                             + datetime[10] + datetime[11]
                             + '''doesn't exist''')
        else:
            return datetime
      
            
            


def get_timespan():
    """
    function to ask the user for the two timespans which he wants to compare
    returns a list of the 4 border years
    author: Leo
     
    Raises
    ------
    ValueError if they aren't in ascending order or outside the datarange 
     
    Returns
    -------
    timespan: list of the 4 years 
     
    """
     
    while True:
        try:
            year1 = int(input('start year of first timespan: '))
            year2 = int(input('end year of first timespan: '))
            year3 = int(input('start year of second timespan: '))
            year4 = int(input('end year of second timespan: '))
              
            if (1901>year1 or year1>=year2 or year1>=year3 or year1>=year4
                or year2>=year4 or year3>=year4 or year4>2018):
            #if 1901>year1 or year1>=year2 or year2>=year3 or year3>=year4 or year4>2018:
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
    checks if the years for the timespans the user gets in the get_timespan() function
    are valid.
    
    author: Leo
    
    Parameters
    ----------
    year1-year4: int
                 the 4 years which are given as an userinput two specify the 
                 two compared timespans
                 
    Raises
    ------
    ValueError if there aren't 4 years 
    ValueError if they aren't in ascending order or outside the datarange
    TypeError  if they aren't given as an integer
    
    Return
    ------
    timespan: list of the 4 years 
    
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
    elif (1901>year1 or year1>=year2 or year1>=year3 or year1>=year4
        or year2>=year4 or year3>=year4 or year4>2018):
        raise ValueError('''The data includes the timespan from 1901 - 2018,
                         the years have to be given in ascending order!''')
    else: return timespan
    
