###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy
from procedural_compute.core.utils import make_tuples
from procedural_compute.cfd.utils.foamUtils import formatObjectName
from procedural_compute.cfd.properties.scene.turbulence import BM_SCENE_CFDSolver_RAS
from procedural_compute.cfd.properties.scene.turbulence import BM_SCENE_CFDSolver_LES


class ODS_CFD_FIELD_VECTOR(bpy.types.PropertyGroup):

    value: bpy.props.FloatVectorProperty(name="value", description="Default Value", default=(0, 0, 0))

    def setValue(self, value):
        self.value = value

    def draw(self, layout):
        layout.row().prop(self, "value")


bpy.utils.register_class(ODS_CFD_FIELD_VECTOR)


class ODS_CFD_FIELD_SCALAR(bpy.types.PropertyGroup):

    value: bpy.props.FloatProperty(name="value", description="Default Value", default=0)

    def setValue(self, value):
        self.value = value

    def draw(self, layout):
        layout.row().prop(self, "value")


bpy.utils.register_class(ODS_CFD_FIELD_SCALAR)


class ODS_CFD_FIELDS(bpy.types.PropertyGroup):
    volScalarField: bpy.props.PointerProperty(type=ODS_CFD_FIELD_SCALAR)
    volVectorField: bpy.props.PointerProperty(type=ODS_CFD_FIELD_VECTOR)
    items_list = make_tuples(["volVectorField", "volScalarField"])
    classType: bpy.props.EnumProperty(name="classType", items=items_list, description="classType", default="volScalarField")
    dim: bpy.props.StringProperty(name="dim", default="[0,1,-1,0,0,0,0]")

    def setValue(self, value):
        c = getattr(self, self.classType)
        return c.setValue(value)

    def draw(self, layout):
        row = layout.row()
        row.prop(self, "name")
        row.prop(self, "classType")
        c = getattr(self, self.classType)
        c.draw(layout)
        return None


bpy.utils.register_class(ODS_CFD_FIELDS)


class BM_SCENE_CFDSolver(bpy.types.PropertyGroup):

    RAS: bpy.props.PointerProperty(type=BM_SCENE_CFDSolver_RAS)
    LES: bpy.props.PointerProperty(type=BM_SCENE_CFDSolver_LES)

    items_list = make_tuples([
        "potentialFoam",
        "simpleFoam",
        "pisoFoam",
        "buoyantSimpleFoam",
        "buoyantPimpleFoam",
        "buoyantBoussinesqSimpleFoam",
        "buoyantBoussinesqPimpleFoam"
    ])
    name: bpy.props.EnumProperty(name="solver", items=items_list, description="Solver Name", default="simpleFoam")

    items_list = make_tuples(["Laminar", "RAS"])
    turbModel: bpy.props.EnumProperty(name="turbModel", items=items_list, description="Turbulence Model", default="RAS")

    nu: bpy.props.FloatProperty(name="nu", step=1, precision=5, description="Kinematic Viscosity (nu)", default=1.5e-5)

    fields: bpy.props.CollectionProperty(type=ODS_CFD_FIELDS, name="fields", description="Fields")
    active_fields_index: bpy.props.IntProperty()

    # Define the overrides here (as pointers to Blender text blocks)
    override_setup: bpy.props.PointerProperty(type=bpy.types.Text, name="Setup overrides", description="Reference to a a text that contains setup override")
    override_fields: bpy.props.PointerProperty(type=bpy.types.Text, name="Fields overrides", description="Reference to a a text that contains fields override")
    override_presets: bpy.props.PointerProperty(type=bpy.types.Text, name="Presets overrides", description="Reference to a text that contains preset overrides")
    override_case_files: bpy.props.PointerProperty(type=bpy.types.Text, name="Case file overrides", description="Reference to a text that contains case file overrides")

    def drawMenu(self, layout):
        sc = bpy.context.scene

        # Draw Solver name and tubulence model selections
        L = layout.box()
        L.row().prop(self, "name", expand=False)
        if not self.name == "potentialFoam":
            L.row().prop(self, "turbModel")
            if self.turbModel == "Laminar":
                return
            m = getattr(self, self.turbModel)
            m.drawMenu(L)

        L = layout.box()
        L.label(text="Overrides:")
        L.row().prop(self, "override_setup")
        L.row().prop(self, "override_fields")
        L.row().prop(self, "override_presets")
        L.row().prop(self, "override_case_files")

        # Draw Internal fields and defaults
        #L = layout.box()
        #L.label(text="Fields and Defaults")
        #drawCollectionTemplateList(L, self, "fields")
        #if len(self.fields) > 0 and self.active_fields_index >= 0:
        #    self.fields[self.active_fields_index].draw(L)

    def to_json(self):
        objects = bpy.context.visible_objects

        skip_names = ['cfdBoundingBox','cfdMeshKeepPoint']
        bcs = {
            formatObjectName(obj.name): obj.ODS_CFD.to_json()
            for obj in objects if not obj.name in skip_names
        }

        json_dict = {
            'solver': self.name,
            'boundary_conditions': bcs,
            'overrides': {
                'setup': [self.override_setup.as_string()] if self.override_setup else [],
                'presets': [self.override_presets.as_string()] if self.override_presets else [],
                'fields': [self.override_fields.as_string()] if self.override_fields else [],
                'caseFiles': [self.override_case_files.as_string()] if self.override_case_files else []
            }
        }

        return json_dict

bpy.utils.register_class(BM_SCENE_CFDSolver)
