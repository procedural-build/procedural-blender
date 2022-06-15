###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural Compute
# License : procedural compute license
# Version : 1.2
# Web     : compute.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples

from .site import SCENE_PROPS_COMPUTE_CORE_SITE
from .auth import SCENE_PROPS_COMPUTE_CORE_AUTH
from .task import SCENE_PROPS_COMPUTE_CORE_TASK

from procedural_compute.cfd.properties.scene import SCENE_PROPS_COMPUTE_CFD
from procedural_compute.energy.properties.scene import SCENE_PROPS_COMPUTE_ENERGY


class SCENE_PROPS_COMPUTE_CORE(bpy.types.PropertyGroup):

    auth: bpy.props.PointerProperty(type=SCENE_PROPS_COMPUTE_CORE_AUTH)
    site: bpy.props.PointerProperty(type=SCENE_PROPS_COMPUTE_CORE_SITE)
    task: bpy.props.PointerProperty(type=SCENE_PROPS_COMPUTE_CORE_TASK)

    CFD: bpy.props.PointerProperty(type=SCENE_PROPS_COMPUTE_CFD)
    Energy: bpy.props.PointerProperty(type=SCENE_PROPS_COMPUTE_ENERGY)

    mainMenu: bpy.props.EnumProperty(
        name="mainMenu",
        items=make_tuples(["SunPath", "CFD", "Radiance", "Energy"]),
        description="Procedural Compute menu categories"
    )


bpy.utils.register_class(SCENE_PROPS_COMPUTE_CORE)

##############
# Point from Scene to ODS variables
bpy.types.Scene.Compute = bpy.props.PointerProperty(type=SCENE_PROPS_COMPUTE_CORE)
