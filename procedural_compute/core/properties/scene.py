###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural Compute
# License : procedural compute license
# Version : 1.2
# Web     : compute.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples

from .site import SCENE_PT_COMPUTE_CORE_SITE
from .auth import SCENE_PT_COMPUTE_CORE_AUTH 


##############


class SCENE_PT_COMPUTE_CORE(bpy.types.PropertyGroup):

    auth: bpy.props.PointerProperty(type=SCENE_PT_COMPUTE_CORE_AUTH)
    site: bpy.props.PointerProperty(type=SCENE_PT_COMPUTE_CORE_SITE)

    mainMenu: bpy.props.EnumProperty(
        name="mainMenu",
        items=make_tuples(["SunPath", "CFD", "Radiance", "Energy"]),
        description="Procedural Compute menu categories"
    )


bpy.utils.register_class(SCENE_PT_COMPUTE_CORE)

##############
# Point from Scene to ODS variables
bpy.types.Scene.Compute = bpy.props.PointerProperty(type=SCENE_PT_COMPUTE_CORE)
