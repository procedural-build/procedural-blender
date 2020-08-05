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
# MATERIALS MENU
###################


class MATERIAL_PT_bm(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_label = "Procedural Compute Material Properties"

    def draw(self, context):
        layout = self.layout
        sc = context.scene
        # Main Menu Headings
        if len(BM_SCENE_ODS.__annotations__['mainMenu'][1]['items']) > 0:
            layout.row().prop(sc.ODS, "mainMenu", expand=True)

        return
