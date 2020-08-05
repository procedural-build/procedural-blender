###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ods-engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################


import bpy

from procedural_compute.core.properties import BM_SCENE_ODS


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
        if len(BM_SCENE_ODS.__annotations__['mainMenu'][1]['items']) > 0:
            layout.row().prop(sc.ODS, "mainMenu", expand=True)

        return
