###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

def frameToTime(frame):
    sc = bpy.context.scene
    solarDT = sc.ODS_SUN.solarDT

    # Get the hour and minute from the current frame and timestep size
    hour = int(frame/solarDT)
    minute = (frame - (solarDT*hour))*int(60/solarDT)

    return hour, minute

def timeToFrame(hour, minute):
    sc = bpy.context.scene
    solarDT = sc.ODS_SUN.solarDT

    # Loop minutes around (in case specified minutes are greater than 60 or less than 0)
    if minute >= 60:
        minute = 0
    elif minute < 0:
        minute = 59

    # Sync minutes with timesteps per hour (round it up or down)
    RM = round(minute/int(60/solarDT))*int(60/solarDT)
    DM = minute - RM
    if DM > 0:
        minute = (int(minute/int(60/solarDT))+1)*int(60/solarDT)
    elif DM < 0:
        minute = (int(minute/int(60/solarDT)))*int(60/solarDT)

    # Sync hour/minute with current frame
    frame_current = (hour * solarDT) + int(minute / int(60/solarDT))

    return frame_current

def getTimeStamp():
    sc = bpy.context.scene
    (hour, minute) = frameToTime(sc.frame_current)
    timestamp = "%02d%02d_%02d%02d"%(sc.ODS_SUN.month, sc.ODS_SUN.day, hour, minute)
    return timestamp
