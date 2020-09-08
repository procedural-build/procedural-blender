###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy

from procedural_compute.core.utils.blendmeUtils import drawCollectionTemplateList
from procedural_compute.core.utils.selectUtils import makeTuples

class iesLight(bpy.types.PropertyGroup):
    iesFile: bpy.props.StringProperty(name="iesFile", default="", maxlen=248, description="IES Filename", subtype='FILE_PATH')
    color: bpy.props.FloatVectorProperty(name="color", default=(1.0,1.0,1.0), min=0.0, max=1.0, subtype='COLOR')
    factor: bpy.props.FloatProperty(name="factor", default=1, min=0.0)

    def draw(self, layout):
        row = layout.row()
        row.prop(self, "name", text="Rename")
        layout.row().prop(self,"iesFile")
        layout.row().prop(self,"factor")
        layout.row().prop(self,"color")

bpy.utils.register_class(iesLight)


class BM_SCENE_RAD_LIGHT(bpy.types.PropertyGroup):

    iesLights: bpy.props.CollectionProperty(type=iesLight, name="iesLights", description="iesLights")
    active_iesLights_index: bpy.props.IntProperty(name="activeIesLight", description="Active iesLight Index")

    def drawButtons(self, layout):
        layout.row().operator("scene.ies2rad", text="ies2rad all lights")
        return None

    def draw(self, layout):
        drawCollectionTemplateList(layout, self, "iesLights")
        if len(self.iesLights) > 0:
            self.iesLights[self.active_iesLights_index].draw(layout)
        return None

    def getRadOptions(self):
        return bpy.context.scene.procedural_compute.rad.Frame.getRadOptions()

bpy.utils.register_class(BM_SCENE_RAD_LIGHT)
