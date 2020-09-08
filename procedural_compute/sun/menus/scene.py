###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

import procedural_compute.sun.properties.scene
from procedural_compute.sun.utils.timeFrameSync import frameToTime


def drawBasic(self, context):
    layout = self.layout
    sc = context.scene

    # Skip this menu if the mainMenu is not pointing to Sun
    if sc.ODS.mainMenu != "SunPath":
        return

    # Syncronise the time variables with the frame
    #bpy.ops.scene.timesync()

    row = layout.row()
    row.operator("scene.calcsolarpath", text="Apply Solar Path")

    split = layout.split()
    col = split.column()
    col.prop(sc.ODS_SUN, "solarDT")
    col.prop(sc.ODS_SUN, "day")
    #col.prop(sc.ODS_SUN, "hour")
    col = split.column()
    col.prop(sc.ODS_SUN, "arcRadius")
    col.prop(sc.ODS_SUN, "month")
    #col.prop(sc.ODS_SUN, "minute")

    #(hour,minute) = frameToTime(sc.frame_current)
    #layout.row().label(text="Current Local Time = " + "%02i"%hour + ":" + "%02i"%minute )
    return
