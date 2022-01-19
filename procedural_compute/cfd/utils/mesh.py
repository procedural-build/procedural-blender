###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.cfd.utils import foamUtils
from math import *


class blockMeshDict(foamUtils.genericFoamFile):
    filepath = 'constant/polyMesh/blockMeshDict'

    def writeBody(self):
        sc = bpy.context.scene
        if 'cfdBoundingBox' in bpy.data.objects.keys():
            ob = bpy.data.objects['cfdBoundingBox']
        else:
            print('ERROR: ', 'No bounding box found.  Please add a CFD bounding box for simulation.')
            return None
        f = self.f
        f.write("\nconvertToMeters 1;\n\nvertices        \n(\n")
        if len(ob.data.vertices) != 8:
            error('Incorrect number of vertices on CFD Bounding Box')
        o = [2, 1, 0, 3, 6, 5, 4, 7]
        v = []
        for i in range(len(ob.data.vertices)):
            v.append(ob.matrix_world @ ob.data.vertices[o[i]].co)
        for i in range(len(v)):
            f.write("(" + str(v[i][0]) + " " + str(v[i][1]) + " " + str(v[i][2]) + ")\n")

        f.write(");\n")
        f.write("\nblocks\n(\n    hex (0 1 2 3 4 5 6 7) ")
        ds = sc.Compute.CFD.mesh.blockMeshSize
        f.write("(%i %i %i)"%(int(round(abs(v[0][0]-v[1][0])/ds)), int(round(abs(v[1][1]-v[2][1])/ds)), int(round(abs(v[4][2]-v[0][2])/ds))))
        f.write(" simpleGrading (1 1 1)\n);\n\n")
        f.write("edges ();\n\n")
        f.write("patches\n(\n")

        patchNames = ['MaxY', 'MinY', 'MinX', 'MaxX', 'MinZ', 'MaxZ']
        patchVerts = ['(3 7 6 2)', '(1 5 4 0)', '(0 4 7 3)', '(2 6 5 1)', '(0 3 2 1)', '(4 5 6 7)']
        for i in range(6):
            o = bpy.data.objects[patchNames[i]]
            if 'symmetry' in o.Compute.CFD.preset:
                patchType = 'symmetryPlane'
            else:
                patchType = 'wall'
            f.write("%s %s ( %s  )\n"%(patchType, patchNames[i], patchVerts[i]))
        f.write(");\n\n")
        f.write("mergePatchPairs ();\n")

        return None


