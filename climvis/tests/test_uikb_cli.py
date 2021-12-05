"""
Test for uibk_cli.py

Author: Brynjar
"""
import pytest
from climvis.uibkvis.uibk_cli import uibkvis_io, HELP_uibkvis


def test_no_browser(capsys):
    """
    Test for the --no-browser.
    """
    uibkvis_io(["-l", "i", "1", "--no-browser"])
    captured = capsys.readouterr()
    assert "File successfully generated at:" in captured.out


def test_no_arguments(capsys):
    """
    Test of uibkvis with empty system arguments. Should print the HELP
    """
    uibkvis_io([])
    captured = capsys.readouterr()
    assert HELP_uibkvis in captured.out


def test_error_bad_user_input(capsys):
    """
    Test of bad user input, which is handeled by a try/except, which should raise a KeyError
    """
    with pytest.raises(KeyError, match="Invalid input!"):
        uibkvis_io(["-l", "i", "2"])
    with pytest.raises(KeyError, match="Invalid input!"):
        uibkvis_io(["-l", "å", "1"])
