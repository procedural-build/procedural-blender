###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy
import procedural_compute.rad.properties.object

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
        if len(bpy.types.BM_SCENE_ODS.mainMenu[1]['items']) > 0:
            layout.row().prop(sc.ODS, "mainMenu", expand=True)
        if sc.ODS.mainMenu != "Radiance":
            return        

        # Draw the object property menu
        context.object.procedural_compute.rad.draw(layout)
        return
bpy.utils.register_class(DATA_PT_camera_bm)


