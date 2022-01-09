#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 23:58:48 2022

@author: Sebastian

This tool visualizes the Solar path for one day and expected UV index
for every month and choosen or current time in the City.

The calculations done are basic geometry, assuming a spherical eart with 
circular sun Orbit, so it is a tool for a fast overview, not for exactest
data. 

UV-Index is defined as a factor times a weighted integral over UV-Wavelenghts. 
However in this function it is estimated by the use of known values and
taking into account solar elevation and the lenght of atmosphere between sun
and the given location (altitude of location)
Therefore the tablefrom https://de.wikipedia.org/wiki/UV-Index was
"""

import matplotlib.pyplot as plt  # plotting library
import numpy as np  # numerical library
from datetime import datetime as dt
import pytz


    # getting current datetime
def calculate_declination(date):
    """This Function  calculates solar declination angle for a given day"""
    dayofyear = float(dt.strftime(date, "%j"))  # optaining day of the year
    # calculating earth declination for given day of the year (simple formula)
    decl = np.deg2rad(-23.44) * np.cos(np.deg2rad(360 / 365 * (dayofyear + 10)))
    return decl


def calculate_hr_angle(lon, date):
    """This function calculates solar hour- angle for a given
    datetime and position, input of time in UTC."""
    # optaining hour + minute
    dectime = (float(dt.strftime(date, "%H"))
               + 1 / 60 * float(dt.strftime(date, "%M")))
    day = np.arange(0, 24, 1/12)  # 5 min intervallfor a day
    # calculating the true local time for any given longitude
    if dectime + lon / 15 < 0:
        day = np.append(day, dectime + lon/15 + 24)
    elif dectime +lon / 15 > 24:
        day = np.append(day, dectime + lon/15 - 24)
    else:
        day = np.append(day, dectime + lon/15)
    #and the hour-angle for every five minutes
    hr_angle = day * 15 - 180
    return hr_angle, day


def calculate_azimuth_and_elevation(lat, lon, date=None):
    """Calculating azimuth and elevation of the sun for given position and time
    at a fixed location, 
    
    returns azimuth and elevation in deg"""
    hr_angle = calculate_hr_angle(lon, date)[0]
    decl = calculate_declination(date)
    a = np.sin(np.deg2rad(lat)) * np.sin(decl)
    b = np.cos(np.deg2rad(lat)) * np.cos(decl) * np.cos(np.deg2rad(hr_angle))
    elevation = np.arcsin(a + b)
    x = (np.sin(decl) * np.cos(np.deg2rad(lat)))
    y = np.cos(decl) * np.sin(np.deg2rad(lat)) * np.cos(np.deg2rad(hr_angle))
    azimuth = np.arccos((x - y) / np.cos(elevation))
    # arccos is limited to the range of (0 - 180°) so our part of the circle
    # between 180° and 360° is mirrored
    azimuth_mirror = 2 * np.pi - azimuth[np.where(hr_angle > 0)]
    azimuth[np.where(hr_angle > 0)] = azimuth_mirror
    elevation = np.rad2deg(elevation)
    return azimuth, elevation


def get_season(date=None):
    '''Checking the season'''
    decl = calculate_declination(date)
    if decl < 0:
        season = "north winter"
    elif decl == 0:
        season = "north winter"
    else:
        season = "north summer"
    return season


def calculate_UV_Index(lat, lon, Altitude, date=None):
    """  This function generates an UV-Index estimate by Reengeneering
    the table from Wikipedia. 1367 W m-2 lead to UV Index of 12-13 in Singapur,
    at Sea level, when the atmospheare is penetrated in the shortest possible
    way (sunelevation is ~90°). """
    # UVI = TOA incomingn radiation pr m2 / (lenght through atmos * atm ext)
    # lenght = 1 /sin(elev)
    # UVI = sin(elev) * TOA /(1/sin(elev)* atm ext)
    # ext=sin(elev) ** 2 * 1367/UVI
    Atm_extinction_Singapur = 1367 / 12
    Atm_extinction_Sydney = np.sin(np.deg2rad(80)) ** 2 * 1367 / 10.5
    Atm_extinction_Mallorca = np.sin(np.deg2rad(75)) ** 2 * 1367 / 9
    Atm_extinction_Berlin = np.sin(np.deg2rad(62)) ** 2 * 1367 / 7
    Atm_extinction_Petersburg = np.sin(np.deg2rad(54)) ** 2 * 1367 / 5
    # here we get a mean atmosphearic extinction coefficient
    mean_Atm_extinct = (Atm_extinction_Berlin
                        + Atm_extinction_Mallorca
                        + Atm_extinction_Petersburg
                        + Atm_extinction_Singapur
                        + Atm_extinction_Sydney) / 5
    # optaining solar elevtions (daily max and current)
    elevation_now = calculate_azimuth_and_elevation(lat, lon, date)[1][-1]
    elevation_noon = calculate_azimuth_and_elevation(lat, lon, date)[1][144]
    if elevation_now < 0:
        elevation_now = 0
        night = True
    else:
        night = False
    elevation = [elevation_noon, elevation_now]
    # Pressure height Standartatmosphere for elevation correction
    local_pressure = 1013.25 * (1 - 6.5 * Altitude / 288150) ** 5.255
    pressure_height = local_pressure / 1013.25
    # Calculating UV-Index
    UVI = 1367 * np.sin(np.deg2rad(elevation)) ** 2 / (mean_Atm_extinct
                                                       * pressure_height)
    return UVI, night


def get_sunrise_sunset(lat, lon, date=None):
    ''' This function optains sunrise and sunset time and sunshine duration'''
    elev = calculate_azimuth_and_elevation(lat, lon, date)[1][:-1]
    # find datapoints where sun is above horizon
    mask = np.where(elev > 0)
    # get the time
    time = calculate_hr_angle(lon, date)[1][:-1]
    sunshine = time[mask]
    # take first and last above horizon vlues
    sunrise = sunshine[0]
    sunset = sunshine[-1]
    sunshine_dur = sunset-sunrise
    return sunrise, sunset, sunshine_dur


def translate_time(x):
    '''translation from hours with decimal minutes to readable times'''
    y = str(int(x)).zfill(2) + ":" + str(int((x*60) % 60)).zfill(2)
    return y


def plot_solar_elevation(lat, lon, Altitude, date, filepath=None):
    ''' The plotting routine of solar_path and UV-Index
    
    returns a plot'''
    # time is essential so eithr use input or get the current utc
    if date =='no':
        date = dt.now(pytz.timezone('utc'))
    else:
        date = dt.strptime(date, "%Y%m%d%H%M")
    # colormap for the UV-Index
    clist =(["lime"] * 3 + ["yellow"] * 3 + ["orangered"] * 3
            + ["magenta"] * 3)
    # calling the functions to get azimuth, elevation, sun-times UV-Index
    a = calculate_azimuth_and_elevation(lat, lon, date)
    b = get_sunrise_sunset(lat, lon, date)
    UVI, night = calculate_UV_Index(lat, lon, Altitude, date)
    # designing the figure
    fig = plt.figure()
    # position, time and sun related times are given as text in the figure
    fig.text(0.15, -0.25, 'Valid local time: '
             + translate_time(calculate_hr_angle(lon, date)[1][-1])
             + "\nSunrise = " + translate_time(b[0]) + " local time"
             + "\nSunset = " + translate_time(b[1]) + " local time"
             + "\nSunshine_duration = " + translate_time(b[2])
             + "h", fontsize=10)
    fig.text(0.55, -0.25, "Valid_date: " + dt.strftime(date, "%d-%b-%Y")
             + "\nLocation:\nLatitude= " + str(round(lat, 4))
             + "°\nLongitude = " + str(round(lon, 4)) + "°", fontsize=10)
    # get a polar axes
    ax1 = fig.add_axes([0, 0, 1, 1], polar=True)
    ax1.set_title("Solar Path", fontsize=22)
    # bringing north to the top and counting clockwise, setting limits
    ax1.set_theta_direction(-1)
    ax1.set_theta_offset(np.pi/2)
    ax1.set_xlim(2 * np.pi, 0)
    ax1.set_rlim(90, 0)
    ax1.set_xticks(np.pi/180.*np.arange(0, 360, 45))
    # ploting solar path and current sun position
    ax1.plot(a[0][:-1], a[1][:-1], color='gold')
    ax1.plot((a[0][-1]), a[1][-1], color='gold', marker="o", markersize=20)
    # find likely free space for the uv Index, making another axes hopefully
    # not atop the important plots
    if get_season(date) == "north winter":
        ax2 = fig.add_axes([.15, .7, .2, .3])
        ax1.set_rgrids([90, 60, 30, 0], angle=45, color='r')
        ax1.set_yticklabels(["90°", "60°", "30°", "solar\nelevation\n0°"],
                            fontsize=14, ha="center", va='bottom')
        ax1.set_xticklabels(["N", "", "E", "SE", "S", "SW", "W", "NW"],
                            fontsize=18)
    else:
        ax2 = fig.add_axes([.15, 0, .2, .3])
        ax1.set_rgrids([90, 60, 30, 0], angle=135, color='r')
        ax1.set_yticklabels(["90°", "60°", "30°", "0°\nsolar\nelevation"],
                            fontsize=14, ha="center", va='top')
        ax1.set_xticklabels(["N", "NE", "E", "", "S", "SW", "W", "NW"],
                            fontsize=18)
    # invisible axis and labels
    ax2.get_xaxis().set_visible(False)
    ax2.get_yaxis().set_visible(False)
    ax2.set_title("UV-Index", va="top", fontsize=18)
    # display UV-Index
    ax2.text(.5, .45, "max: " + str(round(UVI[0])) + "\nnow: "
             + str(round(UVI[1])), ha="center", va="center", fontsize=20)
    # check for night
    if night is True:
        ax2.text(.5, 0.025, "It is night!", va="bottom", ha="center")
    ax2.set_facecolor(clist[min(round(UVI[0]), 12)])
    
    if filepath is not None:
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()
    return fig
