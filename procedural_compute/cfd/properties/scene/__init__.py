###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples

from procedural_compute.cfd.properties.scene.mesh import BM_SCENE_CFDMesh
from procedural_compute.cfd.properties.scene.control import BM_SCENE_CFDControl
from procedural_compute.cfd.properties.scene.solver import BM_SCENE_CFDSolver
from procedural_compute.cfd.properties.scene.system import BM_SCENE_CFDSystem
from procedural_compute.cfd.properties.scene.postproc import BM_SCENE_CFDPostProc

class BM_SCENE_CFD(bpy.types.PropertyGroup):

    mesh: bpy.props.PointerProperty(type=BM_SCENE_CFDMesh)
    control: bpy.props.PointerProperty(type=BM_SCENE_CFDControl)
    solver: bpy.props.PointerProperty(type=BM_SCENE_CFDSolver)
    system: bpy.props.PointerProperty(type=BM_SCENE_CFDSystem)
    postproc: bpy.props.PointerProperty(type=BM_SCENE_CFDPostProc)

    items_list = make_tuples(["System", "Solver", "Mesh", "Control", "PostProc"])
    menu: bpy.props.EnumProperty(name="CFDMenu", items=items_list, description="CFD menu categories", default="System")

    showCoeffs: bpy.props.BoolProperty(name="showCoeffs", description="Show advanced wall coefficients", default=False)

    def drawMenu(self, layout):
        layout.row().prop(self, "menu", expand=True)
        c = getattr(self, self.menu.lower())
        c.drawMenu(layout)
        return None


bpy.utils.register_class(BM_SCENE_CFD)

##############
# Point from Scene to ODS variables
bpy.types.Scene.ODS_CFD = bpy.props.PointerProperty(type=BM_SCENE_CFD)
