###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

import procedural_compute.rad.menus as menus
import procedural_compute.rad.menus.scene as sceneMenu
import procedural_compute.rad.menus.material as materialMenu

import procedural_compute.rad.properties as properties
import procedural_compute.rad.operators as operators


def register():
    bpy.types.SCENE_PT_bm.append(sceneMenu.drawBasic)
    bpy.types.MATERIAL_PT_bm.append(materialMenu.drawBasic)
    return

def unregister():
    bpy.utils.unregister_class(menus.camera.DATA_PT_camera_bm)
    bpy.utils.unregister_class(menus.falsecolour.falsecolorPanel)
    bpy.utils.unregister_class(menus.threshold.thresholdPanel)
    bpy.types.SCENE_PT_bm.remove(sceneMenu)
    bpy.types.MATERIAL_PT_bm.remove(materialMenu)
    return
