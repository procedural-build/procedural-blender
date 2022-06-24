###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
import bmesh
import os
import shutil
import glob

import procedural_compute.cfd.utils.foamCaseFiles as foamCaseFiles
import procedural_compute.cfd.utils.asciiSTLExport as asciiSTLExport
import procedural_compute.cfd.utils.mesh as mesh

import procedural_compute.cfd.solvers

from procedural_compute.core.utils import subprocesses, fileUtils
from procedural_compute.core.utils import threads
from procedural_compute.core.utils.subprocesses import waitSTDOUT

import logging
logger = logging.getLogger(__name__)

class SCENE_OT_ENERGY_MODEL_OPERATORS(bpy.types.Operator):
    bl_label = "Energy Model Operations"
    bl_idname = "scene.energyoperators"
    bl_description = "Generic Energy Model Operations"
    bl_context = "scene"
    bl_options = {'REGISTER', 'UNDO'}

    command: bpy.props.EnumProperty(name="Command", items=(
        ("intersect_edges", "Intersect edges", ""),
        ("fill_floors_and_separate", "Fill floors and separate", ""),
        ("make_walls", "Make walls", ""),
        ("explode_faces", "Explode faces", ""),
        ("inset_openings", "Inset openings", ""),
    ))
    wall_height: bpy.props.FloatProperty(name="Height", min=0.0, default=4.5)
    inset_thickness: bpy.props.FloatProperty(name="Thickness", min=0.0, default=0.1)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH' and context.mode == 'OBJECT')

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Model construction operators")

        row = col.row()
        row.prop(self, "command")

        if self.command == "make_walls":
            row = col.row()
            row.prop(self, "wall_height")

        if self.command == "inset_openings":
            row = col.row()
            row.prop(self, "inset_thickness")

    def execute(self, context):
        logger.info(f"Running energyoperators.execute")
        if hasattr(self, self.command):
            # disable global undo, so we can undo all steps with a single ctrl+z
            undo = context.preferences.edit.use_global_undo
            bpy.context.preferences.edit.use_global_undo = False
            # Execute the function
            c = getattr(self, self.command)()
            # Turn undo back on
            bpy.context.preferences.edit.use_global_undo = undo
        else:
            print(self.command + ": Attribute not found!")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def intersect_edges(self):
        from .intersection import pydata_from_intersections

        # Get the selected meshes
        objects = [o for o in bpy.context.selected_objects if o.type == 'MESH']
        bpy.ops.object.select_all(action='DESELECT')

        # Make a new object
        new_obj = make_object_from_pydata(
            "edge_intersections",
            **pydata_from_intersections(objects)
        )

        # Select the new object and make it active
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = new_obj
        new_obj.select_set(True)

        # Remove doubles in the new object
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode = 'OBJECT')

    def fill_floors_and_separate(self):
        """ Find and fill all enclosed edges of a polygon and fill with a new object """
        from procedural_compute.energy.operators.fill_floors import edge_loop_polygons

        # Get the inside edge loops
        new_objects = {obj.name: edge_loop_polygons(obj) for obj in bpy.context.selected_objects}
        logger.info(f"Got new objects to create: {new_objects}")
        bpy.ops.object.select_all(action='DESELECT')

        for obj_name, loops in new_objects.items():
            for data in loops:
                logger.info(f"Creating new polygon with data: {data}")
                make_filled_polygon_object(obj_name, **data)

        #bpy.context.scene.collection.objects.unlink(obj)
        #bpy.data.objects.remove(obj)

    def make_walls(self):
        """ Extrude object edges vertically to create walls """
        sc = bpy.context.scene
        bpy.context.tool_settings.mesh_select_mode = (False, True, False)
        objects = [o for o in bpy.context.selected_objects if o.type == "MESH"]
        bpy.ops.object.select_all(action='DESELECT')
        _ = [extrude_to_walls(sc, o, self.wall_height) for o in objects]

    def explode_faces(self):
        """ Separate an objects faces into individual objects """
        org_select_mode = bpy.context.tool_settings.mesh_select_mode[:]
        bpy.context.tool_settings.mesh_select_mode = [False, False, True]
        _ = [separate_faces(o) for o in bpy.context.selected_objects if o.type == "MESH"]
        bpy.context.tool_settings.mesh_select_mode = org_select_mode

    def inset_openings(self):
        """ Inset polygons of selected objects to create openings """
        # Make sure we are in face select mode (save current select_mode)
        org_select_mode = bpy.context.tool_settings.mesh_select_mode[:]
        bpy.context.tool_settings.mesh_select_mode = [False, False, True]

        # All the objects have to have their transformations applied
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Do the operation
        objects_to_inset = [o for o in bpy.context.selected_objects if o.type == "MESH"]
        bpy.ops.object.select_all(action='DESELECT')
        new_objects = [inset_all_faces(o, self.inset_thickness) for o in objects_to_inset]

        # Select the new opening objects that have been created
        bpy.ops.object.select_all(action='DESELECT')
        _ = [o.select_set(True) for o in new_objects]
        bpy.context.view_layer.objects.active = new_objects[0]

        # cleaning up, restoring all old setting
        bpy.context.tool_settings.mesh_select_mode = org_select_mode


