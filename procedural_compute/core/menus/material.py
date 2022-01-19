###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils.mainmenu import mainmenu_loaded

###################
# MATERIALS MENU
###################


class MATERIAL_PT_COMPUTE(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_label = "Procedural Compute Material Properties"

    def draw(self, context):
        layout = self.layout
        sc = context.scene
        # Main Menu Headings
        if mainmenu_loaded():
            layout.row().prop(sc.Compute, "mainMenu", expand=True)

        return
