###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

from procedural_compute.core.utils import make_tuples
from procedural_compute.rad.utils.radUtils import formatName


class BM_MAT_RAD_METAL(bpy.types.PropertyGroup):

    items_list = make_tuples(["VeryRough","Rough","MediumRough","MediumSmooth","Smooth","VerySmooth"])
    roughness: bpy.props.EnumProperty(
        name="Roughness",items=items_list,
        description="Influences only External Convection Coefficients",
        default="MediumRough")
    specular: bpy.props.FloatProperty(
        name="Specularity",
        description="Specularity (>0.1 is usually not realistic for Opaque, >0.9 typical for metal)",
        default=0.0, min=0.0, max=1.0, precision=4)

    def drawMenu(self, layout):
        layout.row().prop(self, "roughness")
        layout.row().prop(self, "specular")

    def getMatRGB(self):
        m = self.id_data
        (r,g,b,a) = m.diffuse_color
        return (r,g,b)

    def roughValue(self):
        roughDescriptions = ["VeryRough","Rough","MediumRough","MediumSmooth","Smooth","VerySmooth"]
        roughValues = [0.5, 0.35, 0.2, 0.14, 0.07, 0.0]
        return roughValues[roughDescriptions.index(self.roughness)]

    def textRAD(self):
        # Get the roughness and rgb values
        (r,g,b) = self.getMatRGB()
        text = "\n## material conversion from blender \"diffuse_color\" property"
        text += "\nvoid metal %s"%(formatName(self.id_data.name))
        text += "\n0\n0\n5"
        text += "  %.4f %.4f %.4f %.3f %.3f\n"%(r,g,b,self.specular,self.roughValue())
        return text
bpy.utils.register_class(BM_MAT_RAD_METAL)
