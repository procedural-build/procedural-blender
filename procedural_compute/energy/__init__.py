###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

import procedural_compute.energy.properties as properties
import procedural_compute.energy.operators as operators
import procedural_compute.energy.menus as menus

from procedural_compute.energy.menus.scene import drawBasic as drawSceneMenu
from procedural_compute.energy.menus.object import drawBasic as drawObjectMenu


def register():
    bpy.types.SCENE_PT_COMPUTE.append(drawSceneMenu)
    bpy.types.OBJECT_PT_COMPUTE.append(drawObjectMenu)
    return


def unregister():
    bpy.types.SCENE_PT_COMPUTE.remove(drawSceneMenu)
    bpy.types.OBJECT_PT_COMPUTE.remove(drawObjectMenu)
    return
