###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils.selectUtils import makeTuples
from procedural_compute.core.utils.compute.auth import USER


class BM_SCENE_CFDPostProc(bpy.types.PropertyGroup):

    # Server login and token properties
    task_case_dir: bpy.props.StringProperty(name="Task case_dir", default='foam', description="Task case_dir (on server)")
    auto_load_probes: bpy.props.BoolProperty(default=True)


    def drawMenu(self, layout):
        is_not_windows = 'Windows' not in bpy.app.build_platform.decode()
        sc = bpy.context.scene

        # Probe points - probe points and wait for result
        box = layout.box()
        box.row().prop(self, "task_case_dir")
        row = box.row()
        row.operator("scene.compute_cfdoperators", text="Probe Selected", ).command = "probe_selected"
        row.prop(self, "auto_load_probes", text="Auto Load")
        # Manually load the probe results
        row.operator("scene.compute_cfdoperators", text="Load Probes", ).command = "load_selected_probes"

        # Only use this if you want to pull down the case
        box = layout.box()
        box.row().prop(sc.ODS_CFD.system, "caseDir")
        box.row().operator("scene.compute_cfdoperators", text="Pull folder", ).command = "pull_to_local"

        # Open Paraview
        box = layout.box()
        row = box.row()
        row.operator("scene.cfdoperators", text="Open ParaView", ).command = "paraView"
        row.enabled = is_not_windows


bpy.utils.register_class(BM_SCENE_CFDPostProc)
