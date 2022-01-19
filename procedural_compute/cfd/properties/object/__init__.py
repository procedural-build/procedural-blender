###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.core.utils import make_tuples
from procedural_compute.core.utils.blendmeUtils import drawCollectionTemplateList

import procedural_compute.cfd.solvers
from procedural_compute.cfd.properties.object.mesh import BM_OBJ_CFD_MESH
from procedural_compute.cfd.properties.object.patches import BM_OBJ_CFD_PATCHFIELD

import json


def getSolver():
    return getattr(procedural_compute.cfd.solvers, bpy.context.scene.ODS_CFD.solver.name)


def setFields(self, context):
    fields = getSolver().patchFields(self.preset)
    for f in fields:
        self.addField(f, fields[f]['classType'])
        self.setField(f, fields[f]['patchType'], fields[f]['default'])
    return None


class BM_OBJ_CFD(bpy.types.PropertyGroup):

    mesh: bpy.props.PointerProperty(type=BM_OBJ_CFD_MESH)

    bc_preset: bpy.props.StringProperty(name="Preset", default='wall', description="BC Preset")
    bc_override_text: bpy.props.PointerProperty(type=bpy.types.Text, name="BC Override text", description="Text that contains the override definition")
    bc_overrides: bpy.props.StringProperty(name="BC Overrides", default='', description="BC Overrides")

    ##################################

    items_list = make_tuples(["wall", "wallSlip", "fixedPressure", "fixedPressureOutOnly", "fixedVelocity", "custom"])
    preset: bpy.props.EnumProperty(name="preset", items=items_list, description="Preset", default="wall", update=setFields)

    doMesh: bpy.props.BoolProperty(name="doMesh", default=True, description="Include in Meshing")

    fields: bpy.props.CollectionProperty(type=BM_OBJ_CFD_PATCHFIELD, name="fields", description="Fields")
    active_fields_index: bpy.props.IntProperty()

    porous_isPorous: bpy.props.BoolProperty(name="isPorous", default=False, description="Is this object Porous")
    porous_Dcoeff: bpy.props.IntVectorProperty(name="Dcoeff", description="D", default=(0, 0, 0))
    porous_Fcoeff: bpy.props.FloatVectorProperty(name="Fcoeff", description="F", default=(3.5, 3.5, 3.5))
    # Fcoeff is the Forchheimer coeffcients which relate to the v^2 component of the Darcy-Forchheimer law
    # F = 2*K/(rho*dx) where K is the pressure loss coefficient & dx is the distance over which that pressure is lost
    # using values of dx=0.25, rho=1.2 & K=0.5 gives F = 3.33 rounded up to 3.5
    # Dcoeff is the Darcy component that relates to v

    source_isSource: bpy.props.BoolProperty(name="isSource", default=False, description="Is this object a scalar Source")
    items_list = make_tuples(["absolute", "specific"])
    source_volMode: bpy.props.EnumProperty(name="volMode", items=items_list, description="Volume Mode (specific = amount/m3)", default="specific")
    source_expRate: bpy.props.FloatProperty(name="expRate", description="Explicit Rate", default=1.0)
    source_impRate: bpy.props.FloatProperty(name="impRate", description="Implicit Rate", default=0.0)

    def drawMenu(self, layout):
        L = layout.box()
        self.mesh.drawMenu(L)

        L = layout.box()
        L.row().label(text="Boundary Conditions:")
        L.row().prop(self, "bc_preset")
        if not self.bc_overrides.strip():
            L.row().prop(self, "bc_override_text")
        if not self.bc_override_text:
            L.row().prop(self, "bc_overrides")
        L.row().operator("scene.cfdoperators", text="Copy to Selected").command = "copy_bcs"

        '''
        L.row().prop(self, "preset", expand=False)
        sc = bpy.context.scene
        if 'porous' in sc.ODS_CFD.solver.name:
            L.row().prop(self, "porous_isPorous")
            if self.porous_isPorous:
                L.row().prop(self, "porous_Dcoeff", expand=True)
                L.row().prop(self, "porous_Fcoeff", expand=True)
                return None

        if 'scalarSource' in sc.ODS_CFD.solver.name:
            L.row().prop(self, "source_isSource")
            if self.source_isSource:
                split = L.split()
                split.column().prop(self, "source_volMode", expand=False)
                split.column().prop(self, "source_expRate", expand=False)
                split.column().prop(self, "source_impRate", expand=False)
                return None

        if self.preset == 'custom':
            drawCollectionTemplateList(L, self, "fields")
            if self.active_fields_index >= 0:
                self.fields[self.active_fields_index].draw(L)
        else:
            values = getSolver().presets[self.preset]
            fields = getSolver().fields()
            if 'draw' not in values:
                return None
            drawFields = values['draw']
            for f in drawFields:
                if f in self.fields:
                    self.fields[f].draw(L.box(), header=True)
                else:
                    row = L.box().row()
                    row.label(text = "%s = %s"%(f, values[f]))
        '''
        return None

    def addField(self, fieldName, classType):
        if fieldName in self.fields:
            return self.fields[fieldName]
        newField = self.fields.add()
        newField.name = fieldName
        newField.classType = classType
        return newField

    def setField(self, fieldName, patchType, value, var='value'):
        f = self.fields[fieldName]
        f.setPatchType(patchType)
        f.setValue(value, var=var)
        return f

    def delField(self, fieldName):
        return self.fields.remove(self.fields.find(fieldName))

    def getText(self, field):
        if field in self.fields:
            text = self.fields[field].getText()
        else:
            f = getSolver().patchFields('wall')[field]
            self.addField(field, f['classType'])
            self.setField(field, f['patchType'], f['default'])
            text = self.fields[field].getText()
            self.delField(field)
        return text

    def to_json(self):
        """ Boundary condition overrides may be provided in OpenFOAM dictionary
        format OR JSON and may either be defined in-line or as a reference to
        a Blender Text that contains the
        """
        overrides = ""
        if self.bc_override_text:
            overrides = self.bc_override_text.as_string()
        else:
            overrides = self.bc_overrides.strip()
        # To to parse the string as JSON
        try:
            overrides = json.loads(overrides)
        except json.JSONDecodeError:
            pass
        # Return the dictionary
        json_dict = {
            "preset": self.bc_preset,
            "overrides": overrides
        }
        return json_dict

bpy.utils.register_class(BM_OBJ_CFD)
#####################

bpy.types.Object.ODS_CFD = bpy.props.PointerProperty(type=BM_OBJ_CFD)
