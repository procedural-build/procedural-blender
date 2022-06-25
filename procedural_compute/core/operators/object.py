###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

from procedural_compute.core.utils import make_tuples
import procedural_compute.core.utils.selectUtils as selectUtils

################################
# OBJECT DISPLAY PROPERTIES
################################


class SCENE_OT_displayTransparent(bpy.types.Operator):
    bl_label = "Display Transparent"
    bl_idname = "scene.displaytransparent"
    bl_description = "Set all selected to display transparent"

    def execute(self, context):
        for o in bpy.context.selected_objects:
            o.show_transparent = True
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}


bpy.utils.register_class(SCENE_OT_displayTransparent)


class SCENE_OT_insetSelected(bpy.types.Operator):
    bl_label = "Inset Faces Individually"
    bl_idname = "scene.insetselected"
    bl_description = "Inset Selected Faces Individually"
    bl_options = {'REGISTER', 'UNDO'}

    thickness: bpy.props.FloatProperty(default=0.1)

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')

    def selectPolys(self, o, indexes):
        bpy.ops.object.mode_set(mode='OBJECT')
        for i in indexes:
            o.data.polygons[i].select = True
        bpy.ops.object.mode_set(mode='EDIT')

    def refresh(self):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

    def deselectAll(self, o):
        for v in o.data.vertices:
            v.select = False
        for e in o.data.edges:
            e.select = False
        for p in o.data.polygons:
            p.select = False
        return

    def execute(self, context):
        o = bpy.context.active_object

        # disable global undo, so we can undo all steps with a single ctrl+z
        undo = context.preferences.edit.use_global_undo
        bpy.context.preferences.edit.use_global_undo = False
        # Make sure we are in face select mode (save current select_mode)
        select_mode = bpy.context.tool_settings.mesh_select_mode[:]
        bpy.context.tool_settings.mesh_select_mode = [False, False, True]

        # Get the indexes of all seleted faces
        self.refresh()
        indexes = [p.index for p in o.data.polygons if p.select]
        for i in indexes:
            bpy.ops.mesh.select_all(action='DESELECT')
            self.selectPolys(o, [i])
            bpy.ops.mesh.inset(
                use_boundary=True, use_even_offset=True,
                use_relative_offset=False, thickness=self.thickness, depth=0,
                use_outset=False, use_select_inset=True
            )
        bpy.ops.mesh.select_all(action='DESELECT')
        self.selectPolys(o, indexes)

        # cleaning up, restoring all old setting
        bpy.context.tool_settings.mesh_select_mode = select_mode
        bpy.context.preferences.edit.use_global_undo = undo
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}


bpy.utils.register_class(SCENE_OT_insetSelected)

################################
# SELECTION OPERATORS
################################


class SCENE_OT_selectObjects(bpy.types.Operator):
    '''Select Objects based upon criteria'''
    bl_idname = "scene.select_objects"
    bl_label = "Select Objects By:"
    bl_options = {'REGISTER', 'UNDO'}

    items_list = make_tuples(
        ["None", "Construction", "Type", "Zone", "No Faces"])
    method: bpy.props.EnumProperty(
        name="method", default="None", items=items_list, description="Select Objects of Same:")

    def draw(self, context):
        layout = self.layout
        layout.row().label(text='Objects of Same:')
        layout.row().prop(self, 'method', text="")

    def execute(self, context):
        o = context.active_object
        if o is None:
            return {'FINISHED'}

        if self.method == "Construction":
            selectUtils.selectObjectsOfSameConstruction(o)

        if self.method == "Type":
            if hasattr(bpy.context.scene, 'ODS_EP'):
                selectUtils.selectObjectsOfSameType(o)
            else:
                self.report({'ERROR'}, 'Requires the EnergyPlus Module')
                return {'FINISHED'}

        if self.method == "Zone":
            if hasattr(bpy.context.scene, 'ODS_EP'):
                selectUtils.selectObjectsOfZone(o)
            else:
                self.report({'ERROR'}, 'Requires the EnergyPlus Module')
                return {'FINISHED'}

        if self.method == "No Faces":
            sc = bpy.context.scene
            # Deselect all objects in the scene
            for ob in sc.objects:
                if ob.type == 'MESH':
                    if len(ob.data.polygons) == 0:
                        ob.select = True
                    else:
                        ob.select = False
        return {'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}


bpy.utils.register_class(SCENE_OT_selectObjects)
