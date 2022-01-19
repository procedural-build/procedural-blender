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


class DATA_PT_light_bm(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "ODS Studio Light Properties"

    # Only draw the panel if the object type is a lamp
    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.lamp

    def draw(self, context):
        layout = self.layout
        sc = context.scene
        ob = context.object

        # Main Menu Headings
        if mainmenu_loaded():
            layout.row().prop(sc.Compute, "mainMenu", expand=True)

        # Skip this menu if the mainMenu is not pointing to Radiance
        if sc.Compute.mainMenu != "Radiance":
            return

        layout.row().prop_search(ob.RAD,"iesname",sc.RAD.Light,"iesLights", text="IES Light Type")
        return


bpy.utils.register_class(DATA_PT_light_bm)
