###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ods-engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################

import bpy

from procedural_compute.core.utils.threads import queue_fun
from procedural_compute.core.utils.subprocesses import waitSTDOUT, waitOUTPUT

from procedural_compute.rad.utils.radiancescene import RadianceScene
from procedural_compute.rad.operators.ops import getTimeStamp


def caseDir():
    return bpy.path.abspath(bpy.context.scene.RAD.caseDir)


class SCENE_OT_rtracestencils(bpy.types.Operator):
    bl_label = "rtrace stencils"
    bl_idname = "scene.rtracestencils"
    bl_description = "Calc illum across stencils"

    def execute(self, context):
        obs = bpy.context.selected_objects
        # First check if all objects are flat
        for o in obs:
            if not self.isFlat(o):
                self.report({'ERROR'},'Not all stencils are flat')
                return {'FINISHED'}
        self.writeStencils()
        self.oconvStensils()
        self.rtraceStencils()
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

    def getFilename(self,s):
        sc = bpy.context.scene
        return bpy.path.abspath("%s/%s"%(sc.RAD.caseDir, s))

    def writeStencils(self):
        RadianceScene().exportSelectedObjects(skipNone=False)
        for o in bpy.context.selected_objects:
            text  = "!xform ./materials.rad\n"
            text += "!xform -n %s -m stencil_glow ./objects/%s.rad\n"%(o.name,o.name)
            # Write the file and write text
            filename = self.getFilename('stencils/%s.rad'%(o.name))
            f = open(filename, 'w')
            f.write(text)
            f.close()
        return

    def oconvStensils(self):
        for o in bpy.context.selected_objects:
            cmd = "oconv stencils/%s.rad > stencils/%s.oct"%(o.name, o.name)
            queue_fun("rtrace", waitSTDOUT, (cmd, caseDir()))
        return

    def vertXY(self, o):
        M = o.matrix_world
        X = [(M*v.co)[0] for v in o.data.vertices]
        Y = [(M*v.co)[1] for v in o.data.vertices]
        return (X, Y)

    def getDimRes(self, o):
        (x, y) = self.vertXY(o)
        sc = bpy.context.scene
        R = sc.RAD.Stencil.res
        X = max(x) - min(x)
        Y = max(y) - min(y)
        if X >= Y:
            xres = int(R)
            yres = int(R*Y/X)
        else:
            xres = int(R*X/Y)
            yres = int(R)
        return (min(x), min(y), max(x), max(y), xres, yres)

    def isFlat(self, o):
        M = o.matrix_world
        z0 = (M*o.data.vertices[0].co)[2]
        for v in o.data.vertices:
            if abs((M*v.co)[2] - z0) > 0.001:
                return False
        return True

    def rtraceStencils(self):
        # Now do the calculation
        b = bpy.context.scene.RAD.Stencil
        s = bpy.context.scene.RAD
        timestamp = getTimeStamp()
        for o in bpy.context.selected_objects:
            (minX, minY, maxX, maxY, xres, yres) = self.getDimRes(o)
            XC = (minX+maxX)/2.0
            YC = (minY+maxY)/2.0
            X = maxX-minX
            Y = maxY-minY
            Zvec = (o.matrix_world.to_3x3()*o.data.polygons[0].normal).normalized()
            Zo = (o.matrix_world*o.data.vertices[0].co)
            Z = (Zo + Zvec)[2]

            # Get the arguments for the rtrace command
            rtargs =  " -ab %i -ad %i -as %i -aa %f -av .0 .0 .0 "%(b.ambB, b.ambD, b.ambS, b.ambA)
            if not 'Windows' in bpy.app.build_platform.decode():
                rtargs  = " -n %i"%(s.nproc) + rtargs
                rtargs += " -ar `getinfo -d<octrees/%s.oct|rcalc -e '$1=floor(16*$4/(%f+%f))'`"%(timestamp,X,Y)
            else:
                octDir = bpy.path.abspath("%s/octrees/%s.oct"%(caseDir(),timestamp))
                (AR,err) = waitOUTPUT("getinfo -d<%s|rcalc -e \"$1=floor(16*$4/(%f+%f))\""%(octDir,X,Y),cwd=caseDir())
                rtargs += " -ar %i"%(int(AR))

            # Generate a rectangular grid of rays over the stencil limits
            cmd  = "cnt %u %u"%(yres, xres)
            cmd += " | rcalc -e '$1=%f + ($2-(%u/2)+0.5)*(%f)' "%(XC, xres, X/xres)
            cmd += " -e '$2=%f - ($1-(%u/2)+0.5)*(%f)' "%(YC, yres, Y/yres)
            cmd += " -e '$3=%f' -e '$4=0;$5=0;$6=%f' "%(Z, -1*Zvec[2])
            # raytrace upwards to the stencil area
            cmd += " | rtrace -w -h -opv  stencils/%s.oct "%(o.name)
            cmd += " | rcalc -e '$1=$1;$2=$2;$3=$3;$4=0;$5=0;$6=if($6-0.5,1,0)' "
            cmd += " | rtrace %s -h+ -I+ -ov octrees/%s.oct "%(rtargs, timestamp)
            cmd += " | pvalue -r -x %u -y %u "%(yres, xres)
            cmd += " | pfilt -h 20 -p 1 > images/dftrace_%s_%s.hdr"%(o.name, timestamp)

            if 'Windows' in bpy.app.build_platform.decode():
                cmd = cmd.replace("'","\"")

            queue_fun("rtrace", waitSTDOUT, (cmd, caseDir()))
        return None

bpy.utils.register_class(SCENE_OT_rtracestencils)
