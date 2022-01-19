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
# SCENE MENU
###################
class SCENE_PT_COMPUTE(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Procedural Compute Scene Settings"

    def draw(self, context):
        layout = self.layout
        sc = context.scene
        
        # Authentication menu
        sc.Compute.auth.draw_menu(layout)

        # Site properties menu
        
        # Main Menu Headings
        if mainmenu_loaded():
            layout.row().prop(sc.Compute, "mainMenu", expand=True)

        return
