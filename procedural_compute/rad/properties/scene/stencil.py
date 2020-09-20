###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy


class BM_SCENE_RAD_STENCIL(bpy.types.PropertyGroup):

    res: bpy.props.IntProperty(name="res", min=1, default=400, description="Resolution along longest dimension")
    ambB: bpy.props.IntProperty(name="Bounces", min=0, default=2, description="Ambient Bounces")
    ambD: bpy.props.IntProperty(name="Divisions", min=0, default=256, description="Ambient Divisions")
    ambS: bpy.props.IntProperty(name="SuperSamples", min=0, default=128, description="Ambient super-samples")
    ambA: bpy.props.FloatProperty(name="Accuracy", min=0, max=0.5, precision=3, default=0.15, description="Ambient Accuracy")

    def drawButtons(self, layout):
        L = layout.box()
        split = L.split()
        split.column().operator("scene.radianceops", text="Write Case Files").command="writeRadianceFiles"
        split.column().operator("scene.radianceops", text="Generate Octree").command="genOctree"
        L.row().operator("scene.rtracestencils", text="Trace at Stencils")

    def draw(self, layout):
        L = layout.box()
        L.row().prop(self, "res", text="Resolution")

        split = L.split()
        col = split.column()
        col.prop(self, "ambA")
        col.prop(self, "ambB")
        col = split.column()
        col.prop(self, "ambS")
        col.prop(self, "ambD")

    def getRadOptions(self):
        return bpy.context.scene.procedural_compute.rad.Frame.getRadOptions()


bpy.utils.register_class(BM_SCENE_RAD_STENCIL)
