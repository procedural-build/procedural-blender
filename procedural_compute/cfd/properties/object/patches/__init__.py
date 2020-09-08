###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy
from procedural_compute.core.utils.selectUtils import makeTuples
from procedural_compute.cfd.properties.object.patches.scalar import ODS_CFD_PATCH_SCALAR
from procedural_compute.cfd.properties.object.patches.vector import ODS_CFD_PATCH_VECTOR


class BM_OBJ_CFD_PATCHFIELD(bpy.types.PropertyGroup):

    volScalarField: bpy.props.PointerProperty(type=ODS_CFD_PATCH_SCALAR)
    volVectorField: bpy.props.PointerProperty(type=ODS_CFD_PATCH_VECTOR)

    items_list = makeTuples(["volVectorField", "volScalarField"])
    classType: bpy.props.EnumProperty(name="classType", items=items_list, description="classType", default="volScalarField")

    def setValue(self, value, var='value'):
        return getattr(self, self.classType).setValue(value, var=var)

    def setPatchType(self, patchType):
        setattr(getattr(self, self.classType), 'patchType', patchType)
        return None

    def getText(self):
        return getattr(self, self.classType).getText()

    def draw(self, layout, header=True):
        if header:
            row = layout.row()
            #row.label(text="%s (%s)"%(self.name, self.classType))
            row.prop(self, "name", text="")
            row.label(text=self.classType)
        c = getattr(self, self.classType)
        c.draw(layout, header=header)
        return None


bpy.utils.register_class(BM_OBJ_CFD_PATCHFIELD)
