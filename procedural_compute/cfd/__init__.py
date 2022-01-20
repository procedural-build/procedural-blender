###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

import procedural_compute.cfd.properties as properties
import procedural_compute.cfd.operators as operators
import procedural_compute.cfd.menus as menus

from procedural_compute.cfd.menus.scene import drawBasic as drawSceneMenu
from procedural_compute.cfd.menus.object import drawBasic as drawObjectMenu


def menu_add_cfdbb(self, context):
    return self.layout.operator("mesh.add_cfdbb", text="CFD-Domain", icon='MESH_CUBE')


def register():
    bpy.types.VIEW3D_MT_mesh_add.append(menu_add_cfdbb)
    #-----------------
    bpy.types.SCENE_PT_COMPUTE.append(drawSceneMenu)
    bpy.types.OBJECT_PT_COMPUTE.append(drawObjectMenu)
    return


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_add_cfdbb)
    #-----------------
    bpy.types.SCENE_PT_COMPUTE.remove(drawSceneMenu)
    bpy.types.OBJECT_PT_COMPUTE.remove(drawObjectMenu)
    return
