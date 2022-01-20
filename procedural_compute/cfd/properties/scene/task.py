###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples
from procedural_compute.core.utils.compute.auth import USER

class SCENE_PROPS_COMPUTE_CFD_Task(bpy.types.PropertyGroup):
    # Project and task name
    project_name: bpy.props.StringProperty(name="Project Name", default='', description="Project name")
    project_number: bpy.props.StringProperty(name="Project Number", default='', description="Project number (optional)")
    project_id: bpy.props.StringProperty(name="Project ID", default='', description="Project ID")
    project_data: bpy.props.StringProperty(name="Project data", default='', description="Project data")
    task_name: bpy.props.StringProperty(name="Task Name", default='', description="Task name")
    task_id: bpy.props.StringProperty(name="Task ID", default='', description="Task ID")
    task_data: bpy.props.StringProperty(name="Task data", default='', description="Task data")

    decompN: bpy.props.IntVectorProperty(name="Nxyz", description="Splits in XYZ", default=(1, 1, 1), min=1)

    @property
    def ids(self):
        return (self.project_id, self.task_id)

    def drawMenu(self, layout):
        sc = bpy.context.scene

        L = layout.box()
        L.row().label(text="Project/Task")

        L.row().prop(self, "project_name")
        row = L.row()
        row.prop(self, "project_id")
        row.enabled = False

        L.row().prop(self, "task_name")
        row = L.row()
        row.prop(self, "task_id")
        row.enabled = False

        L.row().operator("scene.compute_operators_cfd", text="Get or Create").command = "get_or_create_project_and_task"

        L.row().prop(self, "decompN")
        
bpy.utils.register_class(SCENE_PROPS_COMPUTE_CFD_Task)