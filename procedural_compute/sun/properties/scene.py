###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy


def recalcsunpath(self, context):
    bpy.context.scene.ODS_SUN.sunpath.recalc = True
    return None


class BM_SCENE_SUNPATH(bpy.types.PropertyGroup):
    draw: bpy.props.BoolProperty(default=False)
    recalc: bpy.props.BoolProperty(default=True)
    flat: bpy.props.BoolProperty(default=False, update=recalcsunpath)
    equi: bpy.props.BoolProperty(default=False, update=recalcsunpath)
    xray: bpy.props.BoolProperty(default=False)
    time: bpy.props.BoolProperty(default=True)
    path: bpy.props.BoolProperty(default=True)
    circles: bpy.props.BoolProperty(default=True)
    pos: bpy.props.FloatVectorProperty(default=(0.0,0.0,0.0), update=recalcsunpath)
bpy.utils.register_class(BM_SCENE_SUNPATH)

class BM_SCENE_SUN(bpy.types.PropertyGroup):
    sunpath: bpy.props.PointerProperty(type=BM_SCENE_SUNPATH)

    solarDT: bpy.props.IntProperty(name="TimeStepsPerHour",
                                    min=1, max=60,
                                    default=4,description="Timesteps Per Hour")

    arcRadius: bpy.props.FloatProperty(name="arcRadius",
                                    min=0.0, default=10.0, description="Radius of Sun Arc", update=recalcsunpath)

    day: bpy.props.IntProperty(name="Day",
                                    min=1, max=31,
                                    description="Day for Sun Position")

    month: bpy.props.IntProperty(name="Month",
                                    min=1, max=12,
                                    description="Month for Sun Position")

    hour: bpy.props.IntProperty(name="Hour",
                                    min=0, max=24,
                                    description="Hour for Sun Position")

    minute: bpy.props.IntProperty(name="Minute",
                                    min=-1, max=60,
                                    description="Minute for Sun Position")
bpy.utils.register_class(BM_SCENE_SUN)

#############################

#from procedural_compute.core.properties.site import BM_SCENE_SITE
#bpy.types.Scene.Site: bpy.props.PointerProperty(type=BM_SCENE_SITE)

##############
# Point from Scene to ODS variables
bpy.types.Scene.ODS_SUN = bpy.props.PointerProperty(type=BM_SCENE_SUN)
