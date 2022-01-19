###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples


class SCENE_PT_COMPUTE_CORE_TASK(bpy.types.PropertyGroup):
    # Project and task get or create
    project_name: bpy.props.StringProperty(name="Project Name", default='', description="Project name")
    project_number: bpy.props.StringProperty(name="Project Number", default='', description="Project number (optional)")
    project_id: bpy.props.StringProperty(name="Project ID", default='', description="Project ID")
    project_data: bpy.props.StringProperty(name="Project data", default='', description="Project data")
    task_name: bpy.props.StringProperty(name="Task Name", default='', description="Task name")
    task_id: bpy.props.StringProperty(name="Task ID", default='', description="Task ID")
    task_data: bpy.props.StringProperty(name="Task data", default='', description="Task data")

    def draw_menu(self, layout):
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

        L.row().operator("scene.compute_operators_core", text="Get or Create").command = "get_or_create_project_and_task"


class SCENE_PT_COMPUTE_CORE_AUTH(bpy.types.PropertyGroup):
    # Server login and token properties
    host: bpy.props.StringProperty(name="Host", default='https://compute.procedural.build', description="Compute host server")
    username: bpy.props.StringProperty(name="Username", default='', description="Compute username")
    password: bpy.props.StringProperty(name="Password", default='', description="Compute password")
    access_token: bpy.props.StringProperty(name="Access Token", default='', description="Access Token")
    refresh_token: bpy.props.StringProperty(name="Refresh Token", default='', description="Refresh Token")
    expire_time: bpy.props.StringProperty(name="Expires in", default='', description="Token expires in seconds")


    def draw_menu(self, layout):
        sc = bpy.context.scene

        L = layout.box()

        L.row().label(text="Authentication")

        L.row().prop(self, "host")
        L.row().prop(self, "username")
        L.row().prop(self, "password")

        split = L.split()
        col = split.column()
        col.operator("scene.compute_operators_core", text="Login").command = "login"
        col = split.column()
        col.operator("scene.compute_operators_core", text="Refresh").command = "refresh"

        row = L.row()
        row.prop(self, "access_token", text="token")
        row.enabled = False
        row = L.row()
        row.prop(self, "expire_time", text="expires in (s)")
        row.enabled = False

bpy.utils.register_class(SCENE_PT_COMPUTE_CORE_AUTH)

##############
# Point from Scene to ODS variables
#bpy.types.Scene.COMPUTE_AUTH = bpy.props.PointerProperty(type=COMPUTE_CORE_AUTH)