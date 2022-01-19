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
# OBJECT MENU
###################


class OBJECT_PT_bm(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "Procedural Compute Object Properties"

    def draw(self, context):
        layout = self.layout
        sc = context.scene
        # Main Menu Headings
        if mainmenu_loaded():
            layout.row().prop(sc.ODS, "mainMenu", expand=True)

        return
