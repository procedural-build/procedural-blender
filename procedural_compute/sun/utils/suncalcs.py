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
from math import sin, cos, tan, degrees, radians, pi, acos, asin, atan2, floor

##This calculates the sun position        
def Solar_Pos (Long, Lat, TimeZone, Month, Day, Hour, Minute):
        
##  Calculates Julian Day - at arbitrary (epoch or 4713BC) year
    def J_Day(Month, Day): 
        monthDayList = [0,31,59,90,120,151,181,212,243,273,304,334]
        j_day = monthDayList[Month-1] + Day
        return j_day

    ##  Solar declination as per Carruthers et al:  
    def Dec(J_Day):
        t = 2 * pi * ((J_Day - 1) / 365.0)
        Dec = 0.322003 - 22.971 * cos(t) - 0.357898 * cos(2*t) - 0.14398 * cos(3*t) + 3.94638 * sin(t) + 0.019334 * sin(2*t) + 0.05928 * sin(3*t)
        #Convert degrees to radians.
        if (Dec > 89.9):
            Dec = 89.9
        if (Dec < -89.9):
            Dec = -89.9            
        Dec = radians(Dec)
        return Dec
    
    ##  Calculate the equation of time as per Carruthers et al.
    def EquationOfTime(J_Day):
        t = (279.134 + 0.985647 * J_Day) * (pi/180.0)
        fEquation = 5.0323 - 100.976 * sin(t) + 595.275 * sin(2*t) + 3.6858 * sin(3*t) - 12.47 * sin(4*t) - 430.847 * cos(t) + 12.5024 * cos(2*t) + 18.25 * cos(3*t)
        #Convert seconds to hours.
        fEquation = fEquation / 3600.00
        return fEquation
    
    ##  Calculate Local Time
    def Local_Time(Hour, Minute):
        fLocal = Hour + (Minute/60.0)
        return fLocal

    ##  Calculate solar time.
    def Solar_Time(fLongitude, fLatitude, fTimeZone, fLocalTime, fEquation):

        # Calculate difference (in minutes) from reference longitude.
        fDifference = degrees(fLongitude - fTimeZone) * 4 / 60.0
    
        # Convert solar noon to local noon.
        local_noon = 12.0 - fEquation - fDifference
    
        # Calculate angle normal to meridian plane.
        if (fLatitude > (0.99 * (pi/2.0))):
            fLatitude = (0.99 * (pi/2.0))
        if (fLatitude < -(0.99 * (pi/2.0))):
            fLatitude = -(0.99 * (pi/2.0))
              
        test = -tan(fLatitude) * tan(fDeclination)
    
        if (test < -1):
            t = acos(-1.0) / (15 * (pi / 180.0))
        elif (test > 1):
            t = acos(1.0) / (15 * (pi / 180.0))
        else:
            t = acos(-tan(fLatitude) * tan(fDeclination)) / (15 * (pi / 180.0))
    
        # Sunrise and sunset.
        fSunrise = local_noon - t
        fSunset  = local_noon + t
    
        # Check validity of local time.
        if (fLocalTime > fSunset):
            fLocalTime = fSunset
        if (fLocalTime < fSunrise):
            fLocalTime = fSunrise
        if (fLocalTime > 24.0):
            fLocalTime = 24.0
        if (fLocalTime < 0.0):
            fLocalTime = 0.0
    
        # Calculate solar time.
        fSolarTime = fLocalTime + fEquation + fDifference
    
        return (fSolarTime, fSunrise, fSunset)
    
##  Calculate Sun Hour Angle
    def H_Ang(fSolarTime):

        fHourAngle = 15 * (fSolarTime - 12) * (pi/180.0)
        return fHourAngle
    
##  Calculate current altitude
    def Alt(fLatitude, fDeclination, fHourAngle): 
    
        t = sin(fDeclination) * sin(fLatitude) + cos(fDeclination) * cos(fLatitude) * cos(fHourAngle)
        fAltitude = asin(t)

        return fAltitude
    
