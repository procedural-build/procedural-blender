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

import procedural_compute.rad.properties.scene
from procedural_compute.core.utils.blendmeUtils import drawCollectionTemplateList

def drawBasic(self, context):
    layout = self.layout
    sc = context.scene

    # Skip this menu if the mainMenu is not pointing to CFD
    if sc.ODS.mainMenu != "Radiance":
        return
    sc.RAD.draw(layout)
