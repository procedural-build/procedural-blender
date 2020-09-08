###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy
from procedural_compute.core.utils.addRemoveMeshObject import addObject
from mathutils import Vector
from random import random


class addCFDBoundingBox(bpy.types.Operator):
    '''Add a CFD BoundingBox'''
    bl_idname = "mesh.add_cfdbb"
    bl_label = "Add CFD-BB"
    bl_options = {'REGISTER', 'UNDO'}

    scale: bpy.props.FloatProperty(default=1.5)
    offset: bpy.props.FloatProperty(default=10.0)
    zscale: bpy.props.FloatProperty(default=2.0)
    centre: bpy.props.BoolProperty(default=True)
    square: bpy.props.BoolProperty(default=True)

    def draw(self, context):
        layout = self.layout
        layout.row().prop(self, "centre")
        layout.row().prop(self, "square")
        layout.row().prop(self, "scale")
        layout.row().prop(self, "offset")
        layout.row().prop(self, "zscale")

    def getBounds(self, obs):
        mins = [-0.5, -0.5, 0.0]
        maxs = [0.5, 0.5, 1.0]
        for o in obs:
            if not o.type == 'MESH':
                continue
            if not len(o.data.vertices) > 0:
                continue
            for i in range(7):
                v = o.matrix_world @ Vector(o.bound_box[i])
                for j in range(3):
                    mins[j] = v[j] if v[j] < mins[j] else mins[j]
                    maxs[j] = v[j] if v[j] > maxs[j] else maxs[j]
        return (Vector(mins), Vector(maxs))

    def add(self):
        # Get the bounding box of all mesh objects
        (bmin, bmax) = self.getBounds(bpy.context.visible_objects)

        # Deselect all objects
        sc = bpy.context.scene
        for o in sc.objects:
            o.select_set(False)

        # Add bounding box frame
        l = -0.5
        h = 0.5
        vs = [
            [h, h, l], [h, l, l],
            [l, l, l], [l, h, l],
            [h, h, h], [h, l, h],
            [l, l, h], [l, h, h]
        ]
        es = [
            [0, 1], [0, 3], [0, 4], [1, 2],
            [1, 5], [2, 3], [2, 6], [3, 7],
            [4, 5], [4, 7], [5, 6], [6, 7]
        ]
        cfdBB = addObject("cfdBoundingBox", vlist=vs, elist=es)

        # Add empty min/max markers, parent and loc position to parent
        markerNames = ["MinX", "MaxX", "MinY", "MaxY", "MinZ", "MaxZ"]
        locks = ['min_x', 'max_x', 'min_y', 'max_y', 'min_z', 'max_z']
        positions = [Vector([0.0] * 3) for i in range(6)]

        for i in range(3):
            positions[2 * i][i] -= 0.5
            positions[2 * i + 1][i] += 0.5

        for i in range(6):
            name = markerNames[i]
            o = addObject(name, drawName=True)
            o.location = Vector(positions[i])
            o.parent = cfdBB
            # Add a locking constrains
            c = o.constraints.new(type="LIMIT_LOCATION")
            c.owner_space = 'LOCAL'
            for j in range(6):
                setattr(c, 'use_' + locks[j], True)
                v = positions[i][int(j / 2)]
                setattr(c, locks[j], v)

        # Make the actual bounding box the active object
        if self.centre:
            for i in range(2):
                cfdBB.scale[i] = 2 * max(abs(bmax[i]), abs(bmin[i])) * self.scale + self.offset
                cfdBB.location[i] = 0.0
        else:
            for i in range(2):
                cfdBB.scale[i] = (bmax[i] - bmin[i]) * self.scale + self.offset
                cfdBB.location[i] = (bmax[i] + bmin[i]) / 2.0

        if self.square:
            for i in range(2):
                cfdBB.scale[i] = max(cfdBB.scale[0], cfdBB.scale[1])

        # Scale in the z-direction
        cfdBB.scale[2] = abs(bmax[2]) * self.zscale
        bpy.ops.scene.cfdoperators(command="snapCFDBoundingBox")
        cfdBB.location[2] = cfdBB.scale[2] / 2.0

        # Add a cfdMeshKeepPoint
        cfdKP = addObject("cfdMeshKeepPoint", drawName=True)
        cfdKP.location = cfdBB.location + cfdBB.scale * (4 + (random() - 1)) / 16.0

        # Set the cfdBoundingBox as active object
        bpy.context.view_layer.objects.active = cfdBB
        return None

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

    def execute(self, context):
        self.add()
        return{'FINISHED'}


bpy.utils.register_class(addCFDBoundingBox)
