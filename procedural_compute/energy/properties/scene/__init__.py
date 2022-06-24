###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples

class SCENE_PROPS_COMPUTE_ENERGY(bpy.types.PropertyGroup):

    def drawMenu(self, layout):
        #layout.row().prop(self, "menu", expand=True)
        #c = getattr(self, self.menu.lower())
        #c.drawMenu(layout)

        L = layout.box()
        L.row().operator("scene.energyoperators", text="Model operator")

        return None


bpy.utils.register_class(SCENE_PROPS_COMPUTE_ENERGY)
