#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 23:58:48 2022

@author: Sebastian

This tool visualizes the Solar path for one day and expected UV index
for every month and choosen or current time in the City

The calculations done are basic geometry, assuming a spherical eart with 
circular sun Orbit, so it is a tool for a fast overview, not for exactest
data. 

UV-Index is defined as a factor times a weighted integral over UV-Wavelenghts
at a given location. 
However in this function it is estimated by the use of known values an also
taking into account solar elevation and the lenght of atmosphere between sun
and location (altitude of location)
reengeneered the table from https://de.wikipedia.org/wiki/UV-Index
"""
from climvis import cfg
import matplotlib.pyplot as plt  # plotting library
import numpy as np  # numerical library
import xarray as xr  # netCDF library
import cartopy  # Map projections libary
import cartopy.crs as ccrs  # Projections list
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
    datetime and position."""
    # optaining hour + minute
    dectime = (float(dt.strftime(date, "%H"))
               + 1 / 60 * float(dt.strftime(date, "%M")))
    day = np.arange(0, 24, 1/12)  # 5 min intervallfor a day
    if dectime + lon / 15 < 24:
        day = np.append(day, dectime + lon/15)
    else:
        day = np.append(day, dectime + lon/15 - 24)
    hr_angle = day * 15 - 180
    return hr_angle, day


def calculate_azimuth_and_elevation(lat,lon, date=None):
    """Calculating azimuth and elevation of the sun for given position and time
    at a fixed location, output is in deg"""
    hr_angle = calculate_hr_angle(lon, date)[0]
    decl = calculate_declination(date)
    a = np.sin(np.deg2rad(lat)) * np.sin(decl)
    b= np.cos(np.deg2rad(lat)) * np.cos(decl) * np.cos(np.deg2rad(hr_angle))
    elevation = np.arcsin(a + b)
    x = (np.sin(decl) * np.cos(np.deg2rad(lat)))
    y = np.cos(decl) * np.sin(np.deg2rad(lat)) * np.cos(np.deg2rad(hr_angle))
    azimuth = np.arccos((x - y) / np.cos(elevation))
    azimuth_mirror = 2 * np.pi - np.arccos((x - y) / np.cos(elevation))[np.where(hr_angle > 0)]
    azimuth[np.where(hr_angle > 0)] = azimuth_mirror
    elevation = np.rad2deg(elevation)
    return azimuth, elevation


def get_season(date=None):
    decl = calculate_declination(date)
    if decl < 0:
        season = "north winter"
    elif decl == 0:
        season = "north winter"
    else:
        season = "south"
    return season


def calculate_UV_Index(lat, lon, Altitude, date=None):
    """ Reengeneering the table from Wikipedia
     1367 W m-2 lead to UV Index of 12-13 in Singapur, at Sea level when the
    sunelevation is ~90°. """
    # UVI = TOA incomingn radiation pr m2 / (lenght through atmos * atm ext)
    # lenght = 1 /sin(elev)
    # UVI = sin(elev) * TOA /(1/sin(elev)* atm ext)
    # ext=sin(elev) ** 2 * 1367/UVI
    Atm_extinction_Singapur = 1367 / 12
    Atm_extinction_Sydney = np.sin(np.deg2rad(80)) ** 2 * 1367 / 10.5
    Atm_extinction_Mallorca = np.sin(np.deg2rad(75)) ** 2 * 1367 / 9
    Atm_extinction_Berlin = np.sin(np.deg2rad(62)) ** 2 * 1367 / 7
    Atm_extinction_Petersburg = np.sin(np.deg2rad(54)) ** 2 * 1367 / 5
    mean_Atm_extinct = (Atm_extinction_Berlin
                        + Atm_extinction_Mallorca
                        + Atm_extinction_Petersburg
                        + Atm_extinction_Singapur
                        + Atm_extinction_Sydney) / 5
    elevation = calculate_azimuth_and_elevation(lat, lon, date)[1][-1]
    # Pressureheight Standartatmosphere
    local_pressure = 1013.25 * (1 - 6.5 * Altitude / 288150) ** 5.255
    pressure_height = local_pressure / 1013.25
    UVI = 1367 * np.sin(np.deg2rad(elevation)) ** 2 / (mean_Atm_extinct 
                                                       * pressure_height)
    return UVI
#    """ UV Index is defined as 0.04 m² W⁻¹ * spectral flux in UV range
#    (lambda 280-400) Integrated with referenzspectrum"""
#    elev = calculate_azimuth_and_elevation(lat, lon, date)[1]
#    #from https://www.fs-ev.org/fileadmin/user_upload/04_Arbeitsgruppen/08_Nichtionisierende_Strahlung/02_Dokumente/Leitfaeden/Leitfaden-Sonnenstrahlung-_AKNIR-29112012.pdf
#    Solar_Spectrum_UVA = 1367 * 0.065 *np.sin(np.deg2rad(elev[-1]))
#    Solar_Spectrum_UVB = 1367 * 0.015 *np.sin(np.deg2rad(elev[-1]))
#    #Referenzspektrum zur berechnung des UVI, genähert
#    RWSA = 10 ** (0.015 *(139-360))
#    RWSB = 10 ** (0.094 *(298-300))
#    TOA_UV_Index = Solar_Spectrum_UVA * RWSA + Solar_Spectrum_UVB *RWSB
#    return TOA_UV_Index


