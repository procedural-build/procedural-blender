###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples


class imageprops(bpy.types.PropertyGroup):
    ndivs: bpy.props.IntProperty(name="n", description="Number of contours(=legend values)", default=8)
    decades: bpy.props.IntProperty(name="log", description="Log scaling factor", default=1)
    mult: bpy.props.FloatProperty(name="m", description="Multiplication factor", default=179)
    scale: bpy.props.FloatProperty(name="s", description="Scale factor (0=auto)", default=0)
    label: bpy.props.StringProperty(name="label", description="Label", maxlen=10, default="lux")
    legwidth: bpy.props.IntProperty(name="lw", description="Legend Width", default=100)
    legheight: bpy.props.IntProperty(name="lh", description="Legend Height", default=200)
    exposure: bpy.props.IntProperty(name="exposure", default=-4, description="Output exposure")
    overlaypic: bpy.props.StringProperty(name="picture", description="Overlay Picture", maxlen=248, default="", subtype='FILE_PATH')
    output: bpy.props.StringProperty(name="output", description="Output", maxlen=248, default="out.hdr", subtype='FILE_PATH')
    items_list = make_tuples(["None","Lines","Bands"])
    contours: bpy.props.EnumProperty(name="contours", items=items_list, default="None")
    limit: bpy.props.FloatProperty(name="lim", description="Threshold limit value", default=500)

    def draw(self, layout):
        row = layout.row()
        row.prop(self, "ndivs")
        row.prop(self, "decades")

        row = layout.row()
        row.prop(self, "legwidth")
        row.prop(self, "legheight")

        layout.row().prop(self, "contours")
        layout.row().prop(self, "overlaypic")

        row = layout.row()
        row.prop(self, "mult")
        row.operator("image.falsecolor", text="getDF").command="getDFMult"

        layout.row().prop(self, "scale")
        layout.row().prop(self, "label")

        layout.row().prop(self, "output")
        row = layout.row()
        row.operator("image.falsecolor", text="Make").command="falsecolor"
        row.operator("image.falsecolor", text="Reload").command="load"

    def drawBatch(self, layout):
        row = layout.row()
        row.prop(self, "mult")
        row.prop(self, "limit")
        row = layout.row()
        row.operator("scene.batchstats", text="Batch Stats")
        return

    def drawThreshold(self, layout):
        row = layout.row()
        row.prop(self, "mult")
        row.prop(self, "limit")
        layout.row().prop(self, "exposure")
        layout.row().prop(self, "output")
        layout.row().operator("image.falsecolor", text="Calculate").command="threshold"

    def getRadOptions(self):
        return ""


bpy.utils.register_class(imageprops)
