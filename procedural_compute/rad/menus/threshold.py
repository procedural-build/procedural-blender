###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy

class thresholdPanel(bpy.types.Panel):
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Threshold"

    def draw(self, context):
        layout = self.layout
        bpy.context.scene.procedural_compute.rad.falsecolor.drawThreshold(layout)
        return
bpy.utils.register_class(thresholdPanel)
