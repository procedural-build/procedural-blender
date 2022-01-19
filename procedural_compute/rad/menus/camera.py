###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy
import procedural_compute.rad.properties.object
from procedural_compute.utils.mainmenu import mainmenu_loaded


class DATA_PT_camera_bm(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "ODS Studio Camera Properties"

    # Only draw the panel if the object type is a camera
    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.camera

    def draw(self, context):
        layout = self.layout
        sc = context.scene
        # Main Menu Headings
        if mainmenu_loaded():
            layout.row().prop(sc.Compute, "mainMenu", expand=True)
            
        if sc.Compute.mainMenu != "Radiance":
            return

        # Draw the object property menu
        context.object.RAD.draw(layout)
        return


bpy.utils.register_class(DATA_PT_camera_bm)
