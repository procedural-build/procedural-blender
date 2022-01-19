###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
import os
import shutil
import glob

import procedural_compute.cfd.utils.foamCaseFiles as foamCaseFiles
import procedural_compute.cfd.utils.asciiSTLExport as asciiSTLExport
import procedural_compute.cfd.utils.mesh as mesh

import procedural_compute.cfd.solvers

from procedural_compute.core.utils import subprocesses, fileUtils
from procedural_compute.core.utils import threads
from procedural_compute.core.utils.subprocesses import waitSTDOUT


class SCENE_OT_cfdOperators(bpy.types.Operator):
    bl_label = "CFD Operations"
    bl_idname = "scene.cfdoperators"
    bl_description = "Generic CFD Operations"

    command: bpy.props.StringProperty(name="Command", description="parse String", default="")

    def execute(self, context):
        if hasattr(self, self.command):
            c = getattr(self, self.command)
            c()
        else:
            print(self.command + ": Attribute not found!")
        return{'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

    def writeCaseFiles(self):
        self.writeSystemFiles()
        self.writeMeshFiles()

    def writeMeshFiles(self):
        self.writeMeshDicts()
        self.writeMeshSurfs()
        self.writeSolverFiles()
        self.writeControlDict()
        return{'FINISHED'}

    def writeMeshDicts(self):
        print("Writing blockMesh and snappyHexMesh dictionaries...")
        objNames = [o.name for o in bpy.context.selected_objects]
        writeDicts = True
        for name in ['cfdBoundingBox', 'cfdMeshKeepPoint']:
            if name not in objNames:
                self.report({'WARNING'}, '%s not found in selected objects.  Skipping writing of mesh dictionaries.  Case will not mesh.'%name)
                writeDicts = False
        if writeDicts:
            mesh.blockMeshDict().write()
            mesh.surfaceFeatureExtractDict().write()
            mesh.snappyHexMeshDict().write()
        print("Done")
        return{'FINISHED'}

    def writeMeshSurfs(self):
        sc = bpy.context.scene
        obs = bpy.context.selected_objects
        for o in obs:
            if o.Compute.CFD.mesh.makeRefinementRegion:
                o.select_set(False)

        if 'porous' not in sc.Compute.CFD.solver.name:
            asciiSTLExport.writeTriSurface()
        else:
            asciiSTLExport.writeTriSurface(writePorous=False)
            for o in obs:
                o.select_set(False)
            for o in obs:
                if o.Compute.CFD.porous_isPorous:
                    o.select_set(True)
                    fname = procedural_compute.cfd.utils.foamUtils.formatObjectName(o.name) + '.stl'
                    asciiSTLExport.writeTriSurface(filename="constant/triSurface/%s"%(fname), writeNonPorous=False)
                    o.select_set(False)
            for o in obs:
                o.select_set(True)

        # Finally write the refinement regions
        for o in obs:
            o.select_set(False)
        for o in obs:
            if o.Compute.CFD.mesh.makeRefinementRegion:
                o.select_set(True)
                fname = procedural_compute.cfd.utils.foamUtils.formatObjectName(o.name) + '.stl'
                asciiSTLExport.writeTriSurface(filename="constant/triSurface/%s"%(fname), writePorous=True, writeNonPorous=True)
                o.select_set(False)
        for o in obs:
            o.select_set(True)
        return{'FINISHED'}

    def snapCFDBoundingBox(self):
        sc = bpy.context.scene
        bb = bpy.data.objects['cfdBoundingBox']
        ds = sc.Compute.CFD.mesh.blockMeshSize
        for i in range(3):
            bb.scale[i] = round((bb.scale[i] / ds)) * ds
        return{'FINISHED'}

    def clearCase(self):
        p = self.caseDir()
        if os.path.exists(p):
            print("Deleting case directory: %s"%p)
            shutil.rmtree(p)
        return{'FINISHED'}

    @staticmethod
    def delProcessDirs(caseDir):
        dirs = glob.glob("%s/processor*"%caseDir)
        for d in dirs:
            print("Deleting processor directory: %s"%d)
            shutil.rmtree(d)
        return None

    def clearProcessDirs(self):
        dirs = glob.glob("%s/processor*"%self.caseDir())
        for d in dirs:
            print("Deleting processor directory: %s"%d)
            shutil.rmtree(d)
        return{'FINISHED'}

    def writeSystemFiles(self):
        print("Writing OpenFOAM system files (machines, decomposeParDict)")
        foamCaseFiles.dotFoam().write()
        foamCaseFiles.machines().write()
        foamCaseFiles.decomposeParDict().write()
        print("Done")
        return{'FINISHED'}

    def writeControlDict(self):
        print("Writing controlDict")
        #foamCaseFiles.controlDict().write()
        sc = bpy.context.scene
        solver = sc.Compute.CFD.solver.name
        if hasattr(procedural_compute.cfd.solvers, solver):
            s = getattr(procedural_compute.cfd.solvers, solver)
            s().caseFiles().controlDict().write()
        print("Done")
        return{'FINISHED'}

    def writeSolverFiles(self):
        sc = bpy.context.scene
        solver = sc.Compute.CFD.solver.name

        if hasattr(procedural_compute.cfd.solvers, solver):
            s = getattr(procedural_compute.cfd.solvers, solver)
            if not s.writeCase(s):
                self.report({'ERROR'}, "This solver should not have an LES Model.  This case will error if you try and run. Use a transient solver.")
                return{'FINISHED'}
        else:
            self.report({'ERROR'}, "Solver %s not found"%solver)
        return{'FINISHED'}

    def sourceFoam(self):
        sc = bpy.context.scene
        ofDir = sc.Compute.CFD.homedir

        # Check if the OpenFOAM directory exists
        if not os.path.exists(ofDir):
            self.report({'WARNING'}, "No OpenFOAM directory found.  Please ensure that you have OpenFOAM installed in %s"%(ofDir))
            return{'FINISHED'}
        else:
            print("Found OpenFOAM install directory in %s.  Starting OpenFOAM for CFD."%(ofDir))

        # Source foam on all CFD sub-processes
        for pp in subprocesses.p:
            if 'cfd' in pp:
                if 'Windows' in bpy.app.build_platform.decode():
                    cmd = "%s/DOS_Mode.bat"%(ofDir)
                else:
                    cmd = "source %s/etc/bashrc"%(ofDir)
                waitSTDOUT(pp, cmd)
        return{'FINISHED'}

    def getMpiCall(self):
        CFD = bpy.context.scene.Compute.CFD
        if not CFD.system.runMPI:
            return ""
        bpy.ops.scene.getnumsubdomains()
        n = CFD.system.numSubdomains
        if 'Windows' in bpy.app.build_platform.decode():
            text = "mpiexec -np %i -machinefile system/machines"%(n)
        else:
            text = "mpirun -np %i --hostfile system/machines"%(n)
        text = "%s %s "%(text, CFD.system.mpiOptions)
        return text

    def parStr(self):
        return "-parallel" if self.getMpiCall() else ""

    def caseDir(self):
        return bpy.path.abspath(bpy.context.scene.Compute.CFD.system.caseDir)

    def basicMesh(self):
        mpi = bpy.context.scene.Compute.CFD.system.runMPI
        self.runFoamBlockMesh()
        if bpy.context.scene.Compute.CFD.mesh.nFeatureSnapIter > 0:
            self.runFoamSurfaceFeatureExtract()
        if mpi:
            self.decomposePar()
        self.runFoamSnapMesh()
        if mpi:
            self.reconstructParMesh()
            threads.queue_fun("cfdRun", self.delProcessDirs, (self.caseDir(),))
        return None

    def basicRun(self):
        mpi = bpy.context.scene.Compute.CFD.system.runMPI
        if mpi:
            self.decomposePar()
        self.runFoamCase()
        if mpi:
            self.reconstructPar()
        return None

    def runFoamBlockMesh(self):
        cmd = "blockMesh | tee logBM.txt"
        threads.queue_fun("cfdRun", waitSTDOUT, (cmd, self.caseDir()))
        return None

    def runFoamSurfaceFeatureExtract(self):
        cmd = "surfaceFeatureExtract | tee logSFE.txt"
        threads.queue_fun("cfdRun", waitSTDOUT, (cmd, self.caseDir()))
        return None

    def runFoamSnapMesh(self):
        cmd = "%s snappyHexMesh -overwrite %s | tee logSHM.txt"%(self.getMpiCall(), self.parStr())
        threads.queue_fun("cfdRun", waitSTDOUT, (cmd, self.caseDir()))
        return None

    def runPostMeshUtils(self):
        def run(cmd):
            setSets = fileUtils.getFilesByExtension('.setSet', '%s/'%self.caseDir())
            for s in setSets:
                waitSTDOUT("%s setSet %s -batch %s | tee logPMesh.txt"%(self.getMpiCall(), self.parStr(), s), cwd=self.caseDir())
            waitSTDOUT("%s setsToZones %s %s | tee logPMesh.txt"%(self.getMpiCall(), self.parStr(), s), cwd=self.caseDir())
            waitSTDOUT("%s changeDictionary %s %s | tee logPMesh.txt"%(self.getMpiCall(), self.parStr(), s), cwd=self.caseDir())
        threads.queue_fun("cfdRun", run, ())
        return None

    def decomposePar(self):
        cmd = "decomposePar | tee -a logPar.txt"  # latestTime by default in OF-2.0
        threads.queue_fun("cfdRun", waitSTDOUT, (cmd, self.caseDir()))
        return{'FINISHED'}

    def reconstructPar(self):
        cmd = "reconstructPar -latestTime | tee -a logPar.txt"
        threads.queue_fun("cfdRun", waitSTDOUT, (cmd, self.caseDir()))
        return None

    def reconstructParMesh(self):
        cmd = "reconstructParMesh -constant -mergeTol 1e-6 | tee -a logPar.txt"
        threads.queue_fun("cfdRun", waitSTDOUT, (cmd, self.caseDir()))
        return None

    def paraView(self):
        cmd = "paraFoam | tee -a logPP.txt"
        threads.queue_fun("cfdPost", waitSTDOUT, (cmd, self.caseDir()))
        return None

    def runFoamCase(self):
        CFD = bpy.context.scene.Compute.CFD
        cmd = "%s %s %s | tee -a log.txt"%(self.getMpiCall(), CFD.solver.name, self.parStr())
        threads.queue_fun("cfdRun", waitSTDOUT, (cmd, self.caseDir()))
        return None

    def copyMeshLevels(self):
        obs = bpy.context.selected_objects
        sob = bpy.context.object
        for o in obs:
            if o.name == sob.name:
                continue
            o.Compute.CFD.mesh.meshMinLevel = sob.Compute.CFD.mesh.meshMinLevel
            o.Compute.CFD.mesh.meshMaxLevel = sob.Compute.CFD.mesh.meshMaxLevel
            o.Compute.CFD.mesh.nSurfaceLayers = sob.Compute.CFD.mesh.nSurfaceLayers
            o.Compute.CFD.mesh.makeRefinementRegion = sob.Compute.CFD.mesh.makeRefinementRegion
            o.Compute.CFD.mesh.refinementMode = sob.Compute.CFD.mesh.refinementMode
            o.Compute.CFD.mesh.distanceLevels = sob.Compute.CFD.mesh.distanceLevels

        return None

    def copy_bcs(self):
        obs = bpy.context.selected_objects
        sob = bpy.context.object
        for o in obs:
            o.Compute.CFD.bc_preset = sob.Compute.CFD.bc_preset
            o.Compute.CFD.bc_overrides = sob.Compute.CFD.bc_overrides
            o.Compute.CFD.bc_override_text = sob.Compute.CFD.bc_override_text
        return None

bpy.utils.register_class(SCENE_OT_cfdOperators)
