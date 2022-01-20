###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples

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


class OBJECT_PROPS_COMPUTE_CFD_MESH(bpy.types.PropertyGroup):
    meshMinLevel: bpy.props.IntProperty(name="min", min=0, default=0, description="meshMaxLevel", update=setMeshMinMax)
    meshMaxLevel: bpy.props.IntProperty(name="max", min=0, default=0, description="meshMaxLevel", update=setMeshMinMax)
    nSurfaceLayers: bpy.props.IntProperty(name="nSurfaceLayers", min=0, default=0, description="nSurfaceLayers")

    makeRefinementRegion: bpy.props.BoolProperty(name="refinementRegion", default=False, description="Make this object a Refinement Region")
    makeCellSet: bpy.props.BoolProperty(name="cellSet", default=False, description="Make this object a cellSet")
    items_list = make_tuples(["distance", "inside", "outside", "surface"])
    refinementMode: bpy.props.EnumProperty(name="mode", items=items_list, description="Preset", default="inside", update=setLevel)
    distanceLevels: bpy.props.StringProperty(name="levels", description="Levels at Distances: (distance level)", default="((1 4))")

    def drawMenu(self, layout):
        sc = bpy.context.scene
        L = layout.box()
        L.row().label(text="Mesh Levels:")
        split = L.split()


        split.column().prop(self, "meshMinLevel")
        split.column().prop(self, "meshMaxLevel")
        if sc.Compute.CFD.mesh.addLayers:
            split.column().prop(self, "nSurfaceLayers")

        # Make Refinement Region
        split.column().prop(self, "makeRefinementRegion")
        split.column().prop(self, "makeCellSet")

        if self.makeRefinementRegion or self.makeCellSet:
            L = layout.box()
            row = L.row()
            row.prop(self, "refinementMode")
            if self.makeRefinementRegion:
                row.prop(self, "distanceLevels")

        layout.row().operator("scene.cfdoperators", text="Copy to Selected").command = "copyMeshLevels"


bpy.utils.register_class(OBJECT_PROPS_COMPUTE_CFD_MESH)
