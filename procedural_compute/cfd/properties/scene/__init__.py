###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples

from .mesh import SCENE_PROPS_COMPUTE_CFDMesh
from .control import SCENE_PROPS_COMPUTE_CFDControl
from .solver import SCENE_PROPS_COMPUTE_CFDSolver
from .system import SCENE_PROPS_COMPUTE_CFDSystem
from .task import SCENE_PROPS_COMPUTE_CFD_Task
from .postproc import SCENE_PROPS_COMPUTE_CFDPostProc


class SCENE_PROPS_COMPUTE_CFD(bpy.types.PropertyGroup):

    mesh: bpy.props.PointerProperty(type=SCENE_PROPS_COMPUTE_CFDMesh)
    control: bpy.props.PointerProperty(type=SCENE_PROPS_COMPUTE_CFDControl)
    solver: bpy.props.PointerProperty(type=SCENE_PROPS_COMPUTE_CFDSolver)
    system: bpy.props.PointerProperty(type=SCENE_PROPS_COMPUTE_CFDSystem)
    task: bpy.props.PointerProperty(type=SCENE_PROPS_COMPUTE_CFD_Task)
    postproc: bpy.props.PointerProperty(type=SCENE_PROPS_COMPUTE_CFDPostProc)

    items_list = make_tuples(["Task", "Solver", "Mesh", "Control", "PostProc"])
    menu: bpy.props.EnumProperty(name="CFDMenu", items=items_list, description="CFD menu categories", default="Task")

    showCoeffs: bpy.props.BoolProperty(name="showCoeffs", description="Show advanced wall coefficients", default=False)

    def drawMenu(self, layout):
        layout.row().prop(self, "menu", expand=True)
        c = getattr(self, self.menu.lower())
        c.drawMenu(layout)
        return None


bpy.utils.register_class(SCENE_PROPS_COMPUTE_CFD)
