###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy
from procedural_compute.core.utils import make_tuples


class SCENE_PROPS_COMPUTE_CFDSolver_LES(bpy.types.PropertyGroup):

    items_list = make_tuples(["Smagorinsky", "oneEqEddy", "SpalartAllmaras"])
    model: bpy.props.EnumProperty(name="lesModel", items=items_list, description="LES Turbulence Model", default="oneEqEddy")

    def drawMenu(self, layout):
        layout.row().prop(self, "model")
        return None


bpy.utils.register_class(SCENE_PROPS_COMPUTE_CFDSolver_LES)
##############


class SCENE_PROPS_COMPUTE_CFDSolver_RAS(bpy.types.PropertyGroup):

    items_list = make_tuples(["kEpsilon", "kOmega", "kOmegaSST"])
    model: bpy.props.EnumProperty(name="rasModel", items=items_list, description="RAS Turbulence Model", default="kEpsilon")

    def drawMenu(self, layout):
        layout.row().prop(self, "model")


bpy.utils.register_class(SCENE_PROPS_COMPUTE_CFDSolver_RAS)
