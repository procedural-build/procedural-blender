###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples


class SCENE_PROPS_COMPUTE_CFDSystem(bpy.types.PropertyGroup):

    # Legacy system settings from ODS Studio
    runMPI: bpy.props.BoolProperty(name="runMPI", description="Do MPIRun", default=False)
    items_list = make_tuples(["simple", "hierarchical"])
    decompMethod: bpy.props.EnumProperty(name="decompMethod", items=items_list, description="Decomposition Method", default="hierarchical")
    numSubdomains: bpy.props.IntProperty(name="SubDomains", min=1, description="Number of SubDomains for Parallel Processing")
    decompN: bpy.props.IntVectorProperty(name="Nxyz", description="Splits in XYZ", default=(1, 1, 1), min=1)
    decompDelta: bpy.props.FloatProperty(name="Delta", step=1, precision=3, default=0.001, description="delta value for MPI decomposition")
    decompOrder: bpy.props.StringProperty(name="Order", default='xyz', description="Order of decomposition")

    caseDir: bpy.props.StringProperty(name="caseDir", default="//foam", maxlen=128, description="Case Directory", subtype='FILE_PATH')
    machines: bpy.props.StringProperty(name="Machines", default="localhost", description="Machines for MPIrun (comma separated)")
    if 'Windows' in bpy.app.build_platform.decode():
        homedir: bpy.props.StringProperty(name="OFHomeDir", default="C:/OpenFOAM", maxlen=128, description="OpenFOAM Home Directory")
        mpiOptions: bpy.props.StringProperty(name="mpiOptions", default="-genvlist Path,WM_PROJECT_DIR,MPI_BUFFER_SIZE", description="Added options for mpi")
    else:
        homedir: bpy.props.StringProperty(name="OFHomeDir", default="/opt/openfoam211", maxlen=128, description="OpenFOAM Home Directory")
        mpiOptions: bpy.props.StringProperty(name="mpiOptions", default="", description="Added options for mpi")

    def drawMenu(self, layout):
        return None

bpy.utils.register_class(SCENE_PROPS_COMPUTE_CFDSystem)
