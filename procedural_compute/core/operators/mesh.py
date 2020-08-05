###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ods-engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################


import bpy

from procedural_compute.core.utils.addRemoveMeshObject import addObject
from mathutils.geometry import intersect_line_line, intersect_ray_tri

################################
# MESH OPERATORS
################################


class addNorthMarker(bpy.types.Operator):
    bl_idname = "mesh.add_northmarker"
    bl_label = "Add North Marker"

    def execute(self, context):
        # Deselect all objects
        sc = bpy.context.scene
        for o in sc.objects:
            o.select_set(False)
        # Add a triangle and line
        o = addObject("northMarker", vlist=[
            [0.0, 1.0, 0.0],
            [-1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.5, 0.0],
            [0.0, -1.0, 0.0]
        ], elist=[
            [0, 1],
            [1, 2],
            [2, 0],
            [3, 4]
        ])
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.primitive_circle_add()
        bpy.ops.object.mode_set(mode = 'OBJECT')
        # Set the rotation to site rotation
        #o = bpy.context.object
        o.rotation_euler[2] = -1.0 * sc.Site.northAxis
        return{'FINISHED'}


bpy.utils.register_class(addNorthMarker)


class cursorToIntersection(bpy.types.Operator):
    bl_idname = "view3d.cursor_to_intersection"
    bl_label = "Cursor To Intersection"

    def execute(self, context):
        o = context.object
        M = o.matrix_world
        if not context.mode == 'EDIT_MESH':
            self.report({'ERROR'}, 'Only works in edit mode')
            bpy.ops.object.mode_set(mode='EDIT')
            return{'FINISHED'}
        bpy.ops.object.mode_set(mode='OBJECT')
        selectedEdges = [e for e in bpy.context.object.data.edges if e.select]
        if len(selectedEdges) < 2:
            self.report({'ERROR'}, 'Insufficient number of edges selected')
            bpy.ops.object.mode_set(mode='EDIT')
            return{'FINISHED'}

        if len(selectedEdges) == 2:
            # Get the line intersection of the two edges
            Pints = intersect_line_line(
                M * o.data.vertices[selectedEdges[0].vertices[0]].co,
                M * o.data.vertices[selectedEdges[0].vertices[1]].co,
                M * o.data.vertices[selectedEdges[1].vertices[0]].co,
                M * o.data.vertices[selectedEdges[1].vertices[1]].co
            )

            if Pints is None:
                self.report({'ERROR'}, 'Selected edges are PARALLEL')
                bpy.ops.object.mode_set(mode='EDIT')
                return{'FINISHED'}

            bpy.context.scene.cursor_location = (Pints[0] + Pints[1]) / 2.0
            bpy.ops.object.mode_set(mode='EDIT')
            return{'FINISHED'}

        if len(selectedEdges) > 2:
            # Get the intersection of an edge and a face
            selectedEdges = selectedEdges[:3]

            # Find the edges that form a face (share a common vertex)
            commonEdges = []
            for e in selectedEdges:
                for ee in selectedEdges:
                    if e.index == ee.index:
                        continue
                    if (e.key[0] in ee.key) or (e.key[1] in ee.key):
                        commonEdges = [e, ee]

            if len(commonEdges) == 0:
                self.report({'ERROR'}, 'No common edges of a TRIANGULAR FACE found.  Please select TWO common edges of a face and another edge.')
                bpy.ops.object.mode_set(mode='EDIT')
                return{'FINISHED'}

            lonelyEdge = set(selectedEdges).difference(set(commonEdges)).pop()
            # Get the intersection of the lonelyEdge and the face (assuming it is triangular)
            rayOrigin = o.data.vertices[lonelyEdge.vertices[0]].co
            rayDirection = o.data.vertices[lonelyEdge.vertices[1]].co - rayOrigin
            triVerts = []
            for e in commonEdges:
                triVerts += [v for v in e.vertices]
            triVerts = list(set(triVerts))
            if not len(triVerts) == 3:
                self.report({'ERROR'}, 'Something is wrong with your triangle edge selection')
                bpy.ops.object.mode_set(mode='EDIT')
                return{'FINISHED'}
            Pint = intersect_ray_tri(
                M * o.data.vertices[triVerts[0]].co,
                M * o.data.vertices[triVerts[1]].co,
                M * o.data.vertices[triVerts[2]].co,
                rayDirection, rayOrigin
            )
            if Pint is None:
                self.report({'ERROR'}, 'Edge and triangle do not intersect.  Try selecting another triangle.')
                bpy.ops.object.mode_set(mode='EDIT')
                return{'FINISHED'}

            bpy.context.scene.cursor_location = Pint

        bpy.ops.object.mode_set(mode='EDIT')
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}


bpy.utils.register_class(cursorToIntersection)


