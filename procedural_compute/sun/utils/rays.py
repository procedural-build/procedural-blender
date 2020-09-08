###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

# Solar_Position
#
# The azimuth and altitude of the Sun are calculated using formulae first proposed by Spencer (Spencer, 1965),
# then refined by Szokolay (Szokolay, 1996). Values for solar declination and the equation of time
# are determined using formulae proposed by Carruthers, et al [1990]
#
# The math behind this calculation was taken from:
# http://squ1.org/wiki/Solar_Position_Calculator
# 
# And has been checked and modified slightly by Mark Pitman against information available at:
# http://www.srrb.noaa.gov/highlights/sunrise/calcdetails.html
# 
# Enter data in this way:
# Solar_Pos (Lat, Long, TimeZone, Month, Day, Hour)
# It will return (Altitude, Azimuth)
# Only Altitude and Azimuth are needed to trace the sun position, for that you will
# need the Sun_Trace.py script

import bpy
import datetime
from math import degrees, radians, sin, cos, tan
from procedural_compute.sun.utils.suncalcs import Solar_Pos

def rayToSun(hour, latitude, longitude, timezone, northAxis=0.0):
    date = datetime.datetime(2010,1,1) + datetime.timedelta(0, hour*3600)
    (az,el) = Solar_Pos(
            longitude, latitude, timezone,
            date.month, date.day, date.hour, date.minute)
    az = az + northAxis
    if el <= 0.1:
        x=0.0;y=0.0;z=-1.0;
    elif el >= 89.9:
        x=0.0;y=0.0;z=1.0;
    else:
        x = sin(radians(az))
        y = cos(radians(az))
        z = tan(radians(el))
    return (x,y,z)

