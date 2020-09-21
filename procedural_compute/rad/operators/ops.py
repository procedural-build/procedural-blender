###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
import os
import glob
import threading

from procedural_compute.core.utils.threads import queue_fun
from procedural_compute.core.utils.subprocesses import waitSTDOUT, waitOUTPUT

from procedural_compute.rad.utils.radiancescene import RadianceScene
from procedural_compute.sun.utils.timeFrameSync import getTimeStamp
from procedural_compute.sun.utils.timeFrameSync import frameToTime

from math import degrees, radians, sin, cos, tan
from procedural_compute.sun.utils.suncalcs import Solar_Pos

from math import floor


def caseDir():
    return bpy.path.abspath(bpy.context.scene.RAD.caseDir)


def getOutsideAmb(skyfile=None):
    sc = bpy.context.scene
    b = sc.ODS
    # Get the name of the current skyfile
    if skyfile==None:
        skyfile = "skies/%s.sky"%(getTimeStamp())

    abspath = "%s/%s"%(caseDir(),skyfile)
    if not os.path.exists(abspath):
        return 0

    # Get outside ground ambient level (from gensky command)
    (out,err) = waitOUTPUT("xform -e ./%s"%(skyfile), cwd=caseDir())

    # Process the output to get what we need
    out = out.decode("utf-8")
    i = out.find("Ground ambient level:")
    out = out[(i+21):]
    i = out.find("\n")
    out = out[:i].replace(' ','')

    extamb = float(out)
    print("FOUND GROUND AMBIENT LEVEL = %f"%(extamb))
    return extamb


# GENERIC RADIANCE OPERATORS
class SCENE_OT_radianceOps(bpy.types.Operator):
    bl_label = "Radiance Operations"
    bl_idname = "scene.radianceops"
    bl_description = "Generic Radiance Operations"

    command: bpy.props.StringProperty(name="Command", description="parse String", default="")

    def execute(self, context):
        if hasattr(self,self.command):
            getattr(self, self.command)()
        else:
            print(self.command + ": Attribute not found!")
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

    def writeRadianceFiles(self):
        print("Writing Radiance Files for Current Frame...")
        sc = bpy.context.scene
        frame  = sc.frame_current
        (hour, minute) = frameToTime(frame)
        RadianceScene().exportFrame(hour, minute)
        print("Done")
        return{'FINISHED'}

    def executeRifFile(self):
        sc = bpy.context.scene
        cmd = "rad -N %i %s.rif"%(sc.RAD.nproc, getTimeStamp())
        queue_fun("rpict", waitSTDOUT, (cmd, caseDir()))
        getOutsideAmb()
        return{'FINISHED'}

    def genOctree(self):
        ts = getTimeStamp()
        cmd = "oconv %s.rad > octrees/%s.oct"%(ts, ts)
        queue_fun("rtrace", waitSTDOUT, (cmd, caseDir()))

    def getFilename(self,s):
        return "%s/%s"%(caseDir(),s)

    def createDir(self,dirpath):
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        return None


bpy.utils.register_class(SCENE_OT_radianceOps)
