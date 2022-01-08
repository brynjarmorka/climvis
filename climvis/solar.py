#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 23:58:48 2022

@author: Sebastian

This tool vizulizes the Solar path for one day and expected UV index
for every month and choosen or current time in the City

The calculations done are basic geometry, assuming a spherical eart with 
zirkular sun Orbit, also UV-Index 
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
def calculate_declination(date=None):
    """This Function  calculates solar declination angle for a given day"""
    dayofyear = float(dt.strftime(date, "%j"))  # optaining day of the year
    # calculating earth declination for given day of the year (simple formula)
    decl = np.deg2rad(-23.44) * np.cos(np.deg2rad(360 / 365 * (dayofyear + 10)))
    return decl


def calculate_hr_angle(lon, date=None):
    """This function calculates solar hour- angle for a given
    datetime and position."""
    # optaining hour + minute
    if date is None:
        date = dt.now(pytz.timezone('utc'))
    dectime = float(dt.strftime(date, "%H")) + 1/60 * float(dt.strftime(date, "%M"))
    day = np.arange(0, 24, 1/12)  # 5 min intervallfor a day
    day = np.append(day, dectime + lon/15)
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


def get_hemisphere(lat, date=None):
    decl = calculate_declination()
    if decl < np.deg2rad(lat):
        hemi = "north"
    else:
        hemi = "south"
    return hemi


def calculate_UV_Index(lat, lon, date=None):
    """ UV Index is defined as 0.04 m² W⁻¹ * spectral flux in UV range
    (lambda 280-400) Integrated with referenzspectrum"""
    elev = calculate_azimuth_and_elevation(lat, lon, date)[1]
    #from https://www.fs-ev.org/fileadmin/user_upload/04_Arbeitsgruppen/08_Nichtionisierende_Strahlung/02_Dokumente/Leitfaeden/Leitfaden-Sonnenstrahlung-_AKNIR-29112012.pdf
    Solar_Spectrum_UVA = 1367 * 0.065 *np.sin(np.deg2rad(elev[-1]))
    Solar_Spectrum_UVB = 1367 * 0.015 *np.sin(np.deg2rad(elev[-1]))
    #Referenzspektrum zur berechnung des UVI, genähert
    RWSA = 10 ** (0.015 *(139-360))
    RWSB = 10 ** (0.094 *(298-300))
    TOA_UV_Index = Solar_Spectrum_UVA * RWSA + Solar_Spectrum_UVB *RWSB
    return TOA_UV_Index


def get_sunrise_sunset(lat, lon, date=None):
    elev = calculate_azimuth_and_elevation(lat, lon, date)[1][:-1]
    mask = np.where(elev > 0)
    time = calculate_hr_angle(lon)[1][:-1]
    sunshine = time[mask]
    sunrise = sunshine[0]
    sunset = sunshine[-1]
    sunshine_dur = sunset-sunrise
#    sunrise = str(int(sunrise_dec)) + ":" + str((sunrise_dec*60) % 60)
#    sunshine_dur = str(int(sunshine_dur_dec)) + ":" + str((sunshine_dur_dec*60) % 60)
#    sunset = str(int(sunset_dec)) + ":" + str((sunset_dec*60) % 60)

    return sunrise, sunset, sunshine_dur


def translate_time(x):
    y = str(int(x)) + ":" + str(int((x*60) % 60))
    return y


def plot_solar_elevation(lat, lon, date=None, filepath=None):
    lat, lon = np.rad2deg(lat), np.rad2deg(lon)
    if date is None:
        date = dt.now(pytz.timezone('utc'))
    a = calculate_azimuth_and_elevation(lat, lon, date)
    b = get_sunrise_sunset(lat, lon, date)
    fig = plt.figure()
    fig.text(0.15, -0.25, 'Valid local time: '
             + translate_time(calculate_hr_angle(lon, date)[1][-1])
             + "\nSunrise = " + translate_time(b[0]) + " local time"
             + "\nSunset = " + translate_time(b[1]) + " local time"
             + "\nSunshine_duration = " + translate_time(b[2])
             + "h", fontsize=10)
    fig.text(0.55, -0.25, "Valid_date: " + dt.strftime(date, "%d-%b-%Y")
             + "\nLocation:\nLatitude= " + str(lat) + "\nLongitude = "
             + str(lon), fontsize=10)
    ax1 = fig.add_axes([0, 0, 1, 1], polar=True)
    ax1.set_title("Solar Path", fontsize=22)
#    ax1.plot.subtitle("Location: Lon = " + str(lon) + "Lat = " +str(lat))
    ax1.set_theta_direction(-1)
    ax1.set_theta_offset(np.pi/2)
    ax1.set_xlim(2 * np.pi, 0)
    ax1.set_rlim(90, 0)
    ax1.set_rticks([90, 60, 30, 0])
    ax1.set_yticklabels(["90°", "60°", "30°", "0° Solar elevation"])
    ax1.set_xticks(np.pi/180.*np.arange(0, 360, 45))
    ax1.set_xticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
                        fontsize=18)
#    ax1.set_xlabel("Location:\nLatitude= " + str(lat) + "\nLongitude = "
#                   +str(lon),
#                   loc = "right", fontsize=10)
#    ax2=fig.add_axes([0, 0, 1, 1], polar=True)
#    ax2.set_frame_on(False)
#    ax2.get_xaxis().set_visible("False")
#    ax2.set_xlabel('hallo', loc = "right")
#    ax1.set_xlabel("Location: Latitude= " + str(lat) + "\nLongitude = " +str(lon)
#                   + "\nSunrise = " + b[0] + " local time"
#                   + "\nSunset = " + b[1] + " local time"
#                   + "\nSunshine_duration = " + b[2], loc = "right", fontsize=10)
    p1 = ax1.plot(a[0][:-1], a[1][:-1], color='gold')
    p2 = ax1.plot((a[0][-1]), a[1][-1], color ='gold', marker = "o", markersize=20)
    
    if filepath is not None:
        plt.savefig(filepath, dpi=150)
        plt.close()
        
    return fig
date=dt(2021,7,18,8,15)
plot_solar_elevation(np.deg2rad(25), 0, date)

#print(calculate_UV_Index(80, 0))

#if get_hemisphere(lat) == "north":
#        ax1.set_xticklabels(np.arange(0 , 24, 3),fontsize=18)
#    else:
#        ax1.set_xticklabels([12, 9, 6, 3, 0, 21, 18, 15],fontsize=18)
#    ax1.set_title('Solar Path',fontsize=20)