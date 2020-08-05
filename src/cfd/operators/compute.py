###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ODS-Engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################


import bpy
import os
import shutil
import glob
import json
import io

from procedural_compute.cfd.utils import foamCaseFiles, asciiSTLExport, mesh, foamUtils
from procedural_compute.core.utils import subprocesses, fileUtils, threads
from procedural_compute.core.utils.subprocesses import waitSTDOUT
import procedural_compute.cfd.solvers

from procedural_compute.core.utils.compute.auth import USER, User
from procedural_compute.core.utils.compute.view import GenericViewSet


class SCENE_OT_cfdOperators(bpy.types.Operator):
    bl_label = "Compute CFD Operations"
    bl_idname = "scene.compute_cfdoperators"
    bl_description = "Compute CFD Operations"

    command: bpy.props.StringProperty(name="Command", description="parse String", default="")

    def execute(self, context):
        if hasattr(self, self.command):
            c = getattr(self, self.command)
            c()
        else:
            print(self.command + ": Attribute not found!")
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

    def login(self):
        """ """
        system_settings = bpy.context.scene.ODS_CFD.system
        USER[0] = User(
            system_settings.username,
            system_settings.password,
            host = system_settings.host
        )
        print("GETTING USER TOKEN")
        USER[0].get_token()
        system_settings.access_token = USER[0].token
        system_settings.expire_time = "%.02f"%(USER[0].token_exp_time)

    def refresh(self):
        """ """
        system_settings = bpy.context.scene.ODS_CFD.system
        print(f"REFRESHING USER TOKEN: {USER[0].token}")
        USER[0].refresh_token()
        system_settings.access_token = USER[0].token
        system_settings.expire_time = "%.02f"%(USER[0].token_exp_time)

    def get_or_create_project_and_task(self):
        system_settings = bpy.context.scene.ODS_CFD.system
        project_name = system_settings.project_name.strip()
        project_number = system_settings.project_number
        task_name = system_settings.task_name.strip()

        # Get or create the project
        project = GenericViewSet('/api/project/').get_or_create(
            { 'name': project_name },
            create_params = { 'number': project_number or None },
            create=True
        )
        if project:
            system_settings.project_name = project.get('name')
            system_settings.project_number = project.get('number') or ""
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

    def upload_geometry(self):
        system_settings = bpy.context.scene.ODS_CFD.system
        task_id = system_settings.task_id

        geometry_objects = [obj for obj in bpy.context.visible_objects if not obj.ODS_CFD.mesh.makeRefinementRegion]
        geometry = io.StringIO()
        asciiSTLExport.writeObjectsToFile(geometry, objects=geometry_objects)
        geometry.seek(0)
        print("Cast geometry to STL format")

        response = GenericViewSet(
            f'/api/task/{task_id}/file/foam/constant/triSurface/cfdGeom.stl/'
        ).update(
            None,
            geometry.read().encode('utf8'),
            raw=True
        )

        self.upload_refinement_regions()

        return response

    def upload_refinement_regions(self):
        system_settings = bpy.context.scene.ODS_CFD.system
        task_id = system_settings.task_id

        print("Writing refinement regions")
        refinement_objects = [obj for obj in bpy.context.visible_objects if obj.ODS_CFD.mesh.makeRefinementRegion]
        for obj in refinement_objects:
            name = foamUtils.formatObjectName(obj.name)
            print(f" - Writing refinement region: {name}")
            geometry = io.StringIO()
            asciiSTLExport.writeObjectsToFile(geometry, objects = [obj])
            geometry.seek(0)
            print(" -- Cast geometry to STL format")
            response = GenericViewSet(
                f'/api/task/{task_id}/file/foam/constant/triSurface/{name}.stl/'
            ).update(
                None,
                geometry.read().encode('utf8'),
                raw=True
            )

    def get_or_create_empty_task(self, project_id, name, parent_task_id, dependent_on=None):
        query_params = {
            'name': name,
            'parent': parent_task_id,
        }
        if dependent_on is not None:
            query_params.update({'dependent_on': dependent_on})

        action_task = GenericViewSet(
            f'/api/project/{project_id}/task/'
        ).get_or_create(
            query_params,
            {
                'config': {
                    'task_type': 'empty'
                }
            },
            create = True
        )
        return action_task

    def write_mesh_files(self):
        """ Upload the geometry and dispatch the task in one operation
        """
        system_settings = bpy.context.scene.ODS_CFD.system
        mesh_properties = bpy.context.scene.ODS_CFD.mesh
        solver_properties = bpy.context.scene.ODS_CFD.solver
        project_id = system_settings.project_id
        task_id = system_settings.task_id

        # Get or create an empty setup task
        setup_task = self.get_or_create_empty_task(
            project_id, 'setup', task_id
        )

        # Write the mesh files
        setup_task = GenericViewSet(
            f'/api/project/{project_id}/task/'
        ).update(
            setup_task['uid'],
        {
            'name': 'setup',
            'status': 'pending',
            'config': {
                'task_type': 'magpy',
                'cmd': 'cfd.io.tasks.write_mesh',
                'base_mesh': mesh_properties.domain_json(),
                'snappyhex_mesh': mesh_properties.snappy_json()
            }
        })

        return setup_task

    def write_solver_files(self):
        system_settings = bpy.context.scene.ODS_CFD.system
        solver_properties = bpy.context.scene.ODS_CFD.solver
        project_id = system_settings.project_id
        task_id = system_settings.task_id

        # Get or create an empty setup task
        setup_task = self.get_or_create_empty_task(
            project_id, 'setup', task_id
        )

        #print("SOLVER PROPERTIES: %s"%(solver_properties.to_json()))

        # the action to create the CFD files
        setup_task = GenericViewSet(
            f'/api/project/{project_id}/task/'
        ).update(
            setup_task['uid'],
            {
                'name': 'setup',
                'status': 'pending',
                'config': {
                    'task_type': 'magpy',
                    'cmd': 'cfd.io.tasks.write_solution',
                    'solution': solver_properties.to_json()
                }
            }
        )

        return setup_task


    def basic_mesh(self):
        system_settings = bpy.context.scene.ODS_CFD.system
        project_id = system_settings.project_id
        task_id = system_settings.task_id

        # Get or create an empty setup task
        setup_task = self.get_or_create_empty_task(
            project_id, 'setup', task_id
        )

        # Get or create the mesh task
        mesh_task = self.get_or_create_empty_task(
            project_id, 'mesh', task_id, dependent_on=setup_task['uid']
        )

        # Get or create the mesh task
        mesh_task = GenericViewSet(
            f'/api/project/{project_id}/task/'
        ).update(
            mesh_task['uid'],
            {
                'name': 'mesh',
                'status': 'pending',
                'config': {
                    'task_type': 'cfd',
                    'cmd': 'pipeline',
                    'commands': [
                        'blockMesh',
                        "snappyHexMesh -overwrite",
                        "reconstructParMesh -constant -mergeTol 1e-6",
                        "!checkMesh -writeSets vtk"
                    ]
                }
            }
        )

        return mesh_task

    def run_solver(self):
        system_settings = bpy.context.scene.ODS_CFD.system
        solver_properties = bpy.context.scene.ODS_CFD.solver
        control_properties = bpy.context.scene.ODS_CFD.control
        project_id = system_settings.project_id
        task_id = system_settings.task_id

        # Get or create an empty setup task
        solver_task = self.get_or_create_empty_task(
            project_id, 'solution', task_id
        )

        # Dispatch to the mesh task
        solver_task = GenericViewSet(
            f'/api/project/{project_id}/task/'
        ).update(
            mesh_task['uid'],
            {
                'name': 'mesh',
                'status': 'pending',
                'config': {
                    'task_type': 'cfd',
                    'cmd': 'pipeline',
                    'commands': [
                        solver_properties.name,
                        "reconstructPar -skipZero"
                    ],
                    'cpus': [i for i in system_settings.decompN],
                    'iterations': control_properties.endTime
                }
            }
        )

        return solver_task



bpy.utils.register_class(SCENE_OT_cfdOperators)
