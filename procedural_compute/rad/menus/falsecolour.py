###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy


class falsecolorPanel(bpy.types.Panel):
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Falsecolor"

    def draw(self, context):
        bpy.context.scene.RAD.falsecolor.draw(self.layout)
        return None


bpy.utils.register_class(falsecolorPanel)
