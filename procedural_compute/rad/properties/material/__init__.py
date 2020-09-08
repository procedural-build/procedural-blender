###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

from procedural_compute.core.utils.selectUtils import makeTuples
from procedural_compute.rad.utils.radUtils import formatName

from procedural_compute.rad.properties.material.plastic import BM_MAT_RAD_PLASTIC
from procedural_compute.rad.properties.material.glass import BM_MAT_RAD_GLASS
from procedural_compute.rad.properties.material.metal import BM_MAT_RAD_METAL
from procedural_compute.rad.properties.material.mirror import BM_MAT_RAD_MIRROR
from procedural_compute.rad.properties.material.trans import BM_MAT_RAD_TRANS

class BM_MAT_RAD(bpy.types.PropertyGroup):

    items_list = makeTuples(["Plastic", "Glass", "Metal", "Mirror","Trans", "None"])
    type: bpy.props.EnumProperty(name="Type", items=items_list, description="Material Type", default="Plastic")

    Plastic: bpy.props.PointerProperty(type=BM_MAT_RAD_PLASTIC)
    Glass: bpy.props.PointerProperty(type=BM_MAT_RAD_GLASS)
    Metal: bpy.props.PointerProperty(type=BM_MAT_RAD_METAL)
    Mirror: bpy.props.PointerProperty(type=BM_MAT_RAD_MIRROR)
    Trans: bpy.props.PointerProperty(type=BM_MAT_RAD_TRANS)

    def drawMenu(self, layout):
        layout.row().prop(self, "type", text="Type", expand=False)
        if self.type == "None":
            return None
        t = getattr(self, self.type)
        t.drawMenu(layout)
        return None

    def textRAD(self):
        if self.type == "None":
            text=""
        else:
            t = getattr(self, self.type)
            text = t.textRAD()
        return text

bpy.utils.register_class(BM_MAT_RAD)

##############
# Point from Scene to ODS variables
bpy.types.Material.RAD: bpy.props.PointerProperty(type=BM_MAT_RAD)