##  Calculates Sun Azimuth
    def Az(fLatitude, fAltitude, fDeclination, fHourAngle):

        t = (cos(fLatitude) * sin(fDeclination)) - (cos(fDeclination) * sin(fLatitude) * cos(fHourAngle))
    
        # Avoid division by zero error.
        if (fAltitude < (pi/2.0)):
            sin1 = (-cos(fDeclination) * sin(fHourAngle)) / cos(fAltitude)
            cos2 = t / cos(fAltitude)

        else:
            sin1 = 0.0
            cos2 = 0.0
        
        # Some range checking.
        if (sin1 > 1.0):
            sin1 = 1.0
        if (sin1 < -1.0):
            sin1 = -1.0
        if (cos2 < -1.0):
            cos2 = -1.0
        if (cos2 > 1.0):
            cos2 = 1.0
        
        # Calculate azimuth subject to quadrant.
        if (sin1 < -0.99999):
            fAzimuth = asin(sin1)
        elif ((sin1 > 0.0) & (cos2 < 0.0)):
            if (sin1 >= 1.0):
                fAzimuth = -(pi/2.0)
            else:
                fAzimuth = (pi/2.0) + ((pi/2.0) - asin(sin1))
        elif ((sin1 < 0.0) & (cos2 < 0.0)):
            if (sin1 <= -1.0):
                fAzimuth = (pi/2.0)
            else:
                fAzimuth = -(pi/2.0) - ((pi/2.0) + asin(sin1))
        else:
            fAzimuth = asin(sin1)
    
        # A little last-ditch range check.
        if ((fAzimuth < 0.0) & (fLocalTime < 10.0)):
            fAzimuth = -fAzimuth

        return fAzimuth

    ##  Tell the script what to do

    # convert latitude, longitude and timezone to radians
    Lat = radians(Lat)
    Long = radians(Long)
    TimeZone = radians(TimeZone * 15)
   
    # get Julian Day
    if Month == []:
        Julian = Day
    else:
        Julian = J_Day(Month, Day)

    # get Declination
    fDeclination = Dec(Julian)

    # get Equation of Time
    fEquation = EquationOfTime(Julian)

    # get Local Time
    fLocalTime = Local_Time(Hour, Minute)

    # get Solar Time
    fSolarTime = Solar_Time(Long, Lat, TimeZone, fLocalTime, fEquation)
    fSunrise = fSolarTime[1]
    fSunset = fSolarTime[2]

    # get Hour Angle
    Hour_Angle = H_Ang(fSolarTime[0])

    # get Altitude
    fAltitude = Alt(Lat, fDeclination, Hour_Angle)

    # get Azimuth    
    fAzimuth = Az(Lat, fAltitude, fDeclination, Hour_Angle)

    ##  Prepare output values

    # Output Declination.
    fDeclination = degrees(fDeclination)

    # Output equation of time.
    fEquation = fEquation * 60

    # Output altitude value.
    fAltitude = degrees(fAltitude)

    # Output azimuth value.
    fAzimuth = degrees(fAzimuth)

    # Output solar time.
    t = int(floor(fSolarTime[0]))
    m = int(floor((fSolarTime[0] - t) * 60.0))
    if (m < 10):
        minute = "0" + str(m)
    else: minute = m
    if (t < 10):
        hour = "0" + str(t)
    else:
        hour = t
    sSolarTime = str(hour) + ":" + str(minute)

    # Output sunrise time.
    t = int(floor(fSunrise))
    m = int(floor((fSunrise - t) * 60.0))
    if (m < 10):
        minute = "0" + str(m)
    else:
        minute = m
    if (t < 10):
        hour = "0" + str(t)
    else:
        hour = t
    sSunrise = str(hour) + ":" + str(minute)

    # Output sunset time.
    t = int(floor(fSunset))
    m = int(floor((fSunset - t) * 60.0))
    if (m < 10):
        minute = "0" + str(m)
    else:
        minute = m
    if (t < 10):
        hour = "0" + str(t)
    else:
        hour = t
    fSunset = str(hour) + ":" + str(minute)

    # This last line is what Python returns to you, in this case:
    # Declination, Equation, Azimuth, Altitude, SolarTime, Sunrise, Sunset 
    #return (fDeclination, fEquation, fAzimuth, fAltitude, sSolarTime, sSunrise, fSunset)
    return (fAzimuth, fAltitude)

def getNames(objList):
    N = len(objList)
    Names = ['']*N
    for n in range(N):
        Names[n] = objList[n].name
    return Names

def azElToPolar(Az, El):
    sc = bpy.context.scene
    R = sc.procedural_compute.sun.arcRadius*((pi/2)-El)/(pi/2)
    X = R*sin(Az)
    Y = R*cos(Az)
    Z = 0.0
    return [X,Y,Z]

def azElToXYZ(Az, El):
    sc = bpy.context.scene
    R = sc.procedural_compute.sun.arcRadius
    X = R*cos(El)*sin(Az)
    Y = R*cos(El)*cos(Az)
    Z = R*sin(El)
    return [X,Y,Z]

def applySolarAzElCurves(ob):
    print("Applying solar curves to selected object...")

    # Get currently selected object
    sc = bpy.context.scene
    N = sc.Site.northAxis
    
    # Clear animation data
    ob.animation_data_clear()

    dt = sc.procedural_compute.sun.solarDT
    Long = sc.Site.longitude
    Lat = sc.Site.latitude
    TimeZone = sc.Site.timezone
    Month = sc.procedural_compute.sun.month
    Day = sc.procedural_compute.sun.day

    # Step through all frames and define Sun Path
    cc = 0
    #for Day in range(180,181):
    for Hour in range(24):
        for T in range(dt):
            Minute = T*(60/dt)
            (Az, El) = Solar_Pos(Long, Lat, TimeZone, Month, Day, Hour, Minute)
            # Adjust the azimuth to the site rotation and get LocX, LocY and LocZ position of sun
            (X,Y,Z) = azElToXYZ(radians(Az)+N, radians(El))
            # Get rotations about x, y and z-axes to always target 0,0,0
            Ry = 0.0
            Rxy = (X**2 + Y**2)**0.5
            Rx = (atan2(Rxy,Z))
            Rz = atan2(X,-1.0*Y)
            # Define a position vector
            PVec = [X,Y,Z,Rx,Ry,Rz]
            
            # Set the current frame
            sc.frame_current = cc
            ob.location = [PVec[0],PVec[1],PVec[2]]
            ob.rotation_euler = [PVec[3],PVec[4],PVec[5]]
            ob.keyframe_insert("location")
            ob.keyframe_insert("rotation_euler")

            # Increment the counter                
            cc += 1
    
    # Set the ending frame for animations
    sc.frame_end = cc-1
    sc.frame_start = 0
    sc.frame_current = int(cc/2)
    print("Done")
    return None
