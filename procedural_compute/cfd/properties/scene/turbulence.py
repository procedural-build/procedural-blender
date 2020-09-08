###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy
from procedural_compute.core.utils.selectUtils import makeTuples


class BM_SCENE_CFDSolver_LES(bpy.types.PropertyGroup):

    items_list = makeTuples(["Smagorinsky", "oneEqEddy", "SpalartAllmaras"])
    model: bpy.props.EnumProperty(name="lesModel", items=items_list, description="LES Turbulence Model", default="oneEqEddy")

    def drawMenu(self, layout):
        layout.row().prop(self, "model")
        return None


bpy.utils.register_class(BM_SCENE_CFDSolver_LES)
##############


class BM_SCENE_CFDSolver_RAS(bpy.types.PropertyGroup):

    items_list = makeTuples(["kEpsilon", "kOmega", "kOmegaSST"])
    model: bpy.props.EnumProperty(name="rasModel", items=items_list, description="RAS Turbulence Model", default="kEpsilon")

    def drawMenu(self, layout):
        layout.row().prop(self, "model")


bpy.utils.register_class(BM_SCENE_CFDSolver_RAS)
