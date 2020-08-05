###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ODS-Engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################


import bpy
from procedural_compute.core.utils.selectUtils import makeTuples

###########


def setMeshMinMax(self, context):
    if self.meshMaxLevel < self.meshMinLevel:
        self.meshMaxLevel = self.meshMinLevel
    return None


def setLevel(self, context):
    if self.refinementMode == "distance":
        self.distanceLevels = "((1.0 5) (2.0 3))"
    elif self.refinementMode == "surface":
        self.distanceLevels = "((4 4))"
    else:
        self.distanceLevels = "((1 4))"


class BM_OBJ_CFD_MESH(bpy.types.PropertyGroup):
    meshMinLevel: bpy.props.IntProperty(name="min", min=0, default=0, description="meshMaxLevel", update=setMeshMinMax)
    meshMaxLevel: bpy.props.IntProperty(name="max", min=0, default=0, description="meshMaxLevel", update=setMeshMinMax)
    nSurfaceLayers: bpy.props.IntProperty(name="nSurfaceLayers", min=0, default=0, description="nSurfaceLayers")

    makeRefinementRegion: bpy.props.BoolProperty(name="makeRefinementRegion", default=False, description="Make this object a Refinement Region")
    items_list = makeTuples(["distance", "inside", "outside", "surface"])
    refinementMode: bpy.props.EnumProperty(name="refinementMode", items=items_list, description="Preset", default="inside", update=setLevel)
    distanceLevels: bpy.props.StringProperty(name="distanceLevels", description="Levels at Distances: (distance level)", default="((1 4))")

    def drawMenu(self, layout):
        sc = bpy.context.scene
        L = layout.box()
        L.row().label(text="Mesh Levels:")
        split = L.split()


        col = split.column()
        col.prop(self, "meshMinLevel")
        col = split.column()
        col.prop(self, "meshMaxLevel")
        if sc.ODS_CFD.mesh.addLayers:
            col = split.column()
            col.prop(self, "nSurfaceLayers")

        # Make Refinement Region
        col = split.column()
        col.prop(self, "makeRefinementRegion")

        if self.makeRefinementRegion:
            L = layout.box()
            L.row().prop(self, "refinementMode")
            L.row().prop(self, "distanceLevels")

        layout.row().operator("scene.cfdoperators", text="Copy to Selected").command = "copyMeshLevels"


bpy.utils.register_class(BM_OBJ_CFD_MESH)
