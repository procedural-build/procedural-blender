###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

class getNumSubdomains(bpy.types.Operator):
    bl_label = "Get No. Subdomains"
    bl_idname = "scene.getnumsubdomains"
    bl_description = "Get the Number of sub-domains"

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

    def execute(self, context):
        sc = context.scene
        sc.ODS_CFD.system.numSubdomains = max(sc.ODS_CFD.system.decompN[0]*sc.ODS_CFD.system.decompN[1]*sc.ODS_CFD.system.decompN[2],1)
        return{'FINISHED'}
bpy.utils.register_class(getNumSubdomains)

#--------------

