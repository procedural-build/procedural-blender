###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ods-engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################

"""
A base-module of classes and function definitions that are
called by other modules of the ODS Suite
"""

import bpy

import procedural_compute.core.properties as properties
import procedural_compute.core.operators as operators
import procedural_compute.core.menus as menus


def menu_add_north(self, context):
    self.layout.operator(
        operators.mesh.addNorthMarker.bl_idname,
        text="North Marker",
        icon='MESH_CONE'
    )


def register():
    bpy.types.VIEW3D_MT_mesh_add.append(menu_add_north)
    #------------------
    bpy.utils.register_class(menus.scene.SCENE_PT_bm)
    bpy.utils.register_class(menus.object.OBJECT_PT_bm)
    bpy.utils.register_class(menus.material.MATERIAL_PT_bm)
    return


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_add_north)
    #------------------
    bpy.utils.unregister_class(menus.scene.SCENE_PT_bm)
    bpy.utils.unregister_class(menus.object.OBJECT_PT_bm)
    bpy.utils.unregister_class(menus.material.MATERIAL_PT_bm)
    return
