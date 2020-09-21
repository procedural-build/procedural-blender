###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

from procedural_compute.rad.utils.radUtils import formatName

##############

class BM_MAT_RAD_MIRROR(bpy.types.PropertyGroup):

    reflectance: bpy.props.FloatProperty(
        name="reflectance",
        description="Visible Reflectance",
        default=0.98, min=0.0, max=1.0, precision=4)

    def drawMenu(self, layout):
        layout.row().prop(self, "reflectance")

    def getMatRGB(self):
        m = self.id_data
        (r,g,b,a) = m.diffuse_color
        return (r,g,b)

    def rgbFactors(self):
        (r,g,b) = self.getMatRGB()
        tn = self.reflectance
        v = []
        for vv in [r,g,b]:
            vc = (vv/sum([r,g,b]))*(tn*3)
            if vc > 1.0:
                vc = 1.0
            v.append(vc)
        return v

    def textRAD(self):
        v = self.rgbFactors()
        text = "\n## material conversion from blender \"diffuse_color\" property"
        text += "\nvoid mirror %s"%(formatName(self.id_data.name))
        text += "\n0\n0\n3"
        text += "  %.4f %.4f %.4f\n" %(v[0],v[1],v[2])
        return text

bpy.utils.register_class(BM_MAT_RAD_MIRROR)
