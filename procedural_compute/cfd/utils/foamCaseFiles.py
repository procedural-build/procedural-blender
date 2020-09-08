###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.cfd.utils import foamUtils
from math import *

class changeDictionaryDict(foamUtils.genericFoamFile):
    filepath = 'system/changeDictionaryDict'

    def writeHeaderAndClose(self,mode='w'):
        self.openFile()
        self.writeHeader()
        self.writeString("dictionaryReplacement\n{\n")
        self.closeFile()

    def writeFooter(self):
        self.writeAppendString("}\n")
        self.closeFile()

    def boundaryPatchType(self,patch,newPatchType):
        self.writeAppendString("    boundary\n    {\n        %s\n        {\n            type    %s;\n        }\n    }\n"%(patch, newPatchType))

    def defaultWallPatch(self,bcList,name):
        self.openFile(mode='a')
        nobj = bpy.data.objects.new(name,bpy.data.meshes.new(name))
        # Direct the BC write instances to the change Dictionary output
        # and write the dummy bc contents to each (wrapping it in some
        # the name of the BC and some curly braces
        for bc in bcList:
            bc.f = self.f
            self.f.write("    %s\n    {\n        boundaryField\n        {\n"%(bc.fieldObjName))
            bc.write(nobj)
            self.f.write("        }\n    }\n")
        # Remove the dummy object
        bpy.data.objects.remove(nobj)
        self.closeFile()


class createCyclicMatchingPatchDict(foamUtils.genericFoamFile):
    filepath = 'system/createCyclicMatchingPatchDict'

    def writeHeaderAndClose(self,mode='w'):
        self.openFile()
        self.writeHeader()
        self.writeString("matchTolerance 1E-2;\npointSync true;\n// Patches to create.\npatchInfo\n(")
        self.closeFile()

    def writeFooter(self):
        self.writeAppendString(");\n")
        self.closeFile()

    def addCyclicPatch(self,patchName,Vn):
        self.writeAppendString("""
    {{
        // Name of patch for making cyclic
        name {0};

        // Normal vector
        normVec ( {1} {2} {3} );

        // Patch in which to put potential non-planar faces
        nonPlanarPatch nonPlanarFanFaces;
    }}
""".format(patchName,Vn[0],Vn[1],Vn[2]))

class nonPlanarFanFacesSetSet(foamUtils.emptyFile):
    filepath = 'nonPlanarFanFaces.setSet'
    def writeBody(self):
        f = self.f
        f.write("faceSet nonPlanarFanFaces new labelToFace (1 1 1)\n")
        f.write("faceSet nonPlanarFanFaces clear\n")
        for o in bpy.context.selected_objects:
            if o.ODS_CFD.patchType == 'fan':
                globalNorm = o.matrix_world.to_3x3() * o.data.polygons[0].normal
                patchName = foamUtils.formatObjectName(o.name)
                f.write("faceSet currentFan new patchToFace " + patchName + "\n")
                f.write("faceSet currentFan delete normalToFace (%f %f %f) 0.001\n"%(globalNorm[0], globalNorm[1], globalNorm[2]))
                f.write("faceSet currentFan delete normalToFace (%f %f %f) 0.001\n"%(-1*globalNorm[0], -1*globalNorm[1], -1*globalNorm[2]))
                f.write("faceSet nonPlanarFanFaces add faceToFace currentFan\n")
                f.write("faceSet currentFan clear\n")

class porousZones(foamUtils.genericFoamFile):
    filepath = 'constant/porousZones'
    def writeBody(self):
        f=self.f
        # Get the number of porous zones
        cc = 0
        for obj in bpy.context.selected_objects:
            if obj.ODS_CFD.porous_isPorous:
                cc += 1
        # Write the number of porous zones header
        f.write("%i\n("%cc)

        # Write porousZone information
        for obj in bpy.context.selected_objects:
            if obj.ODS_CFD.porous_isPorous:
                zoneName = foamUtils.formatObjectName(obj.name)
                # Get axis orientation
                xa = obj.data.vertices[0].co.copy()
                za = obj.data.vertices[0].co.copy()
                xa[0]=1.0;xa[1]=0.0;xa[2]=0.0
                za[0]=0.0;za[1]=0.0;za[2]=1.0
                xa = obj.matrix_world.to_3x3()*xa
                xa.normalize()
                za = obj.matrix_world.to_3x3()*za
                za.normalize()
                # Get coefficients
                dc = obj.ODS_CFD.porous_Dcoeff
                fc = obj.ODS_CFD.porous_Fcoeff
                f.write("""
    {0}
    {{
        coordinateSystem
        {{
            e1  ( {1} {2} {3} );
            e2  ( {4} {5} {6} );
        }}

        Darcy
        {{
            d   d [0 -2 0 0 0 0 0] ( {7} {8} {9} );
            f   f [0 -1 0 0 0 0 0] ( {10} {11} {12} );
        }}
    }}
""".format(zoneName,xa[0],xa[1],xa[2],za[0],za[1],za[2],dc[0],dc[1],dc[2],fc[0],fc[1],fc[2]))

class decomposeParDict(foamUtils.genericFoamFile):
    filepath = 'system/decomposeParDict'
    def writeBody(self):
        sc = bpy.context.scene
        bpy.ops.scene.getnumsubdomains()
        s = sc.ODS_CFD.system
        if s.numSubdomains < 1:
            s.numSubdomains = 1
        self.f.write("""
numberOfSubdomains  {0};

method              {1};

simpleCoeffs
{{
    n               ({2} {3} {4});
    delta           {5};
}}

hierarchicalCoeffs
{{
    n               ({2} {3} {4});
    delta           {5};
    order           {6};
}}
""".format(s.numSubdomains, s.decompMethod, s.decompN[0], s.decompN[1], s.decompN[2], s.decompDelta, s.decompOrder))

class gravity(foamUtils.genericFoamFile):
    filepath = 'constant/g'
    def writeBody(self):
        sc = bpy.context.scene
        self.f.write("""
dimensions      [0 1 -2 0 0 0 0];
value           ( {0} {1} {2} );
""".format(sc.gravity[0],sc.gravity[1],sc.gravity[2]))

class machines(foamUtils.emptyFile):
    filepath = 'system/machines'
    def writeBody(self):
        f = self.f
        lines = bpy.context.scene.ODS_CFD.system.machines.split(',')
        f.write('\n'.join(lines))

class dotFoam(foamUtils.emptyFile):
    filepath = 'case.foam'
    def writeBody(self):
        return

class porousCells(foamUtils.emptyFile):
    filepath = 'porousCells.setSet'
    def writeBody(self):
        f = self.f
        sc = bpy.context.scene
        if 'porous' in sc.ODS_CFD.solver.name:
            kp = bpy.data.objects['cfdMeshKeepPoint']
            for o in bpy.context.selected_objects:
                if o.ODS_CFD.porous_isPorous:
                    zoneName = foamUtils.formatObjectName(o.name)
                    f.write("cellSet %s new surfaceToCell \"%s.stl\" 1((%f %f %f)) true true false -1  -100\n"%(zoneName, zoneName, kp.location[0], kp.location[1], kp.location[2]))
