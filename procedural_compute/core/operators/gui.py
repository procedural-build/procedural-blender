###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

import inspect
import bl_ui

################################
# GUI OPERATORS
################################


class skinInterface(bpy.types.Operator):
    bl_label = "Toggle Skin Interface"
    bl_idname = "scene.skin_interface"
    bl_description = "Skin the Blender Interface"

    command: bpy.props.StringProperty(name="Command", description="parse String", default="")

    def execute(self, context):

        def isException(string):
            exceptions = [
                "onion", "context_object", "context_material",
                "MATERIAL_PT_preview", "MATERIAL_PT_diffuse", "MATERIAL_PT_transp",
                "VIEW3D_PT_tools_objectmode", "VIEW3D_PT_tools_meshedit"
            ]
            for e in exceptions:
                if e in string:
                    return True
            return False

        print("Toggling registration of GUI Panel classes")
        modules = inspect.getmembers(bl_ui)
        for moduleInfo in modules:
            if "properties_" in moduleInfo[0] or moduleInfo[0] == "space_view3d":
                module = getattr(bl_ui, moduleInfo[0])
                classes = inspect.getmembers(module)
                for classInfo in classes:
                    if "_PT_" in classInfo[0] and not isException(classInfo[0]):
                        c = getattr(module, classInfo[0])

                        # Class is not registerable if it does not have a 'bl_rna' attribute
                        if not hasattr(c, 'bl_rna'):
                            continue

                        if hasattr(bpy.types, classInfo[0]):
                            #print("Unregistering class: %s, from module: %s"%(classInfo[0], moduleInfo[0]))
                            bpy.utils.unregister_class(c)
                        else:
                            #print("Registering class: %s, from module: %s"%(classInfo[0], moduleInfo[0]))
                            bpy.utils.register_class(c)

        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}


bpy.utils.register_class(skinInterface)
