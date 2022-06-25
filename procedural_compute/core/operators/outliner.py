###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy

import logging
logger = logging.getLogger(__name__)

################################
# OBJECT DISPLAY PROPERTIES
################################


class OutlinerGeneralOperator(bpy.types.Operator):
    """ """
    bl_label = "General Outliner Operator"
    bl_idname = "outliner.general_operator"
    bl_description = "General Outliner Operator"

    command: bpy.props.StringProperty(
        name="Command", description="Command string", default="")

    @classmethod
    def poll(cls, context):
       return context.area.type == 'OUTLINER'

    def execute(self, context):
        if hasattr(self, self.command):
            logger.info(
                f"\n\n###### EXECUTING OUTINER OPERATION: {self.command} ######\n")
            getattr(self, self.command)(context)
        else:
            logger.info(
                f"{self.command} command not found in bpy.ops.outliner.general_operator")
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}

    def hide_selected(self, context):
        for obj in bpy.context.selected_objects:
            obj.hide_set(True)

    def unhide_selected(self, context):
        #logger.info(f"Unhiding objects: {context.selected_ids}")
        for obj in context.selected_ids:
            obj.hide_set(False)

    def show_only_selected(self, context):
        collection = bpy.context.collection
        #logger.info(f"Showing only: {context.selected_ids} from collection: {collection.name}")
        selected = [o for o in context.selected_ids]
        for obj in collection.objects:
            obj.hide_set(True)
        for obj in selected:
            obj.hide_set(False)

# Register and add to the object menu (required to also use F3 search "Custom Draw Operator" for quick access).


def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(OutlinerGeneralOperator.bl_idname,
                         text="Hide selected", icon='HIDE_ON').command = "hide_selected"
    self.layout.operator(OutlinerGeneralOperator.bl_idname,
                         text="Unhide selected", icon='HIDE_OFF').command = "unhide_selected"
    self.layout.operator(OutlinerGeneralOperator.bl_idname,
                         text="Show only selected", icon='HIDE_ON').command = "show_only_selected"


bpy.utils.register_class(OutlinerGeneralOperator)
bpy.types.OUTLINER_MT_object.append(menu_func)
