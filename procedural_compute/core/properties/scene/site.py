###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples


def recalcsunpath(self, context):
    if hasattr(bpy.context.scene, 'ODS_SUN'):
        bpy.context.scene.ODS_SUN.sunpath.recalc = True
    return None



# Import properties from submodules
class SCENE_PROPS_COMPUTE_CORE_SITE(bpy.types.PropertyGroup):

    terrain: bpy.props.EnumProperty(
        name="Terrain",
        items=make_tuples(["Suburbs", "Country", "City", "Ocean", "Urban"]),
        description="Set terrain type",
        default="Country"
    )

    buildingName: bpy.props.StringProperty(name="Name", default="Undefined", maxlen=128, description="Building Name")
    northAxis: bpy.props.FloatProperty(name="North", description="True north axis clockwise relative to 0deg=Y+", subtype="ANGLE", update=recalcsunpath)
    location: bpy.props.StringProperty(name="Location", default="Undefined", maxlen=32, description="Site Location Name")
    latitude: bpy.props.FloatProperty(name="Latitude", step=1, precision=5, description="Site Latitude", default=-31.95224, min=-90.0, max=90.0, update=recalcsunpath)
    longitude: bpy.props.FloatProperty(name="Longitude", step=1, precision=5, description="Site Longitude", default=115.8614, min=-180.0, max=180.0, update=recalcsunpath)
    timezone: bpy.props.FloatProperty(name="TimeZone", step=1, precision=2, description="Time Zone", default=8.0, min=-12.0, max=12.0, update=recalcsunpath)
    elevation: bpy.props.FloatProperty(name="Elevation", step=1, precision=2, description="Site Elevation")

    def draw_menu(self, layout):
        sc = context.scene
        # General site settings
        layout.row().prop(self, "buildingName")
        layout.row().prop(self, "location")

        split = layout.split()
        col = split.column()
        col.prop(self, "latitude")
        col.prop(self, "longitude")
        col.prop(self, "northAxis")
        col = split.column()
        col.prop(self, "timezone")
        col.prop(self, "elevation")
        col.prop(self, "terrain", expand=False)
        return

bpy.utils.register_class(SCENE_PROPS_COMPUTE_CORE_SITE)

##############
# Point from Scene to ODS variables
#bpy.types.Scene.Site = bpy.props.PointerProperty(type=COMPUTE_CORE_SCENE_SITE)
