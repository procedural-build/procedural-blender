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
class SCENE_PT_bm(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "Procedural Compute Studio Scene Settings"

    def drawHeader(self, context):
        layout = self.layout
        sc = context.scene
        # General site settings
        layout.row().prop(sc.Site, "buildingName")
        layout.row().prop(sc.Site, "location")

        b = sc.Site
        split = layout.split()
        col = split.column()
        col.prop(b, "latitude")
        col.prop(b, "longitude")
        col.prop(b, "northAxis")
        col = split.column()
        col.prop(b, "timezone")
        col.prop(b, "elevation")
        col.prop(b, "terrain", expand=False)
        return

    def draw(self, context):
        layout = self.layout
        sc = context.scene
        # Draw the header
        self.drawHeader(context)
        # Main Menu Headings
        if mainmenu_loaded():
            layout.row().prop(sc.ODS, "mainMenu", expand=True)

        return
