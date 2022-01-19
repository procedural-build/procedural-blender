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


class BM_SCENE_CFDSystem(bpy.types.PropertyGroup):

    # Server login and token properties
    host: bpy.props.StringProperty(name="Host", default='https://compute.procedural.build', description="Compute host server")
    username: bpy.props.StringProperty(name="Username", default='', description="Compute username")
    password: bpy.props.StringProperty(name="Password", default='', description="Compute password")
    access_token: bpy.props.StringProperty(name="Access Token", default='', description="Access Token")
    refresh_token: bpy.props.StringProperty(name="Refresh Token", default='', description="Refresh Token")
    expire_time: bpy.props.StringProperty(name="Expires in", default='', description="Token expires in seconds")

    # Project and task name
    project_name: bpy.props.StringProperty(name="Project Name", default='', description="Project name")
    project_number: bpy.props.StringProperty(name="Project Number", default='', description="Project number (optional)")
    project_id: bpy.props.StringProperty(name="Project ID", default='', description="Project ID")
    project_data: bpy.props.StringProperty(name="Project data", default='', description="Project data")
    task_name: bpy.props.StringProperty(name="Task Name", default='', description="Task name")
    task_id: bpy.props.StringProperty(name="Task ID", default='', description="Task ID")
    task_data: bpy.props.StringProperty(name="Task data", default='', description="Task data")

    # Legacy system settings from ODS Studio
    runMPI: bpy.props.BoolProperty(name="runMPI", description="Do MPIRun", default=False)
    items_list = make_tuples(["simple", "hierarchical"])
    decompMethod: bpy.props.EnumProperty(name="decompMethod", items=items_list, description="Decomposition Method", default="hierarchical")
    numSubdomains: bpy.props.IntProperty(name="SubDomains", min=1, description="Number of SubDomains for Parallel Processing")
    decompN: bpy.props.IntVectorProperty(name="Nxyz", description="Splits in XYZ", default=(1, 1, 1), min=1)
    decompDelta: bpy.props.FloatProperty(name="Delta", step=1, precision=3, default=0.001, description="delta value for MPI decomposition")
    decompOrder: bpy.props.StringProperty(name="Order", default='xyz', description="Order of decomposition")

    caseDir: bpy.props.StringProperty(name="caseDir", default="//foam", maxlen=128, description="Case Directory", subtype='FILE_PATH')
    machines: bpy.props.StringProperty(name="Machines", default="localhost", description="Machines for MPIrun (comma separated)")
    if 'Windows' in bpy.app.build_platform.decode():
        homedir: bpy.props.StringProperty(name="OFHomeDir", default="C:/OpenFOAM", maxlen=128, description="OpenFOAM Home Directory")
        mpiOptions: bpy.props.StringProperty(name="mpiOptions", default="-genvlist Path,WM_PROJECT_DIR,MPI_BUFFER_SIZE", description="Added options for mpi")
    else:
        homedir: bpy.props.StringProperty(name="OFHomeDir", default="/opt/openfoam211", maxlen=128, description="OpenFOAM Home Directory")
        mpiOptions: bpy.props.StringProperty(name="mpiOptions", default="", description="Added options for mpi")

    def drawMenu(self, layout):
        sc = bpy.context.scene

        L = layout.box()

        L.row().label(text="Authentication")

        L.row().prop(self, "host")
        L.row().prop(self, "username")
        L.row().prop(self, "password")

        split = L.split()
        col = split.column()
        col.operator("scene.compute_cfdoperators", text="Login").command = "login"
        col = split.column()
        col.operator("scene.compute_cfdoperators", text="Refresh").command = "refresh"

        row = L.row()
        row.prop(self, "access_token", text="token")
        row.enabled = False
        row = L.row()
        row.prop(self, "expire_time", text="expires in (s)")
        row.enabled = False

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

        L.row().operator("scene.compute_cfdoperators", text="Get or Create").command = "get_or_create_project_and_task"

        L.row().prop(self, "decompN")


bpy.utils.register_class(BM_SCENE_CFDSystem)
