###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils.selectUtils import makeTuples


class BM_OBJ_RAD(bpy.types.PropertyGroup):
    radiance: bpy.props.BoolProperty(name="Radiance", description="Render Radiance Values", default=True)
    irrad: bpy.props.BoolProperty(name="Irradiance", description="Render Irradiance Values", default=True)

    def drawMenu(self, layout):
        # Radiance properties
        row = layout.row()
        row.prop(self, "radiance", text="Radiance?")
        row.prop(self, "irrad", text="Irradiance?")


bpy.utils.register_class(BM_OBJ_RAD)

#####################

bpy.types.Object.RAD = bpy.props.PointerProperty(type=BM_OBJ_RAD)
