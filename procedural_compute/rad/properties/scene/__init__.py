###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils.selectUtils import makeTuples
from procedural_compute.core.utils import threads

from .frame import BM_SCENE_RAD_FRAME
from .light import BM_SCENE_RAD_LIGHT
from .stencil import BM_SCENE_RAD_STENCIL
from .image import imageprops


def setQueue(self, context):
    threads.queues["rpict"].maxsize = self.nproc
    return None


class BM_SCENE_RAD(bpy.types.PropertyGroup):

    falsecolor: bpy.props.PointerProperty(type=imageprops)
    Frame: bpy.props.PointerProperty(type=BM_SCENE_RAD_FRAME)
    Light: bpy.props.PointerProperty(type=BM_SCENE_RAD_LIGHT)
    Stencil: bpy.props.PointerProperty(type=BM_SCENE_RAD_STENCIL)

    items_list = [
      ("Frame",     "Frame",    "Render Current Frame"),
      ("Light",     "Light",    "Set IES Lights"),
      ("Stencil",   "Stencil",  "Render Stencils")
    ]
    menu: bpy.props.EnumProperty(name="RADMenu", items=items_list, description="Radiance menu", default="Frame")

    nproc: bpy.props.IntProperty(name="nproc", min=1, default=4, description="Number of local processors", update=setQueue)
    caseDir: bpy.props.StringProperty(name="caseDir", default="//rad", maxlen=128, description="Case Directory", subtype='FILE_PATH')

    items_list = [("-s", "Sunny sky without sun",           "The sky distribution will correspond to a standard CIE clear day"),
                  ("+s", "Sunny sky with sun",              "In addition to the sky distribution function, a source description of the sun is generated."),
                  ("-c", "Cloudy sky",                      "The sky distribution will correspond to a standard CIE overcast day"),
                  ("-i", "Intermediate sky without sun",    "The sky will correspond to a standard CIE intermediate day"),
                  ("+i", "Intermediate sky with sun",       "In addition to the sky distribu tion, a (somewhat subdued) sun is generated"),
                  ("-u", "Uniform cloudy sky",              "The sky distribution will be  completely uniform")]
    skytype: bpy.props.EnumProperty(name="skytype", items=items_list, description="Radiance Sky Types", default="-c")

    def draw(self, layout):
        layout.row().prop(self, "menu", expand=True)
        split = layout.split(factor=0.25)
        split.column().prop(self, "nproc", text="CPUs")
        split.column().prop(self, "caseDir", text="Case Dir")
        getattr(self, self.menu).drawButtons(layout)
        # Draw Sky-type options
        L = layout.box()
        L.row().prop(self, "skytype", text="Sky", expand=False)
        # Draw the sub-menu
        getattr(self, self.menu).draw(layout)
        return None

    def getRadOptions(self):
        return getattr(self, self.menu).getRadOptions()

bpy.utils.register_class(BM_SCENE_RAD)

##############
# Point from Scene to ODS variables
bpy.types.Scene.RAD = bpy.props.PointerProperty(type=BM_SCENE_RAD)