class SCENE_OT_explodePolygons(bpy.types.Operator):
    bl_label = "Explode Polygons"
    bl_idname = "scene.explode_polygons"
    bl_description = "Explode Polygons"

    def execute(self, context):
        sc = context.scene
        obs = context.selected_objects
        # disable global undo, so we can undo all steps with a single ctrl+z
        undo = context.preferences.edit.use_global_undo
        bpy.context.preferences.edit.use_global_undo = False
        # Make sure we are in face select mode (save current select_mode)
        select_mode = bpy.context.tool_settings.mesh_select_mode[:]
        bpy.context.tool_settings.mesh_select_mode = [False, False, True]
        # Go through each object exploding linked flat faces
        for o in obs:
            if o.type != 'MESH':
                continue
            if len(o.data.polygons) == 0:
                continue
            sc.objects.active = o
            # Deselect all faces
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode = 'OBJECT')
            # Get mesh data
            mesh = o.data
            # Separation loop - separate linked flat faces
            stopLoop = False
            while not stopLoop:
                mesh.polygons[0].select = True
                # If there is more than one polygon in the mesh then separate the selected face
                if len(mesh.polygons) > 1:
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.separate(type = 'SELECTED')  # separate face in edit mode
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                else:
                    stopLoop = True
        # cleaning up, restoring all old setting
        bpy.context.tool_settings.mesh_select_mode = select_mode
        bpy.context.preferences.edit.use_global_undo = undo
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}


bpy.utils.register_class(SCENE_OT_explodePolygons)


class SCENE_OT_explodeLinkedFlatFaces(bpy.types.Operator):
    bl_label = "Explode Linked"
    bl_idname = "scene.explode_linked"
    bl_description = "Explode Linked"

    def execute(self, context):
        obs = context.selected_objects
        # disable global undo, so we can undo all steps with a single ctrl+z
        undo = context.preferences.edit.use_global_undo
        bpy.context.preferences.edit.use_global_undo = False
        # Make sure we are in face select mode (save current select_mode)
        select_mode = bpy.context.tool_settings.mesh_select_mode[:]
        bpy.context.tool_settings.mesh_select_mode = [False, False, True]
        # Go through each object exploding linked flat faces
        for o in obs:
            if (o.type != 'MESH') or (len(o.data.polygons) == 0):
                continue
            context.view_layer.objects.active = o
            # Deselect all faces
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode = 'OBJECT')
            # Get mesh data
            mesh = o.data
            # Separation loop - separate linked flat faces
            stopLoop = False
            while not stopLoop:
                mesh.polygons[0].select = True
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_linked()
                bpy.ops.object.mode_set(mode = 'OBJECT')
                # Check that the number of selected faces != total number of faces
                c = 0
                for f in mesh.polygons:
                    if f.select:
                        c += 1
                # If not then separate the selected faces
                if c != len(mesh.polygons):
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.separate(type = 'SELECTED')  # separate face in edit mode
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                else:
                    stopLoop = True
        # cleaning up, restoring all old setting
        bpy.context.tool_settings.mesh_select_mode = select_mode
        bpy.context.preferences.edit.use_global_undo = undo
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}


bpy.utils.register_class(SCENE_OT_explodeLinkedFlatFaces)


class SCENE_OT_explodeLinkedFlatFaces(bpy.types.Operator):
    bl_label = "Explode Linked Flat Faces"
    bl_idname = "scene.explode_linked_flat_faces"
    bl_description = "Explode Linked Flat Faces"

    def execute(self, context):
        sc = context.scene
        obs = context.selected_objects
        # disable global undo, so we can undo all steps with a single ctrl+z
        undo = context.preferences.edit.use_global_undo
        bpy.context.preferences.edit.use_global_undo = False
        # Make sure we are in face select mode (save current select_mode)
        select_mode = bpy.context.tool_settings.mesh_select_mode[:]
        bpy.context.tool_settings.mesh_select_mode = [False, False, True]
        # Go through each object exploding linked flat faces
        for o in obs:
            if o.type != 'MESH':
                continue
            if len(o.data.polygons) == 0:
                continue
            sc.objects.active = o
            # Deselect all faces
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode = 'OBJECT')
            # Get mesh data
            mesh = o.data
            # Separation loop - separate linked flat faces
            stopLoop = False
            while not stopLoop:
                mesh.polygons[0].select = True
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.faces_select_linked_flat(sharpness=1)
                bpy.ops.object.mode_set(mode = 'OBJECT')
                # Check that the number of selected faces != total number of faces
                c = 0
                for f in mesh.polygons:
                    if f.select:
                        c += 1
                # If not then separate the selected faces
                if c != len(mesh.polygons):
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.separate(type = 'SELECTED')  # separate face in edit mode
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                else:
                    stopLoop = True
        # cleaning up, restoring all old setting
        bpy.context.tool_settings.mesh_select_mode = select_mode
        bpy.context.preferences.edit.use_global_undo = undo
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}


bpy.utils.register_class(SCENE_OT_explodeLinkedFlatFaces)


class removeDoublesInSelected(bpy.types.Operator):
    bl_idname = "scene.remove_doubles"
    bl_label = "Remove Doubles in Selected"

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}

    def execute(self, context):
        sc = bpy.context.scene
        for o in bpy.context.selected_objects:
            sc.objects.active = o
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}


bpy.utils.register_class(removeDoublesInSelected)
