###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

import procedural_compute.rad.menus as menus

from procedural_compute.rad.menus.scene import drawBasic as drawSceneMenu
from procedural_compute.rad.menus.object import drawBasic as drawObjectMenu
from procedural_compute.rad.menus.material import drawBasic as drawMaterialMenu

import procedural_compute.rad.properties as properties
import procedural_compute.rad.operators as operators


def register():
    bpy.types.SCENE_PT_COMPUTE_CORE.append(drawSceneMenu)
    bpy.types.OBJECT_PT_COMPUTE.append(drawObjectMenu)
    bpy.types.MATERIAL_PT_bm.append(drawMaterialMenu)
    return

def unregister():
    bpy.utils.unregister_class(menus.camera.DATA_PT_camera_bm)
    bpy.utils.unregister_class(menus.falsecolour.falsecolorPanel)
    bpy.utils.unregister_class(menus.threshold.thresholdPanel)

    bpy.types.SCENE_PT_COMPUTE_CORE.remove(drawSceneMenu)
    bpy.types.OBJECT_PT_COMPUTE.remove(drawObjectMenu)
    bpy.types.MATERIAL_PT_bm.remove(drawMaterialMenu)
    return
