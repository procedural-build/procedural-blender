###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

from .operators import *
from .menus.scene import drawBasic
from .operators.ops import addClock


def menu_add_clock(self, context):
    return self.layout.operator(addClock.bl_idname, text="Clock", icon='MESH_CIRCLE')


def register():
    bpy.types.VIEW3D_MT_mesh_add.append(menu_add_clock)
    #------------------
    bpy.types.SCENE_PT_bm.append(drawBasic)
    return


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_add_clock)
    #------------------
    bpy.types.SCENE_PT_bm.remove(drawBasic)
    return
