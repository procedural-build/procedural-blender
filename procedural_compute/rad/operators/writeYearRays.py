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
from procedural_compute.sun.utils.timeFrameSync import frameToTime, getTimeStamp
from procedural_compute.sun.utils.suncalcs import Solar_Pos

from math import degrees, radians, sin, cos, tan


def caseDir():
    return bpy.path.abspath(bpy.context.scene.RAD.caseDir)


class SCENE_OT_writeYearRays(bpy.types.Operator):
    bl_label = "Calc Annual Solar Exposure"
    bl_idname = "scene.calcrays"
    bl_description = "Calc Annual Solar Exposure"

    def execute(self, context):
        self.writeYearRays()
        self.calcYearRays()
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

    def getFilename(self,s):
        sc = bpy.context.scene
        return bpy.path.abspath("%s/%s"%(sc.RAD.caseDir, s))

    def calcYearRays(self):
        sc = bpy.context.scene
        (nDays, nFrames) = self.writeYearRays()
        for o in bpy.context.selected_objects:
            timestamp = getTimeStamp()
            if not 'Windows' in bpy.app.build_platform.decode():
                cmd = "cat yearRays | rcalc -e '$1=%f' -e '$2=%f' -e '$3=%f' -e '$4=$1' -e '$5=$2' -e '$6=$3'"%(o.location[0],o.location[1],o.location[2])
            else:
                cmd = "cat yearRays | rcalc -e \"$1=%f\" -e \"$2=%f\" -e \"$3=%f\" -e \"$4=$1\" -e \"$5=$2\" -e \"$6=$3\""%(o.location[0],o.location[1],o.location[2])
            cmd += " | rtrace -ab 0 -h+ -ov -fac -x %u -y %u octrees/%s.oct "%(nFrames,nDays,timestamp)
            cmd += " | pfilt -h 20 -n 0 -p 1 -r 1 > images/yearTrace_temp.hdr "
            cmd += " && protate images/yearTrace_temp.hdr images/yearTrace_%s.hdr && rm -v images/yearTrace_temp.hdr"%(o.name)
            threads.queue_fun("rtrace", waitSTDOUT, (cmd, caseDir()))
        return

    def writeYearRays(self):
        sc = bpy.context.scene
        b = sc.ODS_SUN

        f = open( self.getFilename('yearRays'), 'w')

        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        nDays = 0
        for month in months:
            for day in range(days[month-1]):
                nDays += 1
                nFrames = 0
                for frame in range(1, (24*b.solarDT)+1):
                    (hour, minute) = frameToTime(frame)
                    (az,el) = Solar_Pos(sc.Site.longitude, sc.Site.latitude, sc.Site.timezone, month, day, hour, minute)
                    az = az + degrees(sc.Site.northAxis)
                    if el <= 0.1:
                        x=0.0;y=0.0;z=-1.0;
                    elif el >= 89.9:
                        x=0.0;y=0.0;z=1.0;
                    else:
                        x = sin(radians(az))
                        y = cos(radians(az))
                        z = tan(radians(el))
                    f.write( "%f %f %f\n"%(x, y, z) )
                    nFrames += 1
        f.close()
        return (nDays, nFrames)

bpy.utils.register_class(SCENE_OT_writeYearRays)
