###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

from procedural_compute.cfd.utils import foamCaseFiles, asciiSTLExport, mesh, foamUtils

import bpy


class BM_SCENE_CFDMesh(bpy.types.PropertyGroup):
    basic: bpy.props.BoolProperty(name="basicMesh", description="Basic Mesh", default=True)
    castellated: bpy.props.BoolProperty(name="Castellated Mesh", description="Castellated Mesh", default=True)
    snap: bpy.props.BoolProperty(name="Snap Mesh", description="Snap Mesh", default=True)
    addLayers: bpy.props.BoolProperty(name="Boundary Layer Mesh", description="Add Boundary Layer Mesh", default=False)

    hideCastellatedMenu: bpy.props.BoolProperty(name="Hide", description="Hide", default=True)
    hideSnapMenu: bpy.props.BoolProperty(name="Hide", description="Snap Mesh", default=True)
    hideAddLayersMenu: bpy.props.BoolProperty(name="Hide", description="Hide", default=True)

    # Castellated Mesh parameters
    blockMeshSize: bpy.props.FloatProperty(name="BlockMeshSize", step=1, precision=2, default=1.0, description="Approx. BlockMesh Cell Size")
    defaultLevel: bpy.props.IntProperty(name="defaultLevel", min=0, description="Default Surface Mesh Level")
    maxLocalCells: bpy.props.IntProperty(name="maxLocalCells", default=16000000, description="Maximum Cells on a Single Processor")
    maxGlobalCells: bpy.props.IntProperty(name="maxGlobalCells", default=16000000, description="Maximum Total Number of Cells")
    minRefinementCells: bpy.props.IntProperty(name="minRefinementCells", default=10, description="Minimum number of cells for subdivision")
    nCellsBetweenLevels: bpy.props.IntProperty(name="nCellsBetweenLevels", default=2, description="Cells between levels")
    resolveFeatureAngle: bpy.props.FloatProperty(name="resolveFeatureAngle", description="Angle to resolve features", step=1, precision=1, default=0.52, subtype="ANGLE")

    # Snappy Hex Mesh parameters
    nSmoothPatch: bpy.props.IntProperty(name="nSmoothPatch", default=3, description="Number of Patch Smoothing Iterations")
    nSolveIter: bpy.props.IntProperty(name="nSolveIter", default=30, description="Number of Solver Iterations")
    nRelaxIter: bpy.props.IntProperty(name="nRelaxIter", default=5, description="Number of Relaxation Iterations")
    tolerance: bpy.props.FloatProperty(name="tolerance", description="Snap Tolerance", default=1.0)

    # Feature edge snapping properties
    nFeatureSnapIter: bpy.props.IntProperty(name="nFeatureSnapIter", default=0, description="Feature Edge Snapping Iterations (0=disable feature edge snapping)")
    implicitFeatureSnap: bpy.props.BoolProperty(name="implicitFeatureSnap", default=False, description="Detect (geometric) features by sampling the surface")
    explicitFeatureSnap: bpy.props.BoolProperty(name="explicitFeatureSnap", default=True, description="Use castellatedMeshControls::features")
    multiRegionFeatureSnap: bpy.props.BoolProperty(name="multiRegionFeatureSnap", default=True, description="Detect features between multiple surfaces (only for explicitFeatureSnap, default = false)")

    # Add Layers parameters
    relativeSizes: bpy.props.BoolProperty(name="relativeSizes", description="Layer parameters based on cell size outside layer", default=True)
    expansionRatio: bpy.props.FloatProperty(name="expansionRatio", description="Expansion Factor", default=1.0)
    finalLayerThickness: bpy.props.FloatProperty(name="finalLayerThickness", description="Wanted thickness of final added cell layer", default=0.3)
    minThickness: bpy.props.FloatProperty(name="minThickness", description="Minimum thickness of cell layer", default=0.1)
    nGrow: bpy.props.IntProperty(name="nGrow", default=1, description="If points get not extruded do nGrow layers of connected faces")
    featureAngle: bpy.props.FloatProperty(name="featureAngle", description="When not to extrude surface", step=1, precision=1, default=0.52, subtype="ANGLE")
    nRelaxIterLayer: bpy.props.IntProperty(name="nRelaxIterLayer", default=3, description="Number of Relaxation Iterations")
    nSmoothSurfaceNormals: bpy.props.IntProperty(name="nSmoothSurfaceNormals", default=1, description="Number of smoothing iterations of surface normals")
    nSmoothNormals: bpy.props.IntProperty(name="nSmoothNormals", default=3, description="Number of smoothing iterations of interior mesh movement direction")
    nSmoothThickness: bpy.props.IntProperty(name="nSmoothThickness", default=10, description="Smooth layer thickness over surface patches")
    maxFaceThicknessRatio: bpy.props.FloatProperty(name="maxFaceThicknessRatio", description="Stop layer growth on highly warped cells", default=0.5)
    maxThicknessToMedialRatio: bpy.props.FloatProperty(name="maxThicknessToMedialRatio", description="Reduce layer growth where ratio thickness to medial distance is large", default=0.3)
    minMedianAxisAngle: bpy.props.FloatProperty(name="minMedianAxisAngle", description="Angle used to pick up medial axis points", step=1, precision=1, default=2.26, subtype="ANGLE")
    nBufferCellsNoExtrude: bpy.props.IntProperty(name="nBufferCellsNoExtrude", default=0, description="Create buffer region for new layer terminations")
    nLayerIter: bpy.props.IntProperty(name="nLayerIter", default=50, description="Overall max number of layer addition iterations")

    def drawMenu(self, layout):
        sc = bpy.context.scene
        layout.box().row().prop(sc.ODS_CFD.system, "caseDir")

        split = layout.split()
        col = split.column()
        col.prop(self, "blockMeshSize")
        col = split.column()
        col.operator("scene.cfdoperators", text="snapBB").command = "snapCFDBoundingBox"

        # Castellated mesh settings
        box_layout = layout.box()
        box_layout.row().prop(self, "castellated")
        if self.castellated:
            row = box_layout.row()
            row.prop(self, "maxLocalCells")
            row.prop(self, "maxGlobalCells")

            row = box_layout.row()
            row.prop(self, "nCellsBetweenLevels")
            row.prop(self, "minRefinementCells")

        # Castellated mesh settings
        box_layout = layout.box()
        box_layout.row().prop(self, "snap")
        if self.snap:
            box_layout.row().prop(self, "tolerance")

        # Castellated mesh settings
        box_layout = layout.box()
        box_layout.row().prop(self, "addLayers")

        # Operators
        layout.row().operator("scene.compute_cfdoperators", text="Upload Geometry").command = "upload_geometry"
        layout.row().operator("scene.compute_cfdoperators", text="Write Mesh Files").command = "write_mesh_files"
        layout.row().operator("scene.compute_cfdoperators", text="Write Solver Files").command = "write_solver_files"

        layout.row().operator("scene.compute_cfdoperators", text="Run Mesh Pipeline").command = "run_mesh_pipeline"

        box_layout = layout.box()
        box_layout.row().label(text="Clean/delete methods (use with caution):")
        box_layout.row().operator("scene.compute_cfdoperators", text="Clean Processor Dirs").command = "clean_processor_dirs"
        box_layout.row().operator("scene.compute_cfdoperators", text="Clean Mesh Files").command = "clean_mesh_files"


        '''
        if self.basic:
            row = layout.row()
            row.operator("scene.compute_cfdoperators", text="Run Mesh Pipeline").command = "run_mesh_pipeline"
            row.prop(self, "basic", text="Basic Mesh")
        else:
            row = layout.row()
            row.label(text="")
            row.prop(self, "basic", text="Basic Mesh")
            split = layout.split()
            col = split.column()
            col.operator("scene.cfdoperators", text="blockMesh").command = "runFoamBlockMesh"
            col.operator("scene.cfdoperators", text="snappyHexMesh").command = "runFoamSnapMesh"
            #col.operator("scene.cfdoperators", text="postMeshUtils").command = "runPostMeshUtils"
            if sc.ODS_CFD.system.runMPI:
                col = split.column()
                col.operator("scene.cfdoperators", text="decomposePar").command = "decomposePar"
                col.operator("scene.cfdoperators", text="reconstructParMesh").command = "reconstructParMesh"
                #col.operator("scene.cfdoperators", text="reconstructPar").command = "reconstructPar"
        '''

        '''
        row = layout.row()
        row.prop(self, "castellated")
        row.prop(self, "hideCastellatedMenu")
        if self.castellated and not self.hideCastellatedMenu:
            layout.row().prop(self, "maxLocalCells")
            layout.row().prop(self, "maxGlobalCells")
            layout.row().prop(self, "minRefinementCells")
            layout.row().prop(self, "nCellsBetweenLevels")
            layout.row().prop(self, "resolveFeatureAngle")

        row = layout.row()
        row.prop(self, "snap")
        row.prop(self, "hideSnapMenu")
        if self.snap and not self.hideSnapMenu:
            layout.row().prop(self, "nSmoothPatch")
            layout.row().prop(self, "tolerance")
            layout.row().prop(self, "nSolveIter")
            layout.row().prop(self, "nRelaxIter")
            # Feature Edge Snap properties
            layout.row().prop(self, "nFeatureSnapIter")
            if self.nFeatureSnapIter > 0:
                row = layout.row()
                row.prop(self, "implicitFeatureSnap")
                row.prop(self, "explicitFeatureSnap")
                row.prop(self, "multiRegionFeatureSnap")

        row = layout.row()
        row.prop(self, "addLayers")
        row.prop(self, "hideAddLayersMenu")
        if self.addLayers and not self.hideAddLayersMenu:
            layout.row().prop(self, "relativeSizes")
            layout.row().prop(self, "expansionRatio")
            layout.row().prop(self, "finalLayerThickness")
            layout.row().prop(self, "minThickness")
            layout.row().prop(self, "nGrow")
            layout.row().prop(self, "featureAngle")
            layout.row().prop(self, "nRelaxIterLayer")
            layout.row().prop(self, "nSmoothSurfaceNormals")
            layout.row().prop(self, "nSmoothNormals")
            layout.row().prop(self, "nSmoothThickness")
            layout.row().prop(self, "maxFaceThicknessRatio")
            layout.row().prop(self, "maxThicknessToMedialRatio")
            layout.row().prop(self, "minMedianAxisAngle")
            layout.row().prop(self, "nBufferCellsNoExtrude")
            layout.row().prop(self, "nLayerIter")
        '''

    def get_unique_object(self, object_name):
        objects = bpy.context.visible_objects
        candidates = [o for o in objects if o.name.split('.')[0] == object_name]
        if len(candidates) > 1:
            print(f"WARNING: Multiple ({len(bounding_boxes)}) bounding boxes found in scene visible objects.  Selecting first")
        elif len(candidates) == 0:
            raise ValueError(f"ERROR: No object with name matching {object_name}\..* in visible objects")
        return candidates[0]

    def get_bounds(self):
        bounding_box = self.get_unique_object('cfdBoundingBox')

        # Get the min/max corners of the bounding box
        local_vertices = [v.co for v in bounding_box.data.vertices]
        local_bounds = [local_vertices[0], local_vertices[0]]
        for v in local_vertices:
            if sum(v) < sum(local_bounds[0]):
                local_bounds[0] = v
            elif sum(v) > sum(local_bounds[1]):
                local_bounds[1] = v

        # Transform and return the bounds
        return [bounding_box.matrix_world @ v for v in local_bounds]

    def get_set_set(self, obj, keep_point=[0,0,0], locations=[True, True, False]):
        return {
            'name': foamUtils.formatObjectName(obj.name),
            'locations': locations,
            'keep_point': keep_point
        }

    def get_set_sets(self):
        keep_point = self.get_unique_object('cfdMeshKeepPoint')
        keep_point_co = [co for co in keep_point.location]
        set_set_objs = [o for o in bpy.context.visible_objects if o.ODS_CFD.mesh.makeCellSet]
        return [self.get_set_set(obj, keep_point=keep_point_co) for obj in set_set_objs]

    def domain_json(self):
        global_bounds = self.get_bounds()

        # Return the blockMesh dictionary
        json_dict = {
            'type': 'simpleBox',
            'cell_size': self.blockMeshSize,
            'bounding_box': {
                'min': list(global_bounds[0]),
                'max': list(global_bounds[1])
            },
            'parameters': {
                'square': True,
                'z0': True
            },
            "set_set_regions": self.get_set_sets()
        }

        return json_dict

    def exclude_object(self, obj):
        special_names = ['cfdBoundingBox','cfdMeshKeepPoint', 'MinX', 'MaxX', 'MinY', 'MaxY', 'MinZ', 'MaxZ']
        return (obj.ODS_CFD.mesh.makeRefinementRegion or obj.ODS_CFD.mesh.makeCellSet) or (obj.name.split('.')[0] in special_names)

    def snappy_json(self):
        objects = [o for o in bpy.context.visible_objects if not self.exclude_object(o)]

        # Make a dictionary for default surface properties
        default_surface_dict = {
            'level': {
                'min': self.defaultLevel,
                'max': self.defaultLevel
            }
        }

        # Make a dictionary of the surfaces
        surface_dict = {
            foamUtils.formatObjectName(o.name): {
                'level': {
                    'min': o.ODS_CFD.mesh.meshMinLevel,
                    'max': o.ODS_CFD.mesh.meshMaxLevel
                }
            } for o in objects
        }

        # Make a dictionary of the refinement regions
        refinements = [
            {
                'name': foamUtils.formatObjectName(o.name),
                'details': {
                    'mode': o.ODS_CFD.mesh.refinementMode,
                    'levels': o.ODS_CFD.mesh.distanceLevels
                }
            } for o in bpy.context.visible_objects if o.ODS_CFD.mesh.makeRefinementRegion
        ]

        # Overrides
        keep_point = self.get_unique_object('cfdMeshKeepPoint')
        overrides_dict = {
            'castellatedMesh': self.castellated,
            'snap': self.snap,
            'addLayers': self.addLayers,
            'castellatedMeshControls': {
                'locationInMesh': [co for co in keep_point.location],
                'maxLocalCells': self.maxLocalCells,
                'maxGlobalCells': self.maxGlobalCells,
                'minRefinementCells': self.minRefinementCells,
                'nCellsBetweenLevels': self.nCellsBetweenLevels
            },
            'snapControls': {
                'tolerance': self.tolerance
            }
        }

        # json dictionary
        json_dict = {
            'overrides': overrides_dict,
            'default_surface': default_surface_dict,
            'surfaces': surface_dict,
            'refinementRegions': refinements
        }

        return json_dict

bpy.utils.register_class(BM_SCENE_CFDMesh)
