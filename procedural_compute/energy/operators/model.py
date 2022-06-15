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

    command: bpy.props.StringProperty(name="Command", description="parse String", default="")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH' and context.mode == 'OBJECT')

    def execute(self, context):
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
        self.execute(context)
        return {'FINISHED'}

    def fill_floors_and_separate(self):
        from .fill_floors import fill_and_separate, make_object
        # Do the operation
        new_objects = {obj.name: fill_and_separate(obj) for obj in bpy.context.selected_objects}

        logger.info(f"Got new objects to create: {new_objects}")

        for obj_name, loops in new_objects.items():
            for data in loops:
                make_object(obj_name, **data)

        #bpy.context.scene.collection.objects.unlink(obj)
        #bpy.data.objects.remove(obj)

bpy.utils.register_class(SCENE_OT_ENERGY_MODEL_OPERATORS)
