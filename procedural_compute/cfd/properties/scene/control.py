###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils.selectUtils import makeTuples


class BM_SCENE_CFDControl(bpy.types.PropertyGroup):

    items_list = makeTuples(["firstTime", "latestTime", "startTime"])
    startFrom: bpy.props.EnumProperty(name="startFrom", items=items_list, description="startFrom", default="latestTime")

    items_list = makeTuples(["endTime", "nextWrite", "writeNow", "noWriteNow"])
    stopAt: bpy.props.EnumProperty(name="stopAt", items=items_list, description="stopAt", default="endTime")

    items_list = makeTuples(["timeStep", "runTime", "adjustableRunTime", "cpuTime", "clockTime"])
    writeControl: bpy.props.EnumProperty(name="writeControl", items=items_list, description="writeControl", default="timeStep")

    items_list = makeTuples(["ascii", "binary"])
    writeFormat: bpy.props.EnumProperty(name="writeFormat", items=items_list, description="writeFormat", default="ascii")

    items_list = makeTuples(["compressed", "uncompressed"])
    writeCompression: bpy.props.EnumProperty(name="writeCompression", items=items_list, description="writeCompression", default="uncompressed")

    items_list = makeTuples(["general", "scientific", "fixed"])
    timeFormat: bpy.props.EnumProperty(name="timeFormat", items=items_list, description="timeFormat", default="general")

    adjustTimeStep: bpy.props.BoolProperty(name="adjustTimeStep", description="Variable Time Step", default=False)
    maxCo: bpy.props.FloatProperty(name="maxCo", description="maxCo", default=0.5, precision=2)

    basic: bpy.props.BoolProperty(name="basicMesh", description="Basic Run", default=True)
    startTime: bpy.props.FloatProperty(name="startTime", description="startTime", default=0.0)
    endTime: bpy.props.FloatProperty(name="endTime", description="endTime", default=500.0)
    deltaT: bpy.props.FloatProperty(name="deltaT", description="deltaT", default=1, precision=3)
    writeInterval: bpy.props.FloatProperty(name="writeInterval", default=50, description="writeInterval")
    purgeWrite: bpy.props.IntProperty(name="purgeWrite", default=2, description="purgeWrite")
    timePrecision: bpy.props.IntProperty(name="timePrecision", default=6, description="timePrecision")
    runTimeModifiable: bpy.props.BoolProperty(name="runTimeModifiable", description="runTimeModifiable", default=True)
    solveFlow: bpy.props.BoolProperty(name="solveFlow", description="solveFlow", default=False)
    controlLibs: bpy.props.StringProperty(name="RunTimeLibs", default="libFanDirectionalPatchField.so", maxlen=248, description="Runtime Include Libraries (comma separated)")

    writePrecision: bpy.props.IntProperty(name="writePrecision", default=6, description="writePrecision")

    def drawMenu(self, layout):
        sc = bpy.context.scene
        split = layout.split()

        layout.row().operator("scene.compute_cfdoperators", text="Run Solver").command = "run_solver"

        layout.row().operator("scene.compute_cfdoperators", text="Run Wind Tunnel").command = "run_wind_tunnel"

        layout.row().prop(self, "endTime")
        #layout.row().prop(self, "stopAt", expand=False)
        #row = layout.row()
        #row.operator("scene.cfdoperators", text="Write controlDict").command = "write_control_dict"

        '''
        if self.basic:
            row = layout.row()
            row.operator("scene.cfdoperators", text="Run Case").command = "basicRun"
            row.prop(self, "basic", text="Basic Run")
        else:
            layout.row().prop(self, "basic", text="Basic Run")
            row = layout.row()
            row.operator("scene.cfdoperators", text="decomposePar").command = "decomposePar"
            row.operator("scene.cfdoperators", text="Run Case").command = "runFoamCase"
            row.operator("scene.cfdoperators", text="reconstructPar").command = "reconstructPar"

        split = layout.split()
        col = split.column()
        col.prop(self, "startFrom", expand=False)
        col.prop(self, "stopAt", expand=False)
        col = split.column()
        col.prop(self, "startTime")
        col.prop(self, "endTime")

        row = layout.row()
        row.prop(self, "adjustTimeStep")
        if not self.adjustTimeStep:
            row.prop(self, "deltaT")
        else:
            row.prop(self, "maxCo")
            row.prop(self, "deltaT", text='maxDeltaT')

        row = layout.row()
        row.prop(self, "writeControl", expand=False)
        row.prop(self, "writeFormat", expand=False)

        row = layout.row()
        row.prop(self, "writeInterval")
        row.prop(self, "purgeWrite")

        row = layout.row()
        row.prop(self, "writePrecision")
        row.prop(self, "writeCompression", expand=False)

        row = layout.row()
        row.prop(self, "timeFormat", expand=False)
        row.prop(self, "timePrecision")
        layout.row().prop(self, "runTimeModifiable")
        if "ageing" in sc.ODS_CFD.solver.name:
            layout.row().prop(self, "solveFlow")
        '''

    def getText(self):
        sc = bpy.context.scene
        t = ""
        t += "application        %s;\n\n"%(sc.ODS_CFD.solver.name)
        t += "startFrom          %s;\n\n"%(self.startFrom)
        t += "startTime          %f;\n\n"%(self.startTime)
        t += "stopAt             %s;\n\n"%(self.stopAt)
        t += "endTime            %f;\n\n"%(self.endTime)
        t += "deltaT             %f;\n\n"%(self.deltaT)
        if sc.ODS_CFD.control.adjustTimeStep:
            t += "adjustTimeStep     yes;\n\n"
            t += "maxCo              %f;\n\n"%(self.maxCo)
            t += "maxDeltaT          %f;\n\n"%(self.deltaT)
        t += "writeControl       %s;\n\n"%(self.writeControl)
        t += "writeInterval      %f;\n\n"%(self.writeInterval)
        t += "purgeWrite         %i;\n\n"%(self.purgeWrite)
        t += "writeFormat        %s;\n\n"%(self.writeFormat)
        t += "writePrecision     %i;\n\n"%(self.writePrecision)
        t += "writeCompression   %s;\n\n"%(self.writeCompression)
        t += "timeFormat         %s;\n\n"%(self.timeFormat)
        t += "timePrecision      %i;\n\n"%(self.timePrecision)
        t += "runTimeModifiable  %s;\n\n"%(str(self.runTimeModifiable).lower())
        # Added strings for ageingScalarTransportFoam
        #if "ageing" in sc.ODS_CFD.solver.name:
        #    t += "solveFlow %s;"%(str(self.solveFlow).lower())
        # Write the added user-defined libraries
        libs = []
        #if "buoyant" in sc.ODS_CFD.solver.name:
        #    libs.append("\"libcompressibleTurbulenceModel.so\"")
        #if getNumberOfPatchType('outletMappedUniformInlet') > 0 or getNumberOfPatchType('swirl') > 0:
        #    libs.append("\"libFvPatchFieldsODS.so\"")
        t += "libs ( %s );\n"%(" ".join(libs))
        # Append information that is in controlDict.append
        if 'controlDict.append' in bpy.data.texts:
            t += bpy.data.texts['controlDict.append'].as_string()
        return t


bpy.utils.register_class(BM_SCENE_CFDControl)
