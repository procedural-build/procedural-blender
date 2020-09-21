###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
import os
from math import degrees

from procedural_compute.sun.utils.suncalcs import Solar_Pos
from procedural_compute.rad.utils.exportbase import ExportBase
from procedural_compute.rad.utils.material import MaterialContext

class RadianceSky(ExportBase):
   
    def export(self, hour, minute, name):
        sc = bpy.context.scene
        b = sc.ODS_SUN
        (az,el) = Solar_Pos(sc.Site.longitude, sc.Site.latitude, sc.Site.timezone, b.month, b.day, hour, minute)
        az = az + degrees(sc.Site.northAxis)
        text = "!gensky -ang %.3f %.3f "%(el, az+180.0)

        text += " %s -g 0.2 -t 1.7\n"%(sc.RAD.skytype)
        text += "skyfunc glow skyglow\n0\n0\n4 0.9 0.9 1.15 0\n"
        text += "skyglow source sky\n0\n0\n4 0 0 1 180\n\n"
        text += "skyfunc glow groundglow\n0\n0\n4 1.4 0.9 0.6 0\n"
        text += "groundglow source ground\n0\n0\n4 0 0 -1 180\n"

        filename = self.getFilename("skies/%s.sky"%name)
        self.createFile(filename, text)
        return "./skies/%s.sky"%name

