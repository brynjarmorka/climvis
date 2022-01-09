# Testing command line interfaces is hard. But we'll try
# At least we separated our actual program from the I/O part so that we
# can test that
"""
changed by Leo
Tests for the functions of the climvis.cli file with the needed input Parameters
tried to test for user input with unittest.mock
"""

import climvis
import pytest
from climvis.cli import cruvis_io, get_month, user_input
from unittest import mock



def test_help(capsys):

    # Check that with empty arguments we return the help
    cruvis_io([], [], [], [])
    captured = capsys.readouterr()
    assert "Usage:" in captured.out
    print(captured.out)

    cruvis_io(["-h"], [], [], [])
    captured = capsys.readouterr()
    assert "Usage:" in captured.out

    cruvis_io(["--help"], [], [], [])
    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_version(capsys):

    cruvis_io(["-v"], [], [], [])
    captured = capsys.readouterr()
    assert climvis.__version__ in captured.out
    
def test_get_month():
    """
    testing for command line input
    attempt to test if the get_month function works if 
    the user input is valid
    """
    
    with mock.patch('builtins.input', return_value=1):
        assert get_month()==1
    with mock.patch('builtins.input', return_value=5):
        assert get_month()==5
    with mock.patch('builtins.input', return_value=10):
        assert get_month()==10
        
<<<<<<< HEAD
#def test_user_input():
=======
def test_user_input():
    """
    testing for command line input
    attempt to test if the user_input function works if 
    the user input is valid
    """
>>>>>>> 83579a728fce8f8376552ff965d9c52136d0ac91
    
#    with mock.patch('builtins.input', return_value="yes"):
#        assert user_input()=='yes'
#    with mock.patch('builtins.input', return_value="no"):
#        assert user_input()=='no'
    


def test_print_html(capsys):#, monkeypatch):
        
    timespan = [1901, 1970, 1971, 2018]
    month = 2
    add_clim_change = "c"
    cruvis_io(["-l", "Berlin", "Germany", "--no-browser"], timespan, month, add_clim_change)
    captured = capsys.readouterr()
    assert "File successfully generated at:" in captured.out
    


def test_error_1argument(capsys):

    cruvis_io(["-l"], [], [], [])
    captured = capsys.readouterr()
    assert "cruvis --loc needs city parameter!" in captured.out

# This test is not working correctly because the user now selects city manually with an input when len(coords) > 1.
# Since it is user input, the testing of the input is done with try/except within an while-loop, in the cli.py file.
# def test_error_2cities():
#     with pytest.raises(ValueError, match = 'There are more cities with the name Berlin.'
#                                  'Please add the country of the city as input!'):
#         cruvis_io(["-l", "Berlin"])


def test_error_wrongcountry(capsys):
    
    with pytest.raises(ValueError, match = 'The city Innsbruck does not exist in Germany'):
        cruvis_io(["-l", "Innsbruck", "Germany"], [], [], [])
        
def test_error_not_available_city():
    # The available city in the list is Munich
    with pytest.raises(ValueError, match = 'The city München -and corresponding country- does not exist in the available list of cities. Please try another city nearby!'):
        cruvis_io(["-l", "München"], [], [], [])
        