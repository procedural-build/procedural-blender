###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
import os
import json
import logging 

logger = logging.getLogger(__name__)

from procedural_compute.core.utils.secrets import secure_login
from procedural_compute.core.utils.compute.auth import USER, User
from procedural_compute.core.utils.compute.view import GenericViewSet


def get_system_properties():
    system_settings = bpy.context.scene.Compute.system
    project_id = system_settings.project_id
    task_id = system_settings.task_id
    return (project_id, task_id, control_properties, solver_properties, system_settings)


class SCENE_OT_COMPUTE_CORE(bpy.types.Operator):
    bl_label = "Compute CFD Operations"
    bl_idname = "scene.compute_operators_core"
    bl_description = "Compute CFD Operations"

    command: bpy.props.StringProperty(name="Command", description="parse String", default="")

    def execute(self, context):
        if hasattr(self, self.command):
            c = getattr(self, self.command)
            c()
        else:
            logger.info(self.command + ": Attribute not found!")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}

    def login(self):
        """ Login user with provided details OR credentials from environment variables 
        """
        secure_login()

    def refresh(self):
        """ """
        system_settings = bpy.context.scene.ODS_CFD.system
        logger.info(f"REFRESHING USER TOKEN: {USER[0].token}")
        USER[0].refresh_token()
        system_settings.access_token = USER[0].token
        system_settings.expire_time = "%.02f"%(USER[0].token_exp_time)

    def get_or_create_project_and_task(self):
        system_settings = bpy.context.scene.ODS_CFD.system
        project_name = system_settings.project_name.strip()
        project_number = system_settings.project_number
        task_name = system_settings.task_name.strip()

        # Get the list of projects
        if not project_number:
            project_list = GenericViewSet('/api/project/').list()
            project_number = len(project_list) or 1

        # Get or create the project
        project = GenericViewSet('/api/project/').get_or_create(
            { 'name': project_name },
            create_params = { 'number': project_number or None },
            create=True
        )
        if project:
            system_settings.project_name = project.get('name')
            system_settings.project_number = str(project.get('number')) or ""
            system_settings.project_id = project.get('uid')
            system_settings.project_data = json.dumps(project)

        # We won't get here unless the getting of project succeded
        task  = GenericViewSet(f"/api/project/{project['uid']}/task/").get_or_create(
            { 'name': task_name },
            create_params = {
                'config': {
                    'case_dir': 'foam',
                    'task_type': 'parent'
                }
            },
            create = True
        )
        if task:
            system_settings.task_name = task.get('name')
            system_settings.task_id = task.get('uid')
            system_settings.task_data = json.dumps(task)

        return {
            'project': project,
            'task': task
        }

    def get_or_create_task(self, project_id, name, parent_task_id, dependent_on=None, config=None):
        query_params = {
            'name': name,
            'parent': parent_task_id,
        }
        if dependent_on is not None:
            query_params.update({'dependent_on': dependent_on})

        if not config:
            config = {'task_type': 'empty'}

        action_task = GenericViewSet(
            f'/api/project/{project_id}/task/'
        ).get_or_create(
            query_params,
            {
                'config': config
            },
            create = True
        )
        return action_task



bpy.utils.register_class(SCENE_OT_COMPUTE_CORE)
