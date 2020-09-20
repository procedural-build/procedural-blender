###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy
from procedural_compute.core.utils.selectUtils import makeTuples


class BM_SCENE_RAD_FRAME(bpy.types.PropertyGroup):

    items_list = makeTuples(["low","medium","high"])
    quality: bpy.props.EnumProperty(name="quality", items=items_list, description="Radiance Output Quality", default="medium")

    items_list = makeTuples(["low","medium","high"])
    detail: bpy.props.EnumProperty(name="detail", items=items_list, description="Radiance Output Detail", default="medium")

    items_list = makeTuples(["low","medium","high"])
    variability: bpy.props.EnumProperty(name="variability", items=items_list, description="Radiance Output Variability", default="medium")

    items_list = makeTuples(["Interior","Exterior"])
    zoneType: bpy.props.EnumProperty(name="zoneType", items=items_list, description="Radiance zoneType", default="Interior")

    penumbras: bpy.props.BoolProperty(name="penumbras", description="Radiance Output Penumbras", default=True)
    indirect: bpy.props.IntProperty(name="indirect", min=1, default=2, description="Indirect")
    exposure: bpy.props.IntProperty(name="exposure", default=-4, description="Output exposure")
    zoneMin: bpy.props.FloatVectorProperty(name="zoneMin", description="Radiance Min Zone Size", subtype="XYZ", default=(0.0, 0.0, 0.0))
    zoneMax: bpy.props.FloatVectorProperty(name="zoneMax", description="Radiance Max Zone Size", subtype="XYZ", default=(0.0, 0.0, 0.0))
    imagesize: bpy.props.IntProperty(name="imagesize", min=1, default=768, description="Resolution along longest dimension")

    def drawButtons(self, layout):
        split = layout.split()
        split.column().operator("scene.radianceops", text="Write Case Files").command="writeRadianceFiles"
        split.column().operator("scene.radianceops", text="Render Frame").command="executeRifFile"

    def draw(self, layout):
        L = layout.box()
        L.row().label(text="Radiance Output Options:")

        split = L.split()
        split.column().prop(self, "imagesize")
        split.column().prop(self, "indirect")
        split.column().prop(self, "exposure")

        split = L.split()
        col = split.column()
        col.prop(self, "quality", expand=False)
        col.prop(self, "variability", expand=False)
        col = split.column()
        col.prop(self, "detail", expand=False)
        col.prop(self, "penumbras")

        L = layout.box()
        L.row().prop(self, "zoneType", expand=False)
        L.row().prop(self, "zoneMin", text="zoneMin")
        L.row().prop(self, "zoneMax", text="zoneMax")

    def getRadOptions(self):
        text =  "\nRESOLUTION=   %u\n"%(self.imagesize)
        text += "\nQUALITY=      %s\n"%(self.quality)
        text += "DETAIL=       %s\n"%(self.detail)
        text += "VARIABILITY=  %s\n"%(self.variability)
        text += "PENUMBRAS=    %s\n"%(str(self.penumbras))
        text += "INDIRECT=     %u\n"%(self.indirect)
        zmin = self.zoneMin
        zmax = self.zoneMax
        zsize = zmax - zmin
        if zsize.length > 0.01:
            text += "\nZONE=  %s %f %f %f %f %f %f\n"%(self.zoneType, zmin[0], zmax[0], zmin[1], zmax[1], zmin[2], zmax[2])
        if self.zoneType == "Exterior":
            text += "EXPOSURE=     %u\n"%(self.exposure)
        else:
            text += "EXPOSURE=     %u\n"%(self.exposure)
        text += "\nUP=           Z\n"
        text += "\nrender=     \n"
        return text


bpy.utils.register_class(BM_SCENE_RAD_FRAME)
