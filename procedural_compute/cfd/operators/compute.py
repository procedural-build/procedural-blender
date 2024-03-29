###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
import os
import shutil
import glob
import json
import io
import re
import time

from procedural_compute.cfd.utils import foamCaseFiles, asciiSTLExport, mesh, foamUtils
from procedural_compute.core.utils import subprocesses, fileUtils, threads, to_json
from procedural_compute.core.utils.subprocesses import waitSTDOUT
from procedural_compute.core.utils.secrets import secure_login
import procedural_compute.cfd.solvers

from procedural_compute.core.utils.compute.auth import USER, User
from procedural_compute.core.utils.compute.view import GenericViewSet

from .utils import get_sets_from_selected, color_object

import logging
logger = logging.getLogger(__name__)


def get_system_properties():
    _settings = bpy.context.scene.Compute.CFD.task
    solver_properties = bpy.context.scene.Compute.CFD.solver
    control_properties = bpy.context.scene.Compute.CFD.control
    project_id = _settings.project_id
    task_id = _settings.task_id
    return (project_id, task_id, control_properties, solver_properties, _settings)


class SCENE_OT_cfdOperators(bpy.types.Operator):
    bl_label = "Compute CFD Operations"
    bl_idname = "scene.compute_operators_cfd"
    bl_description = "Compute CFD Operations"

    command: bpy.props.StringProperty(name="Command", description="parse String", default="")

    def execute(self, context):
        if hasattr(self, self.command):
            c = getattr(self, self.command)
            logger.info(f"\n\n###### EXECUTING CFD OPERATION: {self.command} ######\n")
            c()
        else:
            logger.info(f"{self.command}: Attribute not found!")
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

    def login(self):
        """ Login user with provided details OR credentials from environment variables 
        """
        secure_login()

    def refresh(self):
        """ """
        bpy.ops.scene.compute_operators_core(command="refresh")

    def get_or_create_project_and_task(self):
        _settings = bpy.context.scene.Compute.CFD.task
        project_name = _settings.project_name.strip()
        project_number = _settings.project_number
        task_name = _settings.task_name.strip()

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
            _settings.project_name = project.get('name')
            _settings.project_number = str(project.get('number')) or ""
            _settings.project_id = project.get('uid')
            _settings.project_data = json.dumps(project)

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
            _settings.task_name = task.get('name')
            _settings.task_id = task.get('uid')
            _settings.task_data = json.dumps(task)

        return {
            'project': project,
            'task': task
        }

    def upload_geometry(self):
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        geometry_objects = [obj for obj in bpy.context.visible_objects if not self._separate_stl(obj)]
        geometry = io.StringIO()
        asciiSTLExport.writeObjectsToFile(geometry, objects=geometry_objects)
        geometry.seek(0)
        logger.info("Cast geometry to STL format")

        response = GenericViewSet(
            f'/api/task/{task_id}/file/foam/constant/triSurface/cfdGeom.stl/'
        ).update(
            None,
            geometry.read().encode('utf8'),
            raw=True
        )

        self.upload_separate_surfaces()

        return response

    def _separate_stl(self, obj):
        return obj.Compute.CFD.mesh.makeRefinementRegion or obj.Compute.CFD.mesh.makeCellSet

    def _has_cellsets(self):
        cellset_objects = [obj for obj in bpy.context.visible_objects if obj.Compute.CFD.mesh.makeCellSet]
        return True if cellset_objects else False

    def upload_separate_surfaces(self):
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        logger.info("Writing refinement regions")
        separate_objects = [obj for obj in bpy.context.visible_objects if self._separate_stl(obj)]
        for obj in separate_objects:
            name = foamUtils.formatObjectName(obj.name)
            logger.info(f" - Writing separate stl region: {name}")
            geometry = io.StringIO()
            asciiSTLExport.writeObjectsToFile(geometry, objects = [obj])
            geometry.seek(0)
            logger.info(" -- Cast refinement regions and cell sets to STL format")
            response = GenericViewSet(
                f'/api/task/{task_id}/file/foam/constant/triSurface/{name}.stl/'
            ).update(
                None,
                geometry.read().encode('utf8'),
                raw=True
            )

    def upload_setset(self):
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        cellset_objects = [obj for obj in bpy.context.visible_objects if obj.Compute.CFD.mesh.makeCellSet]
        if not cellset_objects:
            return None

        setset_str = ""
        for obj in cellset_objects:
            name = foamUtils.formatObjectName(obj.name)
            setset_str += f'cellSet {name} new surfaceToCell "constant/triSurface/{name}.stl" ((0 0 0)) true true false 0 0\n'

            logger.info(f" - Writing separate setSet file:\n\n {setset_str}")
            response = GenericViewSet(
                f'/api/task/{task_id}/file/foam/cellSets.setSet/'
            ).update(
                None,
                setset_str.encode('utf8'),
                raw=True
            )

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

    def write_mesh_files(self):
        """ Upload the geometry and dispatch the task in one operation
        """
        mesh_properties = bpy.context.scene.Compute.CFD.mesh
        solver_properties = bpy.context.scene.Compute.CFD.solver
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        # Get or create an empty setup task
        setup_task = self.get_or_create_task(
            project_id, 'setup', task_id,
        )

        # Get or create the mesh setup task as a child
        setup_mesh_task = self.get_or_create_task(
            project_id, 'setup mesh', setup_task['uid']
        )

        # Write the mesh files
        setup_mesh_task = GenericViewSet(
            f'/api/project/{project_id}/task/'
        ).update(
            setup_mesh_task['uid'],
        {
            'status': "pending",
            'config': {
                'task_type': 'magpy',
                'cmd': 'cfd.io.tasks.write_mesh',
                'base_mesh': mesh_properties.domain_json(),
                'snappyhex_mesh': mesh_properties.snappy_json()
            }
        })

        return setup_mesh_task

    def write_solver_files(self):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        # Get or create an empty setup task
        setup_task = self.get_or_create_task(
            project_id, 'setup', task_id
        )

        # Get or create the mesh setup task as a child
        setup_solution_task = self.get_or_create_task(
            project_id, 'setup solution', setup_task['uid']
        )

        # the action to create the CFD files
        setup_solution_task = GenericViewSet(
            f'/api/project/{project_id}/task/'
        ).update(
            setup_solution_task['uid'],
            {
                'status': "pending",
                'config': {
                    'task_type': 'magpy',
                    'cmd': 'cfd.io.tasks.write_solution',
                    'solution': solver_properties.to_json()
                }
            }
        )

        return setup_solution_task


    def run_mesh_pipeline(self):
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids
        decompN = bpy.context.scene.Compute.CFD.task.decompN

        # Get or create an empty setup task
        setup_task = self.get_or_create_task(
            project_id, 'setup', task_id
        )

        # Get or create the mesh task
        mesh_task = self.get_or_create_task(
            project_id, 'mesh', task_id, dependent_on=setup_task['uid']
        )

        commands = [
            'blockMesh',
            "snappyHexMesh -overwrite",
            "reconstructParMesh -constant -mergeTol 1e-6",
            "!checkMesh -writeSets vtk",
            "foamToSurface -constant surfaceMesh.obj"
        ]

        cellset_objects = [obj for obj in bpy.context.visible_objects if obj.Compute.CFD.mesh.makeCellSet]
        if len(cellset_objects) > 0:
            commands.append("!setSet -batch zones.setSet")

        # Get or create the mesh task
        mesh_task = GenericViewSet(
            f'/api/project/{project_id}/task/'
        ).update(
            mesh_task['uid'],
            {
                'status': "pending",
                'config': {
                    'task_type': 'cfd',
                    'cmd': 'pipeline',
                    'cpus': [i for i in decompN],
                    'commands': commands
                }
            }
        )

        return mesh_task

    def run_solver(self):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        control_properties = bpy.context.scene.Compute.CFD.control
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids
        decompN = bpy.context.scene.Compute.CFD.task.decompN

        # Get or create the mesh task
        mesh_task = self.get_or_create_task(
            project_id, 'mesh', task_id
        )

        # Get or create an empty setup task
        solver_task = self.get_or_create_task(
            project_id, 'solution', task_id, dependent_on=mesh_task['uid']
        )

        # Dispatch to the mesh task
        solver_task = GenericViewSet(
            f'/api/project/{project_id}/task/'
        ).update(
            solver_task['uid'],
            {
                'status': "pending",
                'config': {
                    'task_type': 'cfd',
                    'cmd': 'pipeline',
                    'commands': [
                        solver_properties.name,
                        "reconstructPar -noZero"
                    ],
                    'cpus': [i for i in decompN],
                    'iterations': {
                        'init': control_properties.endTime
                    }
                }
            }
        )

        return solver_task

    def run_wind_tunnel(self):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        mesh_properties = bpy.context.scene.Compute.CFD.mesh
        control_properties = bpy.context.scene.Compute.CFD.control
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids
        decompN = bpy.context.scene.Compute.CFD.task.decompN

        # Get or create the mesh task
        mesh_task = self.get_or_create_task(
            project_id, 'mesh', task_id
        )

        # Angles and increments
        n_angles = control_properties.n_angles
        incr = 360 / n_angles

        # Get the details of the domain
        # Note: these are optional - as these are also stored in the foam.config file on the server when the case is setup
        mesh_properties_json = mesh_properties.domain_json()
        cell_dimensions = mesh_properties_json['cell_size']
        bb = mesh_properties_json['bounding_box']
        bounding_box = [abs(bb['max'][i] - bb['min'][i]) for i in range(3)]

        # Get or create an empty setup task
        solver_task = self.get_or_create_task(
            project_id, 'VirtualWindTunnel', task_id,
            dependent_on=mesh_task['uid'],
            config = {
                'task_type': 'cfd',
                'cmd': 'wind_tunnel',
                'case_dir': "foam",
                'commands': [i * incr for i in range(n_angles)],
                'cpus': [i for i in decompN],
                'cell_dimensions': {"x": cell_dimensions, "y": cell_dimensions, "z": cell_dimensions},
                'bounding_box': {"x": bounding_box[0], "y": bounding_box[1], "z": bounding_box[2]},
                'iterations': {
                    'init': control_properties.endTime,
                    'run': control_properties.iters_n or control_properties.endTime
                }
            }
        )

        return solver_task

    def run_wind_thresholds(self):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        control_properties = bpy.context.scene.Compute.CFD.control
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        # Get or create an empty setup task
        vwt_task = self.get_or_create_task(
            project_id, 'VirtualWindTunnel', task_id, dependent_on=mesh_task['uid']
        )

        # Get or create an empty setup task
        solver_task = self.get_or_create_task(
            project_id, 'WindThreshold', task_id,
            dependent_on=vwt_task['uid'],
            config = {
                'task_type': 'cfd',
                'cmd': 'run_wind_thresholds',
                'case_dir': "foam",
                'cpus': [6, 4, 1],
                'patches': [],
                'epw_file': ''
            }
        )

        return solver_task

    def clean_processor_dirs(self, path_prefix="foam"):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        control_properties = bpy.context.scene.Compute.CFD.control
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        # Get the file list
        files = GenericViewSet(
            f'/api/task/{task_id}/file/'
        ).list()

        # Get the processor folder paths using regex
        processor_paths = set()
        for _file in files:
            processors = re.findall(f'{path_prefix}/processor[0-9]*/', _file.get("file"))
            processor_paths = processor_paths.union(set(processors))
        logger.info(f"Got processor folder paths: {processor_paths}")

        # Delete each of the paths
        for path in processor_paths:
            response = GenericViewSet(
                f'/api/task/{task_id}/file/'
            ).delete(path)
            logger.info(f"Deleted processor path: {path}")
            time.sleep(0.05)     # Sleep for a bit to avoid throttling

    def clean_mesh_files(self, path_prefix="foam/constant"):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        control_properties = bpy.context.scene.Compute.CFD.control
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        # Get the file list
        files = GenericViewSet(
            f'/api/task/{task_id}/file/'
        ).list()

        # Get the processor folder paths using regex
        mesh_files = set()
        for _file in files:
            paths = re.findall(f'{path_prefix}/polyMesh/.*', _file.get("file"))
            paths = [i for i in paths if not i.endswith('blockMeshDict')]
            mesh_files = mesh_files.union(set(paths))

        # Get the first level files and folders
        for _path in list(mesh_files):
            folder_path = re.findall(".*/polyMesh/.*/", _path)
            if folder_path:
                mesh_files.remove(_path)
                mesh_files = mesh_files.union(set(folder_path))

        logger.info(f"Got mesh file and folder paths: {mesh_files}")

        # Delete each of the paths
        for path in mesh_files:
            response = GenericViewSet(
                f'/api/task/{task_id}/file/'
            ).delete(path)
            logger.info(f"Deleted mesh file path: {path}")
            time.sleep(0.05)     # Sleep for a bit to avoid throttling

    def probe_selected(self):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        postproc_properties = bpy.context.scene.Compute.CFD.postproc
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        # Get or create an empty setup task
        sub_task = self.get_or_create_task(
            project_id, 'PostProcess', task_id
        )

        fields = [i.strip() for i in postproc_properties.probe_fields.split(',')]

        config = {
            'task_type': 'cfd',
            "cmd": "pipeline",
            "case_dir": f"{postproc_properties.task_case_dir}/",
            "cpus": [1, 1, 1],
            "commands": [
                "write_sample_set",
                "!postProcess -func internalCloud"
            ],
            "fields": fields,
            "sets": get_sets_from_selected()
        }

        # the action to create the CFD files
        setup_task = GenericViewSet(
            f'/api/project/{project_id}/task/'
        ).update(
            sub_task['uid'],
            {
                'status': "pending",
                'config': config
            }
        )

        # Start polling for the probe results
        if postproc_properties.auto_load_probes:
            self.load_selected_probes()

        return setup_task

    def load_selected_probes(self):
        from procedural_compute.core.operators import fetch_async, fetch_sync

        solver_properties = bpy.context.scene.Compute.CFD.solver
        postproc_properties = bpy.context.scene.Compute.CFD.postproc
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        # We should first check the VWT folder and get all of the angles that are available

        first_object = bpy.context.selected_objects[0]
        base_url = f"/api/task/{task_id}/file"  # {_settings.host}
        file_url = f"{base_url}/{postproc_properties.task_case_dir}/postProcessing/internalCloud/{postproc_properties.probe_time_dir}/{first_object.name}_{postproc_properties.load_probe_field}.xy/"

        def handle_probe_data(data):
            lines = data.splitlines()
            logger.info(f"GOT DATA FOR {file_url}. Lines: {len(lines)}.  Applying to object: {first_object.name}")
            color_object(first_object, lines, scale=[postproc_properties.probe_min_range, postproc_properties.probe_max_range])

        logger.info(f"Waiting for file from url: {file_url}")
        fetch_async(file_url, callback=handle_probe_data, timeout=30, query_params={'download': 'true'})

    def clean_task(self):
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        # Get the file list
        files = GenericViewSet(
            f'/api/task/{task_id}/file/'
        ).list()

        # Get the root folders
        root_paths = set([f.get('file').split('/')[0] for f in files if "/" in f.get('file', "")])
        root_paths = root_paths.difference(['logs'])

        logger.info(f"Got mesh file and folder paths: {root_paths}")
        to_json(list(root_paths), log=True)

        # Get the list of sub-tasks to the main task 
        tasks  = GenericViewSet(
            f"/api/project/{project_id}/task/"
        ).list(
            query_params = {
                "parent__pk": task_id
            }
        )
        logger.info(f"Got {len(tasks)} sub-tasks for project {project_id}, task {task_id} to delete")
        to_json([i.get('uid') for i in tasks], log=True)
        #to_json(tasks, log=True)


        # Delete each of the paths
        for path in root_paths:
            response = GenericViewSet(
                f"/api/task/{task_id}/file/"
            ).delete(path)
            logger.info(f"Deleting root path: {path}")
            time.sleep(0.2)     # Sleep for a bit to avoid throttling

        # Delete the tasks
        for task in tasks:
            _id = task.get("uid") 
            response = GenericViewSet(
                f"/api/task/"
            ).delete(_id)
            logger.info(f"Deleting task: {_id}")
            time.sleep(0.2)     # Sleep for a bit to avoid throttling


bpy.utils.register_class(SCENE_OT_cfdOperators)
