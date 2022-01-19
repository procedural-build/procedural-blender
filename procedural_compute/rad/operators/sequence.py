###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2021, ods-engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################


import bpy
from procedural_compute.core.utils.threads import queue_fun
from procedural_compute.rad.utils.radiancescene import RadianceScene


class SCENE_OT_radanimation(bpy.types.Operator):
    bl_label = "Radiance Animation"
    bl_idname = "scene.radanimation"
    bl_description = "Radiance Animation"

    def execute(self, context):
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

    def writeAnimationFiles(self, context):
        print("Writing Radiance Files for Current Day Animation...")
        sc = bpy.context.scene
        # Back up the current frame position
        orgFrame = sc.frame_current
        # Do the sequence export
        RadianceScene().exportStaticObjects(name="%s.rad"%(sc.name))
        text = ""
        for frame in range(sc.frame_start, sc.frame_end+1, sc.RAD.Sequence.sequstep):
            sc.frame_set(frame)
            (hour, minute) = frameToTime(frame)
            text += RadianceScene().exportFrame(hour, minute, writeStaticData=False)
        # Write the bash script for processing the animation
        RadianceScene().createFile(bpy.path.abspath("%s/animation.sh"%(sc.RAD.caseDir)),text)
        # Restore the original frame position
        sc.frame_current = orgFrame
        print("Done")
        return{'FINISHED'}

    def executeAnimScript(self, context):
        sc = bpy.context.scene
        commands = bpy.path.abspath("%s/animation.sh"%(sc.RAD.caseDir))
        if not os.path.exists(commands):
            self.report({'ERROR'},'Could not find render commands.\\Have you exported the animation case files first?')
            return{'FINISHED'}
        # Open the list of commands to execute for the sequence and run them
        f = open(commands,'r')
        for cmd in f.readlines():
            queue_fun("rpict", waitSTDOUT, (cmd, caseDir()))
        f.close()
        return{'FINISHED'}


bpy.utils.register_class(SCENE_OT_radanimation)