class snappyHexMeshDict(foamUtils.genericFoamFile):
    filepath = 'system/snappyHexMeshDict'
    
    def writeBody(self):
        specialNames = ['cfdBoundingBox','cfdMeshKeepPoint','MinX','MaxX','MinY','MaxY','MinZ','MaxZ']
        sc = bpy.context.scene
        obs = bpy.context.selected_objects
        f = self.f
        m = sc.Compute.CFD.mesh

        # Which of the steps to run
        self.writeString("castellatedMesh %s;\n"%(str.lower(str(m.castellated))))
        self.writeString("snap %s;\n"%(str.lower(str(m.snap))))
        self.writeString("addLayers %s;\n"%(str.lower(str(m.addLayers))))

        # Geometry. Definition of all surfaces.
        self.writeString("\ngeometry\n{\n")
        self.writeString("cfdGeom.stl\n", indent=4)
        self.writeString("{\n", indent=4)
        self.writeString("type triSurfaceMesh;\n", indent=8)
        self.writeString("name cfdGeom;\n", indent=8)
        self.writeString("regions\n", indent=8)
        self.writeString("{\n", indent=8)
        for o in obs:
            obname = foamUtils.formatObjectName(o.name)
            if (o.type == 'MESH'):
                if (len(o.data.polygons) > 0) and (not obname in specialNames) and o.Compute.CFD.doMesh and (not o.Compute.CFD.porous_isPorous) and (not o.Compute.CFD.mesh.makeRefinementRegion):
                    self.writeString("%s { name %s ; }\n"%(obname,obname), indent=12)
        self.writeString("}\n", indent=8)
        self.writeString("}\n", indent=4)

        # Write Refinement Region Objects
        for o in obs:
            obname = foamUtils.formatObjectName(o.name)
            if (o.type == 'MESH'):
                if (len(o.data.polygons) > 0) and (not obname in specialNames) and o.Compute.CFD.mesh.makeRefinementRegion:
                    self.writeString("%s.stl\n"%(obname), indent=4)
                    self.writeString("{\n", indent=4)
                    self.writeString("type triSurfaceMesh;\n", indent=8)
                    self.writeString("name %s;\n"%(obname), indent=8)
                    self.writeString("}\n", indent=4)

        self.writeString("};\n")

        #------------------
        # castellatedMeshControls
        self.writeString("castellatedMeshControls\n{\n")
        self.writeString("maxLocalCells        "+str(m.maxLocalCells),indent=4,endl=";\n\n")
        self.writeString("maxGlobalCells       "+str(m.maxGlobalCells),indent=4,endl=";\n\n")
        self.writeString("minRefinementCells   "+str(m.minRefinementCells),indent=4,endl=";\n\n")
        self.writeString("nCellsBetweenLevels  "+str(m.nCellsBetweenLevels),indent=4,endl=";\n\n")
        if m.nFeatureSnapIter > 0:
            self.writeString("features ( { file \"cfdGeom.extendedFeatureEdgeMesh\"; level 0;  } )",indent=4,endl=";\n\n")
        else:
            self.writeString("features ( )",indent=4,endl=";\n\n")

        # Surface based refinement
        self.writeString("refinementSurfaces\n",indent=4)
        self.writeString("{\n", indent=4)
        self.writeString("cfdGeom\n", indent=8)
        self.writeString("{\n", indent=8)
        self.writeString("level (%i %i);\n"%(m.defaultLevel, m.defaultLevel), indent=12)
        self.writeString("regions\n", indent=12)
        self.writeString("{\n", indent=12)
        for o in obs:
            obname = foamUtils.formatObjectName(o.name)
            if (o.type == 'MESH'):
                if (len(o.data.polygons) > 0) and (not obname in specialNames) and o.Compute.CFD.doMesh and (not o.Compute.CFD.porous_isPorous) and (not o.Compute.CFD.mesh.makeRefinementRegion):
                    minLevel = o.Compute.CFD.mesh.meshMinLevel
                    maxLevel = o.Compute.CFD.mesh.meshMaxLevel
                    if maxLevel < minLevel:
                        maxLevel = minLevel
                    self.writeString("%s { level (%i %i) ; }\n"%(obname, minLevel, maxLevel ), indent=16)
        self.writeString("}\n", indent=12)
        self.writeString("}\n", indent=8)
        # Surface based refinement regions
        for o in obs:
            obname = foamUtils.formatObjectName(o.name)
            if (o.type == 'MESH'):
                if (len(o.data.polygons) > 0) and (not obname in specialNames) and o.Compute.CFD.mesh.makeRefinementRegion:
                    if o.Compute.CFD.mesh.refinementMode == "surface":
                        self.writeString("%s\n"%(obname), indent=8)
                        self.writeString("{\n", indent=8)
                        self.writeString("level %s;\n"%(o.Compute.CFD.mesh.distanceLevels), indent=12)
                        self.writeString("cellZone %s;\n"%(obname), indent=12)
                        self.writeString("faceZone %s_faces;\n"%(obname), indent=12)
                        self.writeString("}\n", indent=8)
        self.writeString("}\n\n", indent=4)

        # Resolve sharp angles
        self.writeString("resolveFeatureAngle %f;\n\n"%(degrees(m.resolveFeatureAngle)), indent=4)

        # Refinement regions
        self.writeString("refinementRegions {\n", indent=4)
        for o in obs:
            obname = foamUtils.formatObjectName(o.name)
            if (o.type == 'MESH'):
                if (len(o.data.polygons) > 0) and (not obname in specialNames) and o.Compute.CFD.mesh.makeRefinementRegion:
                    if not o.Compute.CFD.mesh.refinementMode == "surface":
                        self.writeString("%s\n"%(obname), indent=8)
                        self.writeString("{\n", indent=8)
                        self.writeString("mode %s;\n"%(o.Compute.CFD.mesh.refinementMode), indent=12)
                        self.writeString("levels %s;\n"%(o.Compute.CFD.mesh.distanceLevels), indent=12)
                        self.writeString("}\n", indent=8)
        self.writeString("};\n\n", indent=4)


        # Mesh selection
        kp = bpy.data.objects['cfdMeshKeepPoint']
        self.writeString("locationInMesh (%f %f %f);\n"%(kp.location[0],kp.location[1],kp.location[2]), indent=4)

        self.writeString("allowFreeStandingZoneFaces true;\n", indent=4)

        # Close castellatedMeshControls
        self.writeString("}\n\n")

        #------------------
        # snapControls
        self.writeString("snapControls\n{\n")
        self.writeString("nSmoothPatch              %i"%(m.nSmoothPatch),indent=4,endl=";\n\n")
        self.writeString("tolerance                 %f"%(m.tolerance),indent=4,endl=";\n\n")
        self.writeString("nSolveIter                %i"%(m.nSolveIter),indent=4,endl=";\n\n")
        self.writeString("nRelaxIter                %i"%(m.nRelaxIter),indent=4,endl=";\n\n")

        # Edge snap controls
        self.writeString("nFeatureSnapIter          %i"%(m.nFeatureSnapIter),indent=4,endl=";\n\n")
        self.writeString("implicitFeatureSnap       %s"%(str.lower(str(m.implicitFeatureSnap))),indent=4,endl=";\n\n")
        self.writeString("explicitFeatureSnap       %s"%(str.lower(str(m.explicitFeatureSnap))),indent=4,endl=";\n\n")
        self.writeString("multiRegionFeatureSnap    %s"%(str.lower(str(m.multiRegionFeatureSnap))),indent=4,endl=";\n\n")

        self.writeString("}\n\n")

        #------------------
        # addLayersControls
        self.writeString("addLayersControls\n{\n")
        self.writeString("relativeSizes         %s"%(str.lower(str(m.relativeSizes))),indent=4,endl=";\n\n")

        self.writeString("layers",indent=4,endl="\n")
        self.writeString("{",indent=4,endl="\n")
        for o in obs:
            obname = foamUtils.formatObjectName(o.name)
            if not obname in specialNames and o.type == 'MESH' and o.Compute.CFD.doMesh and (not o.Compute.CFD.porous_isPorous) and (not o.Compute.CFD.mesh.makeRefinementRegion):
                if o.Compute.CFD.mesh.nSurfaceLayers > 0:
                    self.writeString(obname + " { nSurfaceLayers " + str(o.Compute.CFD.mesh.nSurfaceLayers) + " ; }\n", indent=8)
        self.writeString("}",indent=4,endl=";\n\n")

        self.writeString("expansionRatio            "+str(m.expansionRatio),indent=4,endl=";\n\n")
        self.writeString("finalLayerThickness       "+str(m.finalLayerThickness),indent=4,endl=";\n\n")
        self.writeString("minThickness              "+str(m.minThickness),indent=4,endl=";\n\n")
        self.writeString("nGrow                     "+str(m.nGrow),indent=4,endl=";\n\n")

        # addLayersControls
        self.writeString("featureAngle              "+str(degrees(m.featureAngle)),indent=4,endl=";\n\n")
        self.writeString("nRelaxIter                "+str(m.nRelaxIterLayer),indent=4,endl=";\n\n")
        self.writeString("nSmoothSurfaceNormals     "+str(m.nSmoothSurfaceNormals),indent=4,endl=";\n\n")
        self.writeString("nSmoothNormals            "+str(m.nSmoothNormals),indent=4,endl=";\n\n")
        self.writeString("nSmoothThickness          "+str(m.nSmoothThickness),indent=4,endl=";\n\n")
        self.writeString("maxFaceThicknessRatio     "+str(m.maxFaceThicknessRatio),indent=4,endl=";\n\n")
        self.writeString("maxThicknessToMedialRatio "+str(m.maxThicknessToMedialRatio),indent=4,endl=";\n\n")
        self.writeString("minMedianAxisAngle        "+str(degrees(m.minMedianAxisAngle)),indent=4,endl=";\n\n")
        self.writeString("nBufferCellsNoExtrude     "+str(m.nBufferCellsNoExtrude),indent=4,endl=";\n\n")
        self.writeString("nLayerIter                "+str(m.nLayerIter),indent=4,endl=";\n\n")
        f.write("}\n\n")

        #------------------
        # Advanced Settings
        f.write("meshQualityControls\n{\n")
        self.writeString("maxNonOrtho 65",indent=4,endl=";\n\n")
        self.writeString("maxBoundarySkewness 20",indent=4,endl=";\n\n")
        self.writeString("maxInternalSkewness 4",indent=4,endl=";\n\n")
        self.writeString("maxConcave 80",indent=4,endl=";\n\n")
        self.writeString("minFlatness 0.5",indent=4,endl=";\n\n")
        self.writeString("minVol 1e-13",indent=4,endl=";\n\n")
        self.writeString("minTetQuality 1e-30",indent=4,endl=";\n\n")
        self.writeString("minArea -1",indent=4,endl=";\n\n")
        self.writeString("minTwist 0.05",indent=4,endl=";\n\n")
        self.writeString("minDeterminant 0.001",indent=4,endl=";\n\n")
        self.writeString("minFaceWeight 0.05",indent=4,endl=";\n\n")
        self.writeString("minVolRatio 0.01",indent=4,endl=";\n\n")
        self.writeString("minTriangleTwist -1",indent=4,endl=";\n\n")
        # Advanced
        self.writeString("nSmoothScale 4",indent=4,endl=";\n\n")
        self.writeString("errorReduction 0.75",indent=4,endl=";\n\n")
        f.write("}\n\n")

        f.write("debug 0;\n\n")
        f.write("mergeTolerance 1E-6;\n")


class surfaceFeatureExtractDict(foamUtils.genericFoamFile):
    filepath = 'system/surfaceFeatureExtractDict'
    def writeBody(self):
        self.f.write("""
cfdGeom.stl
{
    // How to obtain raw features (extractFromFile || extractFromSurface)
    extractionMethod    extractFromSurface;

    extractFromSurfaceCoeffs
    {
        // Mark edges whose adjacent surface normals are at an angle less
        // than includedAngle as features
        // - 0  : selects no edges
        // - 180: selects all edges
        includedAngle   150;
    }

    // Write options

    // Write features to obj format for postprocessing
    writeObj                yes;
}
""")
        return None
