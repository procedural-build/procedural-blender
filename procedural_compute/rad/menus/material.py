###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

import procedural_compute.rad.properties.material
from procedural_compute.core.utils.blendmeUtils import drawCollectionTemplateList


def drawBasic(self, context):
    layout = self.layout
    sc = context.scene
    mat = context.material

    # Skip this menu if the mainMenu is not pointing to CFD
    if sc.Compute.mainMenu != "Radiance":
        return

    if mat == None:
        return

    layout.row().label(text="Outside->Inside = Top->Bottom")
    mat.RAD.drawMenu(layout)

    return
