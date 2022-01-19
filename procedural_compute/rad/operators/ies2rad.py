###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2021, ods-engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################


import bpy
import os

class SCENE_OT_ies2rad(bpy.types.Operator):
    bl_label = "IES to RAD"
    bl_idname = "scene.ies2rad"
    bl_description = "Convert IES Lighting Descriptions to Radiance"

    def execute(self, context):
        self.ies2rad()
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

    def createDir(self,dirpath):
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        return None

    def ies2rad(self):
        sc = bpy.context.scene

        caseDir = bpy.path.abspath(bpy.context.scene.RAD.caseDir)
        dirpath = "%s/lights/"%(caseDir)
        self.createDir(dirpath)

        # Exectute ies2rad command for each light and put results in ies2rad directory
        for light in sc.RAD.Light.iesLights:
            fname = light.iesFile
            color = "".join([str(c)+" " for c in light.color])
            # Convert relative to absolute
            fname = bpy.path.abspath(fname)
            # Execute ies2rad
            cmd = "ies2rad -t default -p lights/ -c %s -m %f -o %s %s" \
                   %(color, light.factor, light.name, fname)
            threads.queue_fun("rtrace", waitSTDOUT, (cmd, caseDir()))

bpy.utils.register_class(SCENE_OT_ies2rad)
