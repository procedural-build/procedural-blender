###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2021, ods-engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################

import bpy
import glob
import os
import threading
from procedural_compute.core.utils.threads import queue_fun
from procedural_compute.core.utils.subprocesses import waitOUTPUT
from procedural_compute.rad.operators.ops import getTimeStamp


class SCENE_OT_batchstats(bpy.types.Operator):
    bl_label = "Batch Process"
    bl_idname = "scene.batchstats"
    bl_description = "Calculate statics for all images"

    def getFilename(self,s):
        sc = bpy.context.scene
        return bpy.path.abspath("%s/%s"%(sc.RAD.caseDir, s))

    @staticmethod
    def fileStats(filepath, mult, lim, out):
        def clean_cmd(cmd):
            if 'Windows' in bpy.app.build_platform.decode():
                cmd = cmd.replace("'","\"")
            return cmd
        (path, filename) = os.path.split(filepath)
        print("Getting statistics for: %s"%filename)
        NP = int(waitOUTPUT(clean_cmd("getinfo -d %s | rcalc -e '$1=$3*$5'"%filename), cwd=path)[0].decode())
        NPZ = int(waitOUTPUT(clean_cmd("pvalue -h -H -o %s | rcalc -e '$1=($3*0.265+$4*0.67+$5*0.065)*179' | rcalc -e '$1=if($1,1,0)' | total"%filename), cwd=path)[0].decode())
        AV = float(waitOUTPUT(clean_cmd("pvalue -h -H -o %s | rcalc -e '$1=($3*0.265+$4*0.67+$5*0.065)*'%f | total -m"%(filename, mult)), cwd=path)[0].decode())
        NPLIM = int(waitOUTPUT(clean_cmd("pvalue -h -H -o %s | rcalc -e '$1=($3*0.265+$4*0.67+$5*0.065)*'%f | rcalc -e '$1=if($1-%f,1,0)' | total"%(filename, mult, lim)), cwd=path)[0].decode())
        AVZ = float(AV*NP/NPZ)
        ALIM= float(NPLIM/NPZ)
        # Append the results to the output file
        lock = threading.Lock()
        lock.acquire()
        f = open(out, 'a')
        f.write("%s,%i,%i,%f,%f\n"%(filename,NP,NPZ,AVZ,ALIM))
        f.close()
        lock.release()
        print("Done")
        return None

    def batchStats(self):
        p = bpy.context.scene.RAD.falsecolor
        cdir = bpy.path.abspath(bpy.context.scene.RAD.caseDir)
        ts = getTimeStamp()
        outFile = "%s/images/Stats-%s.csv"%(cdir,ts)
        files = glob.glob('%s/images/*%s.hdr'%(cdir, ts))
        f=open(outFile,'w');f.write("");f.close()
        for f in files:
            #self.fileStats(f, p.mult, p.limit, outFile)
            queue_fun("rtrace", self.fileStats, (f, p.mult, p.limit, outFile) )
        return None

    def execute(self, context):
        self.batchStats()
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

bpy.utils.register_class(SCENE_OT_batchstats)
