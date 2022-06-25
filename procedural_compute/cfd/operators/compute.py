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

from .utils import get_sets_from_selected, color_object, color_vertices_from_face_attr

import logging
logger = logging.getLogger(__name__)


def get_system_properties():
    _settings = bpy.context.scene.Compute.CFD.task
    solver_properties = bpy.context.scene.Compute.CFD.solver
    control_properties = bpy.context.scene.Compute.CFD.control
    project_id = _settings.project_id
    task_id = _settings.task_id
    return (project_id, task_id, control_properties, solver_properties, _settings)


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


class SCENE_OT_cfdOperators(bpy.types.Operator):
    bl_label = "Compute CFD Operations"
    bl_idname = "scene.compute_operators_cfd"
    bl_description = "Compute CFD Operations"

    command: bpy.props.StringProperty(name="Command", description="parse String", default="")

    def execute(self, context):
        if hasattr(self, self.command):
            logger.info(f"\n\n###### EXECUTING CFD OPERATION: {self.command} ######\n")
            getattr(self, self.command)(context)
        else:
            logger.info(f"{self.command}: Attribute not found!")
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

    def login(self, context):
        """ Login user with provided details OR credentials from environment variables
        """
        secure_login()

    def refresh(self, context):
        """ """
        bpy.ops.scene.compute_operators_core(command="refresh")

    def get_or_create_project_and_task(self, context):
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

    def open_in_browser(self, context):
        _settings = bpy.context.scene.Compute.CFD.task
        project_id = _settings.project_id
        task_id = _settings.task_id
        bpy.ops.wm.url_open(
            url=f"https://compute.procedural.build/project/{project_id}/task/"
        )

    def upload_geometry(self, context):
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

        self.upload_separate_surfaces(context)

        return response

    def _separate_stl(self, obj):
        return obj.Compute.CFD.mesh.makeRefinementRegion or obj.Compute.CFD.mesh.makeCellSet

    def _has_cellsets(self):
        cellset_objects = [obj for obj in bpy.context.visible_objects if obj.Compute.CFD.mesh.makeCellSet]
        return True if cellset_objects else False

    def upload_separate_surfaces(self, context):
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

    def upload_setset(self, context):
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

    def write_mesh_files(self, context):
        """ Upload the geometry and dispatch the task in one operation
        """
        mesh_properties = bpy.context.scene.Compute.CFD.mesh
        solver_properties = bpy.context.scene.Compute.CFD.solver
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        # Get or create an empty setup task
        setup_task = get_or_create_task(
            project_id, 'setup', task_id,
        )

        # Get or create the mesh setup task as a child
        setup_mesh_task = get_or_create_task(
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

    def write_solver_files(self, context):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        # Get or create an empty setup task
        setup_task = get_or_create_task(
            project_id, 'setup', task_id
        )

        # Get or create the mesh setup task as a child
        setup_solution_task = get_or_create_task(
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


    def run_mesh_pipeline(self, context):
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids
        decompN = bpy.context.scene.Compute.CFD.task.decompN

        # Get or create an empty setup task
        setup_task = get_or_create_task(
            project_id, 'setup', task_id
        )

        # Get or create the mesh task
        mesh_task = get_or_create_task(
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

    def run_solver(self, context):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        control_properties = bpy.context.scene.Compute.CFD.control
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids
        decompN = bpy.context.scene.Compute.CFD.task.decompN

        # Get or create the mesh task
        mesh_task = get_or_create_task(
            project_id, 'mesh', task_id
        )

        # Get or create an empty setup task
        solver_task = get_or_create_task(
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

    def run_wind_tunnel(self, context):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        mesh_properties = bpy.context.scene.Compute.CFD.mesh
        control_properties = bpy.context.scene.Compute.CFD.control
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids
        decompN = bpy.context.scene.Compute.CFD.task.decompN

        # Get or create the mesh task
        mesh_task = get_or_create_task(
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
        solver_task = get_or_create_task(
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

    def probe_vwt(self, context):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        postproc_properties = bpy.context.scene.Compute.CFD.postproc
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        attrs = {
            "auto_load_probes": False,
            "probe_fields": "Utrans,p",
            "task_case_dir": "VWT"
        }

        # Backup original values and set them with above values
        org_attrs = {key: getattr(postproc_properties, key) for key in attrs.keys()}
        [setattr(postproc_properties, key, value) for key, value in attrs.items()]

        self.probe_selected(dependent_on="VirtualWindTunnel")

        # Set the original values again
        [setattr(postproc_properties, key, value) for key, value in org_attrs.items()]

    def upload_epw(self, context):
        control_properties = bpy.context.scene.Compute.CFD.control
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        epw_file = bpy.path.abspath(control_properties.epw_file)
        epwName = os.path.basename(epw_file)
        weather_file_path = f"weather/{epwName}"

        with open(epw_file, "rb") as f:
            logger.info(f"Uploading file {epw_file}")
            response = upload_task_file(task_id, weather_file_path, f.read())

        return weather_file_path

    def run_wind_thresholds(self, context):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        control_properties = bpy.context.scene.Compute.CFD.control
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        # Get or create an empty setup task
        sub_task = get_or_create_task(
            project_id, 'WindThreshold', task_id, dependent_on=self.task_name_to_uid("probe")
        )

        # Upload the epw file
        weather_file_path = self.upload_epw()

        config = {
            'task_type': 'cfd',
            'cmd': 'run_wind_thresholds',
            'case_dir': "VWT/",
            "epw_file": weather_file_path,
            "north_angle": control_properties.north_angle,
            'patches': [obj.name for obj in bpy.context.selected_objects if obj.type == "MESH"],
            'thresholds': json.loads(control_properties.thresholds),
            'set_foam_patch_fields': False,
            'cpus': [control_properties.threshold_cpus, 1, 1],
        }

        # the action to create the CFD files
        threshold_task = GenericViewSet(
            f'/api/project/{project_id}/task/'
        ).update(
            sub_task['uid'],
            {
                'status': "pending",
                'config': config
            }
        )

        return threshold_task

    def clean_processor_dirs(self, context, path_prefix="foam"):
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

    def clean_mesh_files(self, context, path_prefix="foam/constant"):
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

    def upload_probe_points(self, context):
        control_properties = bpy.context.scene.Compute.CFD.control
        postproc_properties = bpy.context.scene.Compute.CFD.postproc
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        probe_sets = get_sets_from_selected()
        caseDir = postproc_properties.task_case_dir

        for probe_set in probe_sets:
            name = probe_set.get("name")
            points = probe_set.get("points")

            logger.info(f"Uploading probes from set {name} to the server")

            response = upload_task_file(
                task_id,
                f"{caseDir}/{name}.pts",
                points_to_bytes(points)
            )

        return response

    def task_name_to_uid(self, context, task_name):
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids
        return get_or_create_task(
            project_id, task_name, task_id
        )['uid']

    def probe_selected(self, context, dependent_on=None):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        postproc_properties = bpy.context.scene.Compute.CFD.postproc
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        task_kwargs = {"dependent_on": self.task_name_to_uid(dependent_on)} if dependent_on else {}

        # Get or create an empty setup task
        sub_task = get_or_create_task(
            project_id, 'probe', task_id, **task_kwargs
        )

        # Upload points/mesh files
        sample_sets = [get_sample_files_set(s) for s in get_sets_from_selected()]
        self.upload_probe_points()

        fields = [i.strip() for i in postproc_properties.probe_fields.split(',')]

        config = {
            'task_type': 'cfd',
            "cmd": "pipeline",
            "case_dir": f"{postproc_properties.task_case_dir}/",
            "cpus": [8, 1, 1],
            "commands": [
                "write_sample_set",
                "!postProcess -func internalCloud"
            ],
            "fields": fields,
            "sets": sample_sets
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
            self.load_probes()

        return setup_task

    def load_probe_file(self, context, filename=""):
        from procedural_compute.core.operators import fetch_async, fetch_sync, test_async

        postproc_properties = bpy.context.scene.Compute.CFD.postproc
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        base_url = f"/api/task/{task_id}/file"
        file_url = f"{base_url}/{filename}/"

        logger.info(f"Requests async download of file from: {file_url}")
        fetch_async(
            file_url,
            callback=handle_probe_data,
            callback_kwargs={"scale": [postproc_properties.probe_min_range, postproc_properties.probe_max_range]},
            timeout=600,
            query_params={'download': 'true'}
        )
        #test_async(url=file_url, callback=handle_probe_data)

    def rescale_selected(self, context):
        postproc_properties = bpy.context.scene.Compute.CFD.postproc
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        attr_name = "probe_result"
        scale = [postproc_properties.probe_min_range, postproc_properties.probe_max_range]

        for obj in bpy.context.selected_objects:
            if not attr_name in obj.data.attributes:
                logger.warn(f"Object {obj.name} has no attribute '{attr_name}' set.  Skipping.")
            # Scale the values
            color_vertices_from_face_attr(obj, scale=scale, attr_name=attr_name)

    def load_probes(self, context):
        solver_properties = bpy.context.scene.Compute.CFD.solver
        postproc_properties = bpy.context.scene.Compute.CFD.postproc
        (project_id, task_id) = bpy.context.scene.Compute.CFD.task.ids

        # We should first check the VWT folder and get all of the angles that are available
        logger.info(f"Getting file list for task: {task_id}")
        all_files = GenericViewSet(f'/api/task/{task_id}/file/').list()

        # Filter just the files we want
        prefix = f"{postproc_properties.task_case_dir}/postProcessing/internalCloud/"
        filenames = [f.get("file") for f in all_files if f.get("file").startswith(prefix)]
        #filenames = filenames[:1] # for debugging only
        logger.info(f"Got probe files: {filenames}")

        for filename in filenames:
            self.load_probe_file(context, filename=filename)


    def clean_task(self, context):
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

def get_object_field_names(file_url):
    url_parts = [i for i in file_url.split("/") if i]
    angle = "%06.2f"%(float(url_parts[-2]))
    file_name = url_parts[-1]
    file_name_parts = file_name.split("_")
    object_name = "_".join(file_name_parts[:-1])
    field_name = file_name_parts[-1].split(".")[0]
    case_dir = file_url.split("/postProcessing/internalCloud/")[0].split("/")[-1]
    return (case_dir, angle, object_name, field_name)

def get_or_create_collection(parent_collection, name):
    collection = parent_collection.children.get(name)
    if not collection:
        collection = bpy.context.blend_data.collections.new(name=name)
        parent_collection.children.link(collection)
        logger.info(f"Created collection {parent_collection.name} -> {name}")
    return collection

def get_or_create_collection_path(path: list):
    _root = bpy.context.collection
    collections = [_root]
    for i in range(len(path)):
        collections.append(get_or_create_collection(collections[i], path[i]))
    return collections

def handle_probe_data(file_url, data, scale=[0, 5]):
    lines = data.splitlines()
    logger.info(f"GOT DATA FOR {file_url} with {len(lines)} lines.")

    # Deconstruct the file name to get the details of where we will store the object
    (case_dir, angle, object_name, field_name) = get_object_field_names(file_url)
    target_object_name = f"{angle}-{object_name}-{field_name}"
    logger.info(f"Setting values to collection: {case_dir}/{field_name}/{object_name}-{field_name} in object: {target_object_name} [scale={scale}]")

    # Create the nested collections to where we will store the results for each angle/field
    collections = get_or_create_collection_path([case_dir, field_name, f"{object_name}-{field_name}"])
    target_collection = collections[-1]
    logger.info(f"Got target collection: {'/'.join([i.name for i in collections])}")

    # Delete any object that might already exist
    target_object = target_collection.objects.get(target_object_name)
    if target_object:
        logger.info(f"Deleting existing object {target_object.name} from collection {target_collection.name}")
        bpy.data.objects.remove(target_object, do_unlink=True)

    # Copy the base object (and mesh) and link to the target collection
    obj = bpy.data.objects[object_name]
    target_object = obj.copy()
    target_object.data = obj.data.copy()
    target_object.name = target_object_name
    target_collection.objects.link(target_object)
    logger.info(f"Copied object {obj.name} to {target_object.name} in collection {target_collection.name}")

    # Color the object
    color_object(target_object, lines, scale=scale)

def get_sample_files_set(s):
    name = s.get("name")
    return {"name": name, "file": f"{name}.pts"}


def points_to_bytes(points):
    return json.dumps({"file": points}, indent=4).encode("utf8")


def upload_task_file(task_id, path, bytes):
    return GenericViewSet(
        f'/api/task/{task_id}/file/{path}'
    ).update(
        None,
        bytes,
        raw=True
    )
