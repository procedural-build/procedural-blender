###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.rad.utils.exportbase import ExportBase

class MaterialContext(ExportBase):

    def __init__(self):
        ## matrix for sRGB color space transformation
        ## TODO: Apple RGB?
        red     = [0.412424, 0.212656, 0.0193324]
        green   = [0.357579, 0.715158,  0.119193]
        blue    = [0.180464, 0.0721856, 0.950444]
        self.matrix = [red,green,blue]
        return None
    
    def export(self, materialsList, filename=''):
        # Write the default material to start with
        text = "## materials.rad\n"
        text += self.getMaterialDescription(None)
        # Write blender materials that were assigned to objects
        for matName in materialsList:
            mat = bpy.data.materials[matName]
            text += self.getMaterialDescription(mat)

        if filename == '':
            filename = self.getFilename("materials.rad")
        self.createFile(filename, text)

    def getMaterialDescription(self,material):
        if material == None:
            text = self.defaultMaterialText()
        else:
            text = material.procedural_compute.rad.textRAD()
        return text

    def defaultMaterialText(self):
        s  = "\n## default material"
        s += "\nvoid plastic ods_default_material"
        s += "\n0\n0\n5 0.8 0.8 0.8 0 0\n"

        s += "\n## default glow material for stencils"
        s += "\nvoid glow stencil_glow"
        s += "\n0\n0\n4 1 1 1 0\n"
        return s
