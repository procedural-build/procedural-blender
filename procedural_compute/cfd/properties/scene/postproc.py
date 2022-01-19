###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples
from procedural_compute.core.utils.compute.auth import USER


class BM_SCENE_CFDPostProc(bpy.types.PropertyGroup):

    # Server login and token properties
    task_case_dir: bpy.props.StringProperty(name="Task case_dir", default='foam', description="Task case_dir (on server)")
    auto_load_probes: bpy.props.BoolProperty(default=True)
    probe_time_dir: bpy.props.StringProperty(name="Probe time dir", default='0.0', description="The time folder to load probe results")
    probe_fields: bpy.props.StringProperty(name="Probe fields", default='Utrans,p', description="Probe these fields")
    load_probe_field: bpy.props.StringProperty(name="Load probe field", default='Utrans', description="Load these fields from the probes")
    probe_min_range: bpy.props.FloatProperty(name="Probe Min Range", default=0.0, description="Probe Min Range")
    probe_max_range: bpy.props.FloatProperty(name="Probe Max Range", default=5.0, description="Probe Max Range")


    def drawMenu(self, layout):
        is_not_windows = 'Windows' not in bpy.app.build_platform.decode()
        sc = bpy.context.scene

        # Probe points - probe points and wait for result
        box = layout.box()
        row = box.row()
        row.prop(self, "task_case_dir")
        row.prop(self, "probe_time_dir")
        row = box.row()
        row.prop(self, "probe_fields")
        row.prop(self, "load_probe_field")
        row = box.row()
        row.prop(self, "probe_min_range")
        row.prop(self, "probe_max_range")
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