def get_sunrise_sunset(lat, lon, date=None):
    elev = calculate_azimuth_and_elevation(lat, lon, date)[1][:-1]
    mask = np.where(elev > 0)
    time = calculate_hr_angle(lon, date)[1][:-1]
    sunshine = time[mask]
    sunrise = sunshine[0]
    sunset = sunshine[-1]
    sunshine_dur = sunset-sunrise
#    sunrise = str(int(sunrise_dec)) + ":" + str((sunrise_dec*60) % 60)
#    sunshine_dur = str(int(sunshine_dur_dec)) + ":" + str((sunshine_dur_dec*60) % 60)
#    sunset = str(int(sunset_dec)) + ":" + str((sunset_dec*60) % 60)

    return sunrise, sunset, sunshine_dur


def translate_time(x):
    y = str(int(x)).zfill(2) + ":" + str(int((x*60) % 60)).zfill(2)
    return y


def plot_solar_elevation(lat, lon, Altitude, date=None, filepath=None):
    lat, lon = np.rad2deg(lat), np.rad2deg(lon)
    if date is None:
        date = dt.now(pytz.timezone('utc'))
    clist =["lime"] * 3 + ["yellow"] * 3 + ["orangered"] * 3 + ["magenta"] * 3
    a = calculate_azimuth_and_elevation(lat, lon, date)
    b = get_sunrise_sunset(lat, lon, date)
    UVI = calculate_UV_Index(lat, lon, Altitude, date)
    fig = plt.figure()
    fig.text(0.15, -0.25, 'Valid local time: '
             + translate_time(calculate_hr_angle(lon, date)[1][-1])
             + "\nSunrise = " + translate_time(b[0]) + " local time"
             + "\nSunset = " + translate_time(b[1]) + " local time"
             + "\nSunshine_duration = " + translate_time(b[2])
             + "h", fontsize=10)
    fig.text(0.55, -0.25, "Valid_date: " + dt.strftime(date, "%d-%b-%Y")
             + "\nLocation:\nLatitude= " + str(round(lat, 4)) + "°\nLongitude = "
             + str(round(lon, 4)) + "°", fontsize=10)
    ax1 = fig.add_axes([0, 0, 1, 1], polar=True)
    ax1.set_title("Solar Path", fontsize=22)
#    ax1.plot.subtitle("Location: Lon = " + str(lon) + "Lat = " +str(lat))
    ax1.set_theta_direction(-1)
    ax1.set_theta_offset(np.pi/2)
    ax1.set_xlim(2 * np.pi, 0)
    ax1.set_rlim(90, 0)
    ax1.set_xticks(np.pi/180.*np.arange(0, 360, 45))
#    ax1.set_xlabel("Location:\nLatitude= " + str(lat) + "\nLongitude = "
#                   +str(lon),
#                   loc = "right", fontsize=10)
#    ax2=fig.add_axes([0, 0, 1, 1], polar=True)
#    
#    
#    ax2.set_xlabel('hallo', loc = "right")
#    ax1.set_xlabel("Location: Latitude= " + str(lat) + "\nLongitude = " +str(lon)
#                   + "\nSunrise = " + b[0] + " local time"
#                   + "\nSunset = " + b[1] + " local time"
#                   + "\nSunshine_duration = " + b[2], loc = "right", fontsize=10)
    p1 = ax1.plot(a[0][:-1], a[1][:-1], color='gold')
    p2 = ax1.plot((a[0][-1]), a[1][-1], color ='gold', marker = "o", markersize=20)
    if get_season(date) == "north winter":
        ax2 = fig.add_axes([.15, .7, .2, .3])
        ax1.set_rgrids([90, 60, 30, 0], angle=45, color='r')
        ax1.set_yticklabels(["90°", "60°", "30°", "solar\nelevation\n0°"],
                            fontsize=14, ha="center", va='bottom')
        ax1.set_xticklabels(["N", "", "E", "SE", "S", "SW", "W", "NW"],
                            fontsize=18)
    else:
        ax2 = fig.add_axes([.15, 0, .2,.3])
        ax1.set_rgrids([90, 60, 30, 0], angle=135, color='r')
        ax1.set_yticklabels(["90°", "60°", "30°", "0°\nsolar\nelevation"],
                            fontsize=14, ha="center", va='top')
        ax1.set_xticklabels(["N", "NE", "E", "", "S", "SW", "W", "NW"],
                            fontsize=18)
    ax2.get_xaxis().set_visible(False)
    ax2.get_yaxis().set_visible(False)
    ax2.set_title("UV-Index", va="top", fontsize=18)
    ax2.text(.5, .45, str(int(UVI)), ha="center",va="center", fontsize=48)
    ax2.set_facecolor(clist[int(UVI)])
    if filepath is not None:
        plt.savefig(filepath, dpi=150)
        plt.close()
        
    return fig
#date=dt(2021,7,18,8,15)
plot_solar_elevation(np.deg2rad(30), np.deg2rad(180), 2000)

print(calculate_UV_Index(30, 180, 2000, dt.now(pytz.timezone('utc'))))

#if get_hemisphere(lat) == "north":
#        ax1.set_xticklabels(np.arange(0 , 24, 3),fontsize=18)
#    else:
#        ax1.set_xticklabels([12, 9, 6, 3, 0, 21, 18, 15],fontsize=18)
#    ax1.set_title('Solar Path',fontsize=20)