# Only needed if you want to add into a dynamic menu.
def menu_func(self, context):
    self.layout.operator(SCENE_OT_ENERGY_MODEL_OPERATORS.bl_idname, text="Energy model operations")

bpy.utils.register_class(SCENE_OT_ENERGY_MODEL_OPERATORS)
bpy.types.VIEW3D_MT_object.append(menu_func)


###################


def separate_faces(obj):
    if len(obj.data.polygons) < 2:
        logger.info(f"Not enough faces ({len(obj.data.polygons)}) on {obj.name} to explode")
        return None
    bpy.context.view_layer.objects.active = obj
    # Deselect all faces
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    # Get mesh data
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    # Separation loop - separate linked flat faces
    n_faces = len(mesh.polygons)
    counter = 0
    while len(bm.faces) > 1:
        logger.info(f"Exploding face {counter} / {n_faces} faces from object {obj.name} [remaining: {len(bm.faces)}]")
        bm.faces.ensure_lookup_table()
        # select first face available
        bm.faces[0].select = True
        # Show the updates in the viewport
        bmesh.update_edit_mesh(mesh)
        # Separate the faces
        bpy.ops.mesh.separate(type = 'SELECTED')
        counter += 1
    # Return to object mode (the last face should be remaining on the original object)
    bpy.ops.object.mode_set(mode = 'OBJECT')


def inset_all_faces(obj, thickness):
    logger.info(f"Insetting all faces on object {obj.name} to create an opening")
    # Select only the object of interest
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    #
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.inset(
        use_boundary=True,
        use_even_offset=True,
        use_relative_offset=False,
        thickness=thickness,
        depth=0,
        use_outset=False,
        use_select_inset=False
    )
    # Invert the selection and separate the inset part
    bpy.ops.mesh.separate(type = 'SELECTED')
    # Set back to object mode
    bpy.ops.object.mode_set(mode = 'OBJECT')
    new_objects = [o for o in bpy.context.selected_objects if not o == obj]
    return new_objects[0] if new_objects else None


def make_object_from_pydata(obj_name, vertices=[], edges=[]):
    mesh = bpy.data.meshes.new(obj_name)
    mesh.from_pydata(vertices, edges, [])
    new_obj = bpy.data.objects.new(obj_name, mesh)
    bpy.context.scene.collection.objects.link(new_obj)
    bpy.context.view_layer.objects.active = new_obj
    new_obj.select_set(True)
    return new_obj


def make_filled_polygon_object(obj_name, vertices=[], edges=[]):
    logger.info(f"Creating fill object from {obj_name} with {len(edges)} edges and {len(vertices)} vertices")
    bpy.ops.object.select_all(action='DESELECT')

    # Create a new mesh
    new_obj = make_object_from_pydata(obj_name, vertices=vertices, edges=edges)

    # Fill the resultant polygon
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode = 'OBJECT')


def extrude_to_walls(scene, obj, height):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_edges_indiv()
    bpy.ops.transform.translate(value=(0,0, height))
    bpy.ops.object.mode_set(mode='OBJECT')
