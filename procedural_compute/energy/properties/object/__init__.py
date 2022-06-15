###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples
from procedural_compute.core.utils.collections import drawCollectionTemplateList

import json


class OBJECT_PROPS_COMPUTE_ENERGY(bpy.types.PropertyGroup):

    wall_type: bpy.props.StringProperty(name="Wall Type", default='wall', description="Wall Type")

    def drawMenu(self, layout):

        L = layout.box()
        L.row().label(text="Energy model properties")
        L.row().prop(self, "wall_type")

        #L.row().operator("scene.cfdoperators", text="Copy to Selected").command = "copy_bcs"

        return None

bpy.utils.register_class(OBJECT_PROPS_COMPUTE_ENERGY)